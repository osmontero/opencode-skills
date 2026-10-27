#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes the skill to be triggered
(via the `skill` tool) for a set of queries. Outputs results as JSON.

Runs each query through `opencode run --standalone --format json` in a
scratch project whose `.opencode/skills/` contains a single stub skill
with the description under test. Triggering is detected from the JSON
event stream: a `tool_use` event with `part.tool == "skill"` whose
`part.state.input.id` equals the stub's skill name, and whose output
contains the per-run marker.
"""

import argparse
import json
import shutil
import subprocess
import sys
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .opencode/.

    Used as the default scratch location for eval runs so the temporary
    project sits next to (not inside) the repo being evaluated.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".opencode").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    scratch_dir: str,
    model: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a stub skill under the scratch project's `.opencode/skills/`
    using the *real* skill name (so it shadows the same-named globally
    installed skill) with the description under test and a unique marker
    in the body. Then runs the raw query through
    `opencode run --standalone --format json` and detects the trigger from
    the `skill` tool_use event: `part.state.input.id == skill_name` AND the
    event output contains the marker (proves the stub's description was the
    one in the model's available_skills list, not a global copy).
    """
    unique_id = uuid.uuid4().hex[:8]
    marker = f"EVAL-TRIGGER-MARKER-{unique_id}"
    # Each concurrent query gets its own project dir so parallel workers do not
    # clobber each other's stub skill file.
    project_dir = Path(scratch_dir) / unique_id
    skills_dir = project_dir / ".opencode" / "skills" / skill_name

    try:
        skills_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"name: {skill_name}\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name} (eval stub)\n\n"
            f"{marker}\n"
        )
        (skills_dir / "SKILL.md").write_text(command_content, encoding="utf-8")

        cmd = [
            "opencode",
            "run",
            "--standalone",
            "--format", "json",
        ]
        if model:
            cmd.extend(["--model", model])

        # The query goes over stdin (not argv): Windows caps the command line
        # at ~32k chars, and `opencode run` reads the message from stdin.
        try:
            process = subprocess.run(
                cmd,
                input=query,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=project_dir,
                timeout=timeout,
                check=False,
            )
            buffer = process.stdout.decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired as e:
            # The query did not finish in time. If the skill was triggered
            # before the timeout, count it; otherwise treat as no trigger.
            out = e.stdout or b""
            buffer = out.decode("utf-8", errors="replace")

        # Parse the NDJSON event stream for a `skill` tool_use that names
        # the stub and whose output carries the marker.
        for line in buffer.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "tool_use":
                continue
            part = event.get("part", {})
            if part.get("tool") != "skill":
                continue
            state = part.get("state", {}) or {}
            tool_input = state.get("input", {}) or {}
            if tool_input.get("id") != skill_name:
                continue
            output = state.get("output", "") or ""
            if marker in output:
                return True
        return False
    finally:
        # Remove the per-query project dir so the next run starts clean.
        shutil.rmtree(project_dir, ignore_errors=True)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    scratch_dir: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    scratch = Path(scratch_dir or (project_root / ".skill-eval-scratch"))
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    str(scratch),
                    model,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    # Clean up scratch on the way out.
    shutil.rmtree(scratch, ignore_errors=True)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model in provider/model form (default: opencode config's model)")
    parser.add_argument("--scratch-dir", default=None, help="Scratch dir for temp eval projects (default: <project_root>/.skill-eval-scratch)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        scratch_dir=args.scratch_dir,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
