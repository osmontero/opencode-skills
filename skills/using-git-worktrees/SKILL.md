---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates an isolated git worktree (via the native opencode v2 worktree tools) and moves the session into it
compatibility: opencode
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** In opencode v2, worktrees are created with the native `worktree_*` tools, and the *session* moves into the worktree — not just the shell. This keeps opencode's tracking (list/remove), project config, and AGENTS.md discovery pointing at the right place.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Default Path: Native Worktree Tools

Use this when running inside opencode v2 (the normal case). The tools are `worktree_create`, `worktree_list`, `worktree_remove` (Code Mode namespace `opencode`), plus `session_move`.

### 1. Create the worktree

Call `worktree_create` with a `name` — use the feature/branch name (e.g. `auth`, `fix-login-timeout`). It returns `{ directory }`.

Where the worktree lands is decided by the `worktree.directory` setting in the project's opencode config, not by the skill:

- **Not set (default):** opencode's data directory, `worktree/<project-id prefix>/<name>` — outside the repo, so nothing to gitignore.
- **Set** (e.g. `"worktree": { "directory": ".worktrees" }`): relative paths resolve against the project's canonical checkout. If the directory is *inside* the repo, it must be gitignored (see below).

Do not hand-roll the location with `git worktree add` — opencode only records and manages worktrees it created itself, so manual ones are invisible to `worktree_list` / `worktree_remove`.

If the user wants a non-default location, the v2-idiomatic move is to set `worktree.directory` in the config (and note it in AGENTS.md or memory) — not to pick a path per session.

### 2. Create the branch

`worktree_create` does not take a branch name: the new worktree is at a **detached HEAD** on the repo's current commit. Create the branch from inside the worktree:

```bash
git checkout -b "<branch-name>"
```

(`git checkout main` would fail — main is already checked out in the primary worktree; that is expected and not an error.)

### 3. Move the session into the worktree

Call `session_move` with the worktree directory as `directory`. The move takes effect at a safe boundary, so destination-dependent work (reads, edits, setup commands) belongs in the next call.

**Why this instead of `cd`:** a shell `cd` only changes one command's working directory; `session_move` re-roots the session's Location, so tool calls, config discovery, and instruction files all resolve against the worktree checkout.

### 4. Project-local location safety (only if inside the repo)

When `worktree.directory` places worktrees inside the checkout (`.worktrees/`, `worktrees/`, …), verify the directory is ignored **before** creating the worktree:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If not ignored: add it to `.gitignore`, commit, then create. This prevents worktree contents from polluting `git status` or being accidentally committed.

### 5. Run project setup

The worktree is a fresh checkout — dependencies are not shared with the main worktree. Auto-detect and run setup:

```bash
# Node.js
[ -f package.json ] && npm install

# Rust
[ -f Cargo.toml ] && cargo build

# Python
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f pyproject.toml ] && poetry install

# Go
[ -f go.mod ] && go mod download
```

### 6. Verify clean baseline and report

Run the project's tests to confirm the worktree starts green:

```bash
# project-appropriate: npm test / cargo test / pytest / go test ./...
```

**If tests fail:** report the failures and ask whether to proceed or investigate. **If they pass:** report ready.

```
Worktree ready at <full-path> (branch <name>)
Session moved. Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Cleanup

Pairs with **finishing-a-development-branch** after the work is done:

- `worktree_remove` with the worktree `directory` removes a worktree opencode recorded for the project. It uses the `edit` permission on that directory; set `force: true` only to discard uncommitted changes.
- Never remove a worktree with unpushed, unmerged commits without explicit confirmation — that deletes the work.
- A worktree created manually with raw git (fallback below) is not recorded by opencode; remove it with `git worktree remove <path>` instead.

## Fallback: Raw Git

Use `git worktree add` directly only when:

- Running in a harness without the native tools (Claude Code, Codex, plain terminal).
- The worktree needs a base other than the current HEAD (`git worktree add <path> -b <branch> <base-commit>`).
- The user explicitly asks for a manual worktree.

The same safety rules apply: gitignore check for project-local paths, setup, baseline tests, and announce the location.

## Quick Reference

| Situation | Action |
|-----------|--------|
| In opencode v2 | `worktree_create` → `git checkout -b` → `session_move` → setup → baseline |
| Non-default location wanted | Set `worktree.directory` in opencode config |
| Location inside repo | `git check-ignore` first; add to `.gitignore` + commit if not |
| Needs a base other than HEAD | Fallback: `git worktree add <path> -b <branch> <base>` |
| Tests fail during baseline | Report failures + ask |
| Work done | finishing-a-development-branch → `worktree_remove` |

## Common Mistakes

**Assuming `worktree_create` makes a branch**
- **Problem:** It leaves a detached HEAD; commits land nowhere a branch points at.
- **Fix:** `git checkout -b <branch>` inside the worktree immediately after creation.

**`cd`-ing into the worktree instead of `session_move`**
- **Problem:** Only the shell's CWD changes; the session, config, and instruction discovery still point at the old location.
- **Fix:** Call `session_move`; put dependent work in the next turn.

**Hand-rolling `git worktree add` in opencode**
- **Problem:** opencode doesn't record manual worktrees, so `worktree_list`/`worktree_remove` can't see them, and the location ignores `worktree.directory`.
- **Fix:** Use the native tools in v2; raw git is the fallback above.

**Proceeding with failing baseline tests**
- **Problem:** Can't distinguish new bugs from pre-existing issues.
- **Fix:** Report failures, get explicit permission to proceed.

## Red Flags

**Never:**
- Commit on the detached HEAD (create the branch first)
- Remove a worktree with unpushed/unmerged work without confirmation
- Skip baseline test verification
- Assume the default location when the user has a project-local preference — check/set `worktree.directory`

**Always:**
- Use native tools in opencode v2, raw git only in the fallback cases
- Move the session with `session_move` after creation
- Verify gitignore for in-repo locations
- Auto-detect and run project setup, then a clean test baseline

## Example Workflow

```
You: I'm using the using-git-worktrees skill to set up an isolated workspace.

[worktree_create name="auth" -> C:\Users\osmon\.local\share\opencode\worktree\c3488b\auth]
[git checkout -b feature/auth]
[session_move directory=<worktree dir>]
[npm install, npm test - 47 passing]

Worktree ready at C:\Users\osmon\.local\share\opencode\worktree\c3488b\auth (branch feature/auth)
Session moved. Tests passing (47 tests, 0 failures)
Ready to implement auth feature
```

## Integration

**Called by:**
- **subagent-driven-development** - REQUIRED before executing any tasks
- **executing-plans** - REQUIRED before executing any tasks
- Any skill needing an isolated workspace

**Pairs with:**
- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
