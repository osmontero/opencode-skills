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

(Windows: the venv is at `~\.local\opencode-venv\` — use `& ~\.local\opencode-venv\Scripts\python.exe <script>` or `.\Scripts\Activate.ps1`.)

### Agent files use YAML frontmatter

Each `agents/<name>.md` has frontmatter with `description`, `mode: subagent`, and optionally `permissions` (ordered array) and `model` fields, in the native v2 shape. The body is Markdown instructions. The `description` triggers the agent — keep it specific and actionable. `agents/LICENSE.txt` is not an agent file.

### .opencode/ contains local config

`.opencode/opencode.json` configures providers, models, MCP servers, agent prompts, and the `instructions` files that carry memory. It references `prompts/plan.txt` and `prompts/build.txt` for the plan and build workflows.

**This repo is OpenCode v2 (2.1.x) as of 2026-10-26.** Migrated from v1 (1.19.x). The v1 config is auto-normalized in memory by v2, so an old file still boots — but this one is now in native v2 shape. Things that changed and why it matters here:

- **`instructions` now resolves** — v2.0.x accepted the `instructions` array but never loaded its files (MEMORY.md would have silently stopped working); v2.1.0 added the loader (`#55539`). This repo's memory system depends on it. If you downgrade below 2.1.0, memory breaks.
- **No `compaction` agent override.** v2 compacts under the session agent's system prompt, not a dedicated compaction agent, so `agent.compaction.prompt` is ignored. The compaction-fidelity rules therefore live in `build.txt`/`plan.txt` (see Prompt overrides), and `prompts/compaction.txt` was deleted.
- **Plan files location.** v2's *default* plan-agent policy allows plan files under `~/.opencode/plan` (visible as a native allow rule in `opencode debug agents`), but v2 has **no native plan file or plan-mode reminder** — no `plan`-related string exists in the 2.1.4 binary. This repo's `plan` agent permission + `plan.txt` pin plans to `docs/plans/` and `docs/specs/`, and the allowlist *additionally* permits `~/.opencode/plan` (left over from v2's default). The allowlist is what actually works; the "plan mode" framing in skills/prompts is our own convention.
- **`lsp: true` removed.** v2 accepts but does not run LSP servers (no language servers, no LSP tools, no diagnostics). Lint/typecheck is done via shell commands, per `build.txt`. The old install-script npm steps (LSP deps in `~\.opencode\node_modules` and a v1 `@opencode-ai/plugin` dependency in `.opencode/package.json`) were deleted with it (2026-10-23); the install scripts no longer run `npm install` at all.
- **v2 install is a standalone binary** on Windows (curl/zip), not the `opencode-ai` npm package — npm/brew are no longer the v2 distribution. The npm v1 shim at `~\AppData\Roaming\npm\opencode.ps1` was removed.

### Prompt overrides are general-purpose by design

`.opencode/prompts/{build,plan}.txt` are **custom prompts**, wired via `agents.<name>.system` in `opencode.json`. They replace opencode's defaults, which are coding-specific.

**The governing rule: these prompts carry methodology, not domain knowledge.** How to work — task management, evidence before assertion, scope discipline, delegation, communication, memory, compaction fidelity. Domain technique belongs in skills. That split only holds because each prompt opens with a **Skills Come First** section instructing the agent to check for an applicable skill and to let it govern; removing that section reopens the gap that stripping the coding guidance created. Anything added here that is specific to code, or to any one domain, is in the wrong file.

- **`build.txt` and `plan.txt` deliberately diverge.** build is execution methodology; plan is investigation methodology (explore → constraints → options → agreement) with a definition of what a plan must contain. Upstream has no separate plan prompt — plan mode is enforced by injected `<system-reminder>` blocks and by permissions — so this divergence is ours, and both files still defer enforcement to those reminders rather than restating prohibitions.
- **Task Management is load-bearing, not boilerplate.** The upstream generic fallback ships with *no* task-management section, which is why the agents did not maintain todo lists. Both prompts now specify: list before starting, one `in_progress`, complete immediately without batching, discovered work becomes new items, re-read before claiming done.
- **Compaction fidelity lives in build/plan, not in a separate compaction prompt.** v2 compacts under the *session agent's* system prompt (not a dedicated compaction agent), so a `compaction` agent override is dead code. The counterweight to v2's built-in summarizer ("leave out instructions the agent was given") — keep standing user instructions and unreconstructable literals — is folded into a `# Compaction` section in both `build.txt` and `plan.txt`.
- **Overriding bypasses model-family selection.** v2 picks a default system prompt by substring-matching the model id (`gpt`/`gpt-astra`, `claude`, `kimi`, `trinity`, `muse`), falling through to a generic harness prompt — which is what the ThreatWinds `silas-*` ids resolve to. With a `system` override set, that selection no longer happens at all, for any model.
- **A prompt override replaces the model-family prompt entirely**, but not everything: the merge is `agent.system ? agent.system : SessionSystemPrompt.make(tools)`, and the environment block, date, and instruction sources (AGENTS.md, skills, MCP, references) are still appended after it.
- **Emptying a file is the revert.** A 0-byte `{file:}` reference substitutes an empty string, falling back to the default for that agent.
- **Prompt file references resolve against the config file's directory, not CWD or home.** `{file:./prompts/x.txt}` resolves relative to the `opencode.json` that contains it — so this repo's `.opencode/opencode.json` (auto-loaded as project config, which outranks the global one) reads `.opencode/prompts/` (what you edit), and the installed global config reads `~/.config/opencode/prompts/` (what install.sh placed there). Do not "fix" the references to `{file:~/.config/opencode/prompts/...}`: this repo would then silently use the installed copies and repo prompt edits would be ignored until the next reinstall.

Re-extract a current default after upgrading opencode (this dumps the live resolved prompt for every agent as JSON, so run it from a directory whose config does *not* override the agent, then find the agent's `system` field):

```bash
opencode debug agents    # JSON of all agents; grep for "build"/"plan"/"compaction"
```

Config keys are schema-verified against `https://opencode.ai/config.json`: `agents` accepts the named built-ins `build`, `plan`, `general`, `explore`, `title`, `summary`, and `compaction`, each taking `system`, `model`, `steps`, `permissions`, `request`, and other fields. `prompt` (v1) is auto-translated to `system`; `permission` (v1 map) is auto-translated to `permissions` (v2 ordered array); `variant` joins the model reference after `#`.

The separate top-level `compaction` block (`auto`, `keep.tokens`, `buffer`) controls *when and how much* to compact and is unrelated to the prompt. v2 has no native `tail_turns` or `prune` field; both legacy fields are ignored with a warning.

### Memory is two MEMORY.md files wired through `instructions`

`build.txt` has a **Memory** section telling the agent to record durable lessons on its own initiative — corrections, standing preferences, undocumented failure modes — into `~/.config/opencode/MEMORY.md` (global) or `.opencode/MEMORY.md` (per project). Global writes are autonomous; project writes are proposed first, because they land in the user's repository. This replaces the earlier plugin-based memory design (superseded 2026-08-05).

```json
"instructions": ["~/.config/opencode/MEMORY.md", ".opencode/MEMORY.md"]
```

- **One line here enables memory in every project**, because the install scripts copy this file over the *global* `~/.config/opencode/opencode.json`. No per-project setup.
- **Relative entries resolve per-project, not against the config file.** In v2 they go through `ConfigInstructionPlugin.match` → `fs.globUp(pattern, session.directory, project.root)` with `dot: true`, which scans the session cwd and every ancestor up to the project root — that is why `.opencode/MEMORY.md` matches. `~/`-prefixed and absolute entries resolve against home instead. Missing files are silently skipped (access-denied is kept absent), and a matched file is watched, so editing it mid-session re-injects it as an instruction update. v1 resolved these via `Instruction.systemPaths` → `globUp(pattern, session.directory, worktree)`.
- **`MEMORY.md` rather than `AGENTS.md`, deliberately.** Keeping agent-written memory out of `AGENTS.md` keeps `AGENTS.md` human-owned and clear of `/init`, which rewrites that file. (The v1 rationale that a global `AGENTS.md` displaced `~/.claude/CLAUDE.md` no longer applies — v2 discovers `AGENTS.md` only, with no `CLAUDE.md` fallback — but the split still holds.)
- **Long content is split into a detail file next to MEMORY.md, not inlined.** Because both `MEMORY.md` files are auto-injected on every session, every line costs tokens whether or not the topic is relevant. So when an entry would run more than a few lines (a table, a procedure, a cluster of related facts), the agent keeps **one line** in `MEMORY.md` — the key fact plus a pointer — and writes the full detail to a file in the same directory: `~/.config/opencode/memory/` for global, `.opencode/memory/` for project (kebab-case, named for the topic). These detail files are **not** auto-loaded; the agent reads one only when the topic is in play. This is why `memory/` subdirectories exist and why a `MEMORY.md` may point to files that are not otherwise part of the config. Project detail files are proposed, not written silently — they land in the user's repo. `build.txt`'s Memory section owns the operational rules; this bullet is the "why" for future sessions.
- **Plan mode writes only `docs/plans/*` and `docs/specs/*`.** The `plan` agent's `edit: deny *` is overridden by a narrow allowlist in `.opencode/opencode.json` so planning can persist its own deliverable (spec + plan) instead of leaving it in chat. Everything else stays denied. `plan.txt`'s Memory section says plan mode cannot write `MEMORY.md` either (it's not in the allowlist), so durable facts found while planning go into a "Memory to record" note at the end of the plan; `build.txt` tells the build session to work that note first when it picks up the plan.

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

### building-finetuning-datasets is gate-shaped, not checklist-shaped

The only ML skill in the repo, and the only one whose SKILL.md is mostly two decision gates plus a
required-parts contract, with all technique detail pushed into five `references/` files
(`choosing-technique`, `synthetic-generation`, `data-quality`, `lora-configuration`,
`avoiding-degradation`).

That shape came out of the baseline run, not from taste. Without the skill, the agent produced a
thorough 935-line plan that nonetheless: treated "know our service names and runbook facts" as a
fine-tuning target with zero mention of retrieval; set `lora_alpha` to half the rank, calling
`alpha/r = 0.5` "the standard starting point"; and never once mentioned forgetting, replay, dedup,
decontamination, loss masking, chat templates, EOS, or measuring the base model first. The failure was
never refusal — it was a complete-looking deliverable with required parts missing. Per
`creating-skills`, omitted elements call for a structural contract rather than prohibitions, which is
why "The deliverable" section enumerates six required artifacts in build order instead of warning
against skipping them.

Two facts in there are load-bearing and get "corrected" by well-meaning edits: `alpha = 2r` (not
`0.5r`), and facts belong in RAG because training on unknown facts *linearly increases hallucination*
rather than merely failing to stick. Both are cited to their papers in the skill; keep the citations.

Several claims were cross-checked against a real fine-tuning operation (`threatwinds/llm-finetune`,
a sibling repo) and adjusted where field evidence disagreed with the literature: `lora_dropout` and a
validation split are documented there as *regression* levers, not just anti-overfitting ones (their
v13→v14 narrowed a benchmark regression with that single change), so the skill promotes them; `packing`
is framed as off-by-default for small/multi-turn data because their agentic runs disable it; and their
practice of probing the base model and *dropping* slices it already passes became "Gate 3." That repo's
per-behavior mix-share findings (≈33% fixes a hard prior, ≈18% regresses) are in `data-quality.md`. The
anonymized "documented ~750-row case" phrasing in the references points at that work — keep it
anonymized; the skill is general and their redteam/exploit specifics are sensitive.

### Custom commands override built-ins by name

`.opencode/command/<name>.md` defines a slash command. opencode globs `{command,commands}/**/*.md` from its config directories and merges each by name with `c.template = a.template` — an **unconditional** assignment, so a file named `init.md` replaces the built-in `/init` entirely. This is the same override surface as `agent.<name>`, and it is how `/init` in this repo is customized.

The file is frontmatter (`description`, optionally `agent`, `model`, `subtask`) plus a body that becomes the template. Templates support `$ARGUMENTS` and positional `$1`, `$2`. They do **not** support `${path}` — that appears in opencode's built-in prompts but is JS interpolation resolved at build time, not template syntax.

Recover a built-in command's original text by extracting it from the opencode binary; `opencode debug` has no command inspector, and there is no `debug command` equivalent to `debug agent`.

### Frontmatter conventions

Skills take `name` (must equal the directory name) and `description` only — plus `license` for Anthropic-derived skills and `compatibility: opencode` for superpowers-derived ones. **`mode`, `permission`, and `tools` are agent-only fields and must not appear on a skill.** Agents require `mode: subagent`; a `permissions` entry of `edit: deny` on `*` is correct for read-only reviewer agents.

This repo's agent files use the native v2 frontmatter shape: `permissions:` is an ordered list of `{action, resource, effect}` objects (e.g. `{ action: edit, resource: "*", effect: deny }`). v2 still auto-translates legacy v1 keys (`permission` map → `permissions`, `prompt` → `system`, `disable` → `disabled`, `model`+`variant` → `model#variant`), but do not reintroduce them when editing — keep the native shape.

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
