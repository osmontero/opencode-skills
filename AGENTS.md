# AGENTS.md

This repository contains **opencode skills and global agents** — Markdown-based instruction files installed into `~/.config/opencode/`. There is no application to run, no tests to execute, and no CI pipeline.

## Repository Structure

```
skills/          — 26 skill directories (each: SKILL.md + optional scripts/, references/, assets/)
agents/          — 8 agent definition files (YAML-frontmatter Markdown, *.md) + LICENSE.txt
.opencode/       — Local opencode config (opencode.json, prompts/, plans/)
```

## Key Facts

### Skills are Markdown files, not code

Each skill is a `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). The agent reads this file and follows its instructions. Bundled resources live alongside: `scripts/` (Python), `references/` (docs), `assets/` (templates).

**Editing a skill means editing its SKILL.md and any bundled files.** There is no compilation or build step.

### Python dependencies are managed by `uv`

`pyproject.toml` lists dependencies (pdfplumber, pypdf, pypdfium2, pillow, playwright, etc.). The virtual environment is installed at `~/.local/opencode-venv/` by `install.sh`. Before running any Python scripts:

```bash
source ~/.local/opencode-venv/bin/activate
```

### install.sh is the deployment mechanism

`./install.sh` copies skills, agents, and config to `~/.config/opencode/`. It also removes stale skills/agents no longer in the repo, installs Python deps, replaces the global `opencode.json`, and copies prompt files. **After editing files in this repo, run `./install.sh` to apply changes to the active opencode configuration.**

### Agent files use YAML frontmatter

Each `agents/<name>.md` has frontmatter with `description`, `mode: subagent`, and optionally `permission` and `model` fields. The body is Markdown instructions. The `description` triggers the agent — keep it specific and actionable. `agents/LICENSE.txt` is not an agent file.

### .opencode/ contains local config

`.opencode/opencode.json` configures providers, models, MCP servers, LSP, and agent prompts. It references `prompts/plan.txt` and `prompts/build.txt` for the plan and build workflows. The `plans/` directory stores implementation plans.

**LSP servers:** TypeScript/JavaScript uses `npx -y typescript-language-server --stdio` (no global install). Other LSPs (gopls, rust-analyzer, dart, jdtls) require their respective tools installed globally.

### Plan and build prompts define the core workflow

- `.opencode/prompts/plan.txt` — Brainstorming workflow: explore → clarify → design → spec → writing-plans skill
- `.opencode/prompts/build.txt` — Subagent-driven development: implementer → spec-reviewer → code-quality-reviewer → code-reviewer

These are wired into `opencode.json` under `agent.plan.prompt` and `agent.build.prompt`.

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
- Do not edit skills directly in `~/.config/opencode/` — edit in the repo, then run `./install.sh`.
