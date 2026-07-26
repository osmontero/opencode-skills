> Org overview: [../../AGENTS.md](../../AGENTS.md)

# AGENTS.md

This repository contains **opencode skills and global agents** — Markdown-based instruction files installed into `~/.config/opencode/`. There is no application to run, no tests to execute, and no CI pipeline.

## Repository Structure

```
skills/          — 33 skill directories (each: SKILL.md + optional scripts/, references/, assets/)
agents/          — 11 agent definition files (YAML-frontmatter Markdown, *.md) + LICENSE.txt
.opencode/       — Local opencode config (opencode.json, prompts/, command/)
```

## Key Facts

### Skills are Markdown files, not code

Each skill is a `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). The agent reads this file and follows its instructions. Bundled resources live alongside: `scripts/` (Python), `references/` (docs), `assets/` (templates).

**Editing a skill means editing its SKILL.md and any bundled files.** There is no compilation or build step.

### install.sh / install.ps1 is the deployment mechanism

`./install.sh` (Linux/macOS) or `./install.ps1` (Windows) copies skills, agents, MCP servers, commands, and config to `~/.config/opencode/`. It also removes stale skills/agents/MCP servers/commands no longer in the repo, installs Python deps via `uv`, replaces the global `opencode.json`, and copies prompt files. **After editing files in this repo, run the install script to apply changes to the active opencode configuration.**

Both installers must stay in sync. A new deployable directory added to one is a bug in the other.

### Python dependencies are managed by `uv`

`pyproject.toml` lists dependencies (pdfplumber, pypdf, pypdfium2, pillow, playwright, etc.). The virtual environment is installed at `~/.local/opencode-venv/` by the install script. Before running any Python scripts:

```bash
source ~/.local/opencode-venv/bin/activate
```

### Agent files use YAML frontmatter

Each `agents/<name>.md` has frontmatter with `description`, `mode: subagent`, and optionally `permission` and `model` fields. The body is Markdown instructions. The `description` triggers the agent — keep it specific and actionable. `agents/LICENSE.txt` is not an agent file.

### .opencode/ contains local config

`.opencode/opencode.json` configures providers, models, MCP servers, and agent prompts. It references `prompts/plan.txt` and `prompts/build.txt` for the plan and build workflows.

### Prompt overrides are general-purpose by design

`.opencode/prompts/{build,plan,compaction}.txt` are **custom prompts**, wired via `agent.<name>.prompt` in `opencode.json`. They replaced opencode's defaults, which were coding-specific.

**The governing rule: these prompts carry methodology, not domain knowledge.** How to work — task management, evidence before assertion, scope discipline, delegation, communication. Domain technique belongs in skills. That split only holds because each prompt opens with a **Skills Come First** section instructing the agent to check for an applicable skill and to let it govern; removing that section reopens the gap that stripping the coding guidance created. Anything added here that is specific to code, or to any one domain, is in the wrong file.

- **`build.txt` and `plan.txt` deliberately diverge.** build is execution methodology; plan is investigation methodology (explore → constraints → options → agreement) with a definition of what a plan must contain. Upstream has no separate plan prompt — plan mode is enforced by injected `<system-reminder>` blocks and by permissions — so this divergence is ours, and both files still defer enforcement to those reminders rather than restating prohibitions.
- **Task Management is load-bearing, not boilerplate.** The upstream variant these replaced (`Ta`, the generic fallback) ships with *no* task-management section, which is why the agents did not maintain todo lists. Both prompts now specify: list before starting, one `in_progress`, complete immediately without batching, discovered work becomes new items, re-read before claiming done.
- **`compaction.txt` cooperates with a contract it cannot override.** opencode supplies its own user-side prompt demanding a fixed five-section structure wrapped in `<summary>` tags. The system prompt cannot change that, so it adds *fidelity* rules inside it: standing user instructions and unreconstructable literals (keys, IDs, paths, versions, exact commands) are copied verbatim, and narrative is what gets cut when space runs short. Do not add competing section structures here — they will fight the user prompt.
- **Overriding bypasses model-family selection.** opencode picks a default system prompt by substring-matching the model id (`claude`, `gpt`/`codex`, `gemini-`, `kimi`, `trinity`, `muse-spark`), falling through to a generic variant — which is what the ThreatWinds `qwen-*`/`silas-*` ids resolve to. With an override set, that selection no longer happens at all, for any model.
- **A prompt override replaces the model-family prompt entirely**, but not everything: the merge is `agent.prompt ? [agent.prompt] : provider(model)`, and the environment block plus any user system prompt are still appended after it.
- **Emptying a file is the revert.** That truthiness check means a 0-byte file falls back to opencode's default.

Re-extract a current default after upgrading opencode (this prints the live resolved prompt, so run it from a directory whose config does *not* override the agent):

```bash
opencode debug agent compaction    # also: build, plan, title, summary
```

Config keys are schema-verified against `https://opencode.ai/config.json`: `agent` accepts the named built-ins `plan`, `build`, `general`, `explore`, `title`, `summary`, and `compaction`, each taking a full `AgentConfig` (`prompt`, `model`, `variant`, `temperature`, `top_p`, `steps`, `permission`).

