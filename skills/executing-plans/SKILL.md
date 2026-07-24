---
name: executing-plans
description: Use when you have a written implementation plan to execute in the current session with review checkpoints, and subagents are unavailable or the tasks are too coupled to delegate
compatibility: opencode
---

# Executing Plans

## Overview

Load the plan, review it critically, execute in batches with checkpoints, verify, and hand off.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Prefer subagent-driven-development when you can.** Fresh context per task and two-stage review produce measurably better results than inline execution. Use this skill when subagents are unavailable, when tasks are too tightly coupled to isolate, or when the plan is small enough that dispatch overhead exceeds the benefit.

## The Iron Law

```
NO EXECUTION WITHOUT A CRITICAL REVIEW OF THE PLAN FIRST
```

Executing a flawed plan faithfully produces a flawed implementation efficiently. The review is not a formality — it is the only point where a bad plan costs minutes instead of hours.

Started executing without reviewing? Stop and review now. It is cheaper at task 2 than at task 9.

## Checklist

Create a todo for each:

1. **Verify the workspace** — isolated branch or worktree, clean baseline
2. **Load and review the plan critically** — raise concerns before starting
3. **Build the todo list** — one entry per task
4. **Execute in batches** — 2-3 tasks, then checkpoint
5. **Verify at each checkpoint** — run the actual commands
6. **Final verification** — full suite, plan coverage check
7. **Hand off** — finishing-a-development-branch

## Step 1: Verify the Workspace

**REQUIRED SUB-SKILL:** Use using-git-worktrees before starting.

**Never begin implementation on `main`/`master` without explicit consent.** Check first:

```bash
git branch --show-current
git status --porcelain    # must be clean before starting
```

A dirty tree means you cannot tell your changes from pre-existing ones at review time.

## Step 2: Review the Plan Critically

Read the whole plan before writing any code. Check for:

| Check | Red flag |
|---|---|
| **Placeholders** | "TBD", "add error handling", "write tests for the above", "similar to Task 3" |
| **Type consistency** | `clearLayers()` in Task 3, `clearFullLayers()` in Task 7 |
| **Undefined references** | A task uses a type or function no task defines |
| **File paths** | Paths that do not exist and no task creates |
| **Verification** | Steps with no command, or commands with no expected output |
| **Ordering** | Task 5 depends on something Task 8 builds |
| **Scope** | Multiple independent subsystems that should have been separate plans |

**If you find issues:** raise all of them at once, before starting. Do not fix the plan silently and do not discover them one at a time across the session.

```
Reviewed the plan. Three issues before I start:

1. Task 4 calls `validateToken()` — no task defines it. Task 2 defines
   `verifyToken()`. Same function, or a gap?
2. Task 6 modifies `src/auth/session.ts:40-58`; that file is 22 lines.
   The line range is stale.
3. Tasks 8-11 cover the notifications subsystem, independent of auth.
   Split into a second plan?
```

## Step 3: Execute in Batches

Work 2-3 tasks at a time, then checkpoint. Batching keeps momentum without letting errors compound across nine tasks.

For each task:

1. Mark in_progress
2. **Follow the steps exactly** — the plan's granularity is deliberate
3. Run the verification the step specifies and read the output
4. Commit as the plan directs
5. Mark completed

**Follow the plan's steps exactly** means writing the failing test first when the plan says to, and running it to watch it fail before implementing. Skipping the "run it and see it fail" step is the most common way plan execution silently degrades — see test-driven-development.

**Do not batch commits.** Committing per task is what makes a checkpoint reviewable and a mistake revertible.

## Step 4: Checkpoint

After each batch, report and pause:

```
Tasks 1-3 complete.

- Task 1: token verification — 6 tests, all passing
- Task 2: session store — 4 tests, all passing
- Task 3: middleware wiring — 3 tests, all passing

Full suite: 47 passed, 0 failed.
Deviation: Task 2 specified a Map; used a WeakMap so sessions are
garbage-collected with their request objects. Behavior is identical.

Continue with tasks 4-6?
```

Checkpoints report **evidence**, not confidence — actual command output, not "should be working." See verifying-before-completion.

Optionally dispatch a reviewer at each checkpoint — see requesting-code-review.

## Step 5: Handling Deviations

Plans meet reality. Classify what happens next:

| Situation | Do |
|---|---|
| Step's code has a typo/obvious small error | Fix it, note it at the checkpoint |
| Step's approach works but a better one exists | Follow the plan. Note the alternative. Do not unilaterally improve. |
| Step is impossible as written | Stop. Report why. Propose an alternative. Wait. |
| Step's assumption about the codebase is wrong | Stop. The plan needs updating, not working around. |
| A task turns out unnecessary | Stop and ask — do not silently skip |
| You discover an unrelated bug | Note it. Do not fix it. Scope creep in execution is how plans lose their meaning. |

**Never silently deviate.** Every deviation is reported at the next checkpoint, however small.

## When to Stop and Ask

**STOP immediately when:**

- A blocker appears — missing dependency, environment problem, failing baseline
- An instruction is genuinely unclear
- The same verification fails twice
- The plan's assumptions about the codebase turn out to be wrong
- Implementing a step would require restructuring code the plan did not anticipate

**Ask rather than guess.** A wrong guess at task 3 corrupts every task after it.

**If verification fails repeatedly:** stop and use systematic-debugging. Do not attempt fix after fix — three failed fixes means the problem is not where you think it is.

## Step 6: Final Verification

Before handing off, **REQUIRED SUB-SKILL:** use verifying-before-completion.

- [ ] Every task in the plan is checked off
- [ ] Full test suite run in this message — output read, 0 failures
- [ ] Linter and build run clean
- [ ] Re-read the plan's goal: does the implementation deliver it?
- [ ] Every deviation reported to the user
- [ ] `git status` clean; every change committed

**Plan coverage check:** walk the plan's requirements and point to the code implementing each. A passing test suite proves the tests pass, not that the plan was fulfilled.

## Step 7: Hand Off

**REQUIRED SUB-SKILL:** Use finishing-a-development-branch to verify tests, present the merge/PR/keep/discard options, and clean up.

## Common Mistakes

**Executing before reviewing.** The plan's flaws get faithfully implemented.

**Skipping "watch it fail".** The plan says run the test and see it fail. Skipping it means you never learn whether the test tests anything.

**Silent deviation.** The implementation drifts from the plan and nobody knows until review.

**Batching all commits at the end.** No revertible checkpoints, and an unreviewable diff.

**Forcing through a blocker.** Three fixes deep on a step that was wrong to begin with.

**"While I'm here" changes.** Unrelated refactoring during execution makes the diff unreviewable and the deviation invisible.

**Claiming completion from memory.** "All tests passed earlier" is not verification. Run them now.

## Integration

**Required workflow skills:**
- **using-git-worktrees** — REQUIRED: isolated workspace before starting
- **writing-plans** — creates the plan this skill executes
- **test-driven-development** — how to execute the test-first steps correctly
- **verifying-before-completion** — REQUIRED before any completion claim
- **finishing-a-development-branch** — REQUIRED: complete development after all tasks

**When things go wrong:**
- **systematic-debugging** — verification failing repeatedly
- **receiving-code-review** — acting on checkpoint review feedback

**Alternative:**
- **subagent-driven-development** — preferred when subagents are available
