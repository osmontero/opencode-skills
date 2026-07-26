---
description: Create or update AGENTS.md for this project
---
Create or update `AGENTS.md` for this project.

The goal is a compact instruction file that helps future sessions avoid mistakes and ramp up quickly. Every line must answer: **"Would an agent likely get this wrong without help?"** If not, leave it out. A long AGENTS.md that restates the obvious is worse than a short one, because it buries the few facts that matter.

User-provided focus or constraints (honor these):
$ARGUMENTS

## First, identify what this project is

Do not assume it is a code repository. It may be infrastructure, documentation, research, data, prose, configuration, a mixed workspace, or a monorepo containing several of these. The investigation is the same; what counts as high-signal differs.

If the directory contains several independent projects with no shared tooling, say so and write a short top-level file that routes to each, rather than inventing a unified workflow that does not exist.

## How to investigate

Read the highest-value sources first, in this order:

- `README*`, root manifests, workspace config, lockfiles
- build, test, lint, formatter, typecheck, and codegen config
- CI workflows, pre-commit hooks, task runner config (`Makefile`, `Taskfile`, `justfile`, `*.ps1`, `*.sh`)
- existing instruction files — `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`
- tool config that reveals conventions — `.editorconfig`, `.gitattributes`, `.gitignore`
- repo-local agent config such as `opencode.json`, `.opencode/`

For non-code projects, the equivalents are what governs the work: publishing or deploy config, data pipeline definitions, playbooks, style guides, templates, schemas.

If the structure is still unclear after config and docs, inspect a small number of representative files to find the real entrypoints and how things are wired together. Prefer files that explain the system over random leaf files.

**Prefer executable sources of truth over prose.** If the README conflicts with the config or the scripts, trust the executable source. Keep only what you can verify — check that a command exists before documenting it, and say so if you could not run it.

## What to extract

The highest-signal facts are the ones that took reading several files to infer:

- exact commands, especially non-obvious ones, and the right package manager or runner
- how to run one test, one package, or one focused verification step — not just the full suite
- required ordering when it matters (`lint → typecheck → test`, `build → sync → run`)
- workspace boundaries, ownership of major directories, and the real entrypoints
- toolchain quirks: generated code, migrations, codegen, build artifacts, env loading, dev servers, deploy flow
- **gotchas** — the things that silently do the wrong thing. A build step that must run before another. A config that is ignored unless an env var is set. A directory that looks editable but is generated.
- conventions that differ from the language, framework, or tool defaults
- testing quirks: fixtures, prerequisites, required services, snapshot workflows, slow or flaky suites
- what is deliberately absent, and should stay absent — no CI, no tests, no build step. Recording this stops the next agent from "helpfully" adding one.
- constraints worth preserving from existing instruction files

For non-code projects: how output is produced and published, where the source of truth lives versus generated artifacts, required review or approval steps, and any external system the work depends on.

## Questions

Only ask if the project genuinely cannot answer something important. Use the `question` tool for one short batch at most.

Worth asking:
- undocumented team conventions
- branch, PR, or release expectations
- setup or test prerequisites that are known but unwritten

Do not ask about anything the project already makes clear.

## Writing rules

Include only high-signal, project-specific guidance:
- exact commands and shortcuts an agent would otherwise guess wrong
- structure and architecture notes not obvious from filenames
- conventions that differ from defaults
- setup requirements, environment quirks, operational gotchas
- pointers to instruction sources that matter

Exclude:
- generic advice that applies to every project of this kind
- long tutorials or exhaustive file trees
- obvious language, framework, or tool conventions
- speculative claims, or anything you could not verify
- content better stored elsewhere and referenced via the `instructions` config

When in doubt, omit.

Prefer short sections and bullets. Lead each section with the fact, not the preamble. Keep commands in fenced blocks so they can be copied. If the project is simple, keep the file simple — a good AGENTS.md for a small project is a dozen lines. If it is large, summarize only the structural facts that change how an agent works.

Include a short "What NOT to do" section when the project has real prohibitions — do not add CI, do not edit generated files, do not commit secrets, do not run the deploy script locally.

## If AGENTS.md already exists

Improve it in place rather than rewriting blindly.

- Preserve guidance you can still verify.
- Delete stale claims — commands that no longer exist, structure that has moved, counts that no longer match.
- Reconcile it with the current state of the project, and note anything you changed that the user might not expect.
- Keep the existing voice and organization unless they are actively confusing.