The separate top-level `compaction` block (`auto`, `prune`, `reserved`, `tail_turns`, `preserve_recent_tokens`) controls *when and how much* to compact and is unrelated to the prompt.

### Design and UX is a four-skill cluster

`designing-frontend-interfaces` (visual craft, 5 reference files) → `designing-user-experience` (flows and states) → `building-accessible-interfaces` (WCAG 2.2 AA) → `reviewing-interface-quality` (audit rubric). `applying-themes` supplies contrast-verified palettes; the `interface-reviewer` agent runs the audit as a subagent.

**When editing any of them, keep the cross-references intact** — they name each other by skill name and by reference-file path, and the design skills are written to compose rather than duplicate. Contrast values in `applying-themes/themes/*.md` are machine-checked:

```bash
source ~/.local/opencode-venv/bin/activate
python3 skills/applying-themes/scripts/check_contrast.py skills/applying-themes/themes/*.md
```

That script exits non-zero on failure, so it works as a gate after editing any palette.

> `skills/applying-themes/theme-showcase.pdf` predates the current palettes and no longer matches the theme files. The markdown files are authoritative; regenerate or delete the PDF rather than treating it as a preview.

### Engineering rigor is a four-skill cluster

`reviewing-security` (+ `security-reviewer` agent), `evolving-apis-and-schemas`, `investigating-performance`, and `writing-release-notes`. Each is built around a single refusal stated as an Iron Law, and the value is in the refusal — an edit that softens one into advice removes the reason the skill exists:

| Skill | Iron Law |
|---|---|
| `reviewing-security` | No finding without a path from attacker-controlled input to impact |
| `evolving-apis-and-schemas` | Additive first, destructive last — never in the same deploy |
| `investigating-performance` | No optimization without a measurement that names the bottleneck |
| `writing-release-notes` | Every entry states what changed for the reader, not what changed in the code |

The first three carry a `references/` file each (vulnerability patterns, migration recipes, profiling tools) linked one level deep from SKILL.md. Keep them one level deep — nested references get partially read.

### Custom commands override built-ins by name

`.opencode/command/<name>.md` defines a slash command. opencode globs `{command,commands}/**/*.md` from its config directories and merges each by name with `c.template = a.template` — an **unconditional** assignment, so a file named `init.md` replaces the built-in `/init` entirely. This is the same override surface as `agent.<name>`, and it is how `/init` in this repo is customized.

The file is frontmatter (`description`, optionally `agent`, `model`, `subtask`) plus a body that becomes the template. Templates support `$ARGUMENTS` and positional `$1`, `$2`. They do **not** support `${path}` — that appears in opencode's built-in prompts but is JS interpolation resolved at build time, not template syntax.

Recover a built-in command's original text by extracting it from the opencode binary; `opencode debug` has no command inspector, and there is no `debug command` equivalent to `debug agent`.

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
