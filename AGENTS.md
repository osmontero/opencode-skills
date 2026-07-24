> Org overview: [../../AGENTS.md](../../AGENTS.md)

# AGENTS.md

This repository contains **opencode skills and global agents** — Markdown-based instruction files installed into `~/.config/opencode/`. There is no application to run, no tests to execute, and no CI pipeline.

## Repository Structure

```
skills/          — 29 skill directories (each: SKILL.md + optional scripts/, references/, assets/)
agents/          — 10 agent definition files (YAML-frontmatter Markdown, *.md) + LICENSE.txt
.opencode/       — Local opencode config (opencode.json, prompts/)
```

## Key Facts

### Skills are Markdown files, not code

Each skill is a `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). The agent reads this file and follows its instructions. Bundled resources live alongside: `scripts/` (Python), `references/` (docs), `assets/` (templates).

**Editing a skill means editing its SKILL.md and any bundled files.** There is no compilation or build step.

### install.sh / install.ps1 is the deployment mechanism

`./install.sh` (Linux/macOS) or `./install.ps1` (Windows) copies skills, agents, MCP servers, and config to `~/.config/opencode/`. It also removes stale skills/agents/MCP servers no longer in the repo, installs Python deps via `uv`, replaces the global `opencode.json`, and copies prompt files. **After editing files in this repo, run the install script to apply changes to the active opencode configuration.**

### Python dependencies are managed by `uv`

`pyproject.toml` lists dependencies (pdfplumber, pypdf, pypdfium2, pillow, playwright, etc.). The virtual environment is installed at `~/.local/opencode-venv/` by the install script. Before running any Python scripts:

```bash
source ~/.local/opencode-venv/bin/activate
```

### Agent files use YAML frontmatter

Each `agents/<name>.md` has frontmatter with `description`, `mode: subagent`, and optionally `permission` and `model` fields. The body is Markdown instructions. The `description` triggers the agent — keep it specific and actionable. `agents/LICENSE.txt` is not an agent file.

### .opencode/ contains local config

`.opencode/opencode.json` configures providers, models, MCP servers, and agent prompts. It references `prompts/plan.txt` and `prompts/build.txt` for the plan and build workflows.

### Plan and build prompts are intentionally empty

`.opencode/prompts/plan.txt` and `build.txt` are **0 bytes** (emptied in commit `45c1d4a`). They are still referenced by `opencode.json` under `agent.plan.prompt` and `agent.build.prompt`, so the plan and build agents currently run with no custom prompt override — the workflow comes from the `brainstorming` and `subagent-driven-development` skills instead.

Leave them empty unless deliberately reinstating prompt overrides. If they are no longer wanted, remove the `agent.plan` / `agent.build` blocks from `opencode.json` as well so the config does not reference empty files.

### Design and UX is a four-skill cluster

`designing-frontend-interfaces` (visual craft, 5 reference files) → `designing-user-experience` (flows and states) → `building-accessible-interfaces` (WCAG 2.2 AA) → `reviewing-interface-quality` (audit rubric). `applying-themes` supplies contrast-verified palettes; the `interface-reviewer` agent runs the audit as a subagent.

**When editing any of them, keep the cross-references intact** — they name each other by skill name and by reference-file path, and the design skills are written to compose rather than duplicate. Contrast values in `applying-themes/themes/*.md` are machine-checked:

```bash
source ~/.local/opencode-venv/bin/activate
python3 skills/applying-themes/scripts/check_contrast.py skills/applying-themes/themes/*.md
```

That script exits non-zero on failure, so it works as a gate after editing any palette.

> `skills/applying-themes/theme-showcase.pdf` predates the current palettes and no longer matches the theme files. The markdown files are authoritative; regenerate or delete the PDF rather than treating it as a preview.

### Frontmatter conventions

Skills take `name` (must equal the directory name) and `description` only — plus `license` for Anthropic-derived skills and `compatibility: opencode` for superpowers-derived ones. **`mode`, `permission`, and `tools` are agent-only fields and must not appear on a skill.** Agents require `mode: subagent`; `permission.edit: deny` is correct for read-only reviewer agents.

Descriptions start with "Use when…" and describe *triggering conditions only* — never the skill's workflow. A description that summarizes the process gives the agent a shortcut it will take instead of reading the skill.

### README contains license attribution info and full skill/agent lists

The README documents third-party licenses and attributions, plus tables of all skills and agents. Keep it synchronized if you add/remove skills, agents, or change attribution sources.

### customize-opencode is built-in

The `customize-opencode` skill appears in the available skills list as `<built-in>` and is not in the repo. However, it triggers for editing `opencode.json`, `opencode.jsonc`, files under `.opencode/`, and files under `~/.config/opencode/`. Use it when working on opencode's own configuration.

### creating-skills is the meta-skill

`skills/creating-skills/` contains the full skill development lifecycle: drafting, testing, eval viewer, benchmarking, and description optimization. Its scripts (`scripts/aggregate_benchmark.py`, `scripts/run_loop.py`, etc.) and eval viewer (`eval-viewer/`) are the primary tooling for this repo.

### grader, comparator, and analyzer are skill-specific

These three agents are used exclusively by `skills/creating-skills/` for eval/benchmarking. They are not general-purpose and should remain specialized to that workflow.

## What NOT to do

- Do not run `npm test`, `pytest`, `make`, or similar — there are none.
- Do not create CI workflows — this repo has none and doesn't need them.
- Do not commit `uv.lock`, `.venv/`, `node_modules/`, or `.egg-info/` — they are gitignored.
- Do not edit skills directly in `~/.config/opencode/` — edit in the repo, then run the install script.
