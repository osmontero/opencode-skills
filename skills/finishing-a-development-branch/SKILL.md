---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
compatibility: opencode
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

Stop. Don't proceed to Step 2.

**If tests pass:** Continue to Step 2.

### Step 2: Determine Base Branch

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main - is that correct?"

### Step 3: Present Options

Present exactly these 4 options:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Don't add explanation** - keep options concise.

### Step 4: Execute Choice

#### Option 1: Merge Locally

Base-branch work happens **in the canonical checkout**, not in the session's worktree. If the session is currently in a worktree (see using-git-worktrees), run these from the primary worktree (or `session_move` back first). You cannot `git checkout <base-branch>` inside the feature worktree — the base branch is already checked out in the primary worktree, and git refuses to check out the same branch in two worktrees at once.

```bash
# In the canonical checkout (primary worktree):
git checkout <base-branch>
git pull
git merge <feature-branch>
<test command>            # verify the merged result
git branch -d <feature-branch>
```

Then: move the session back to the canonical checkout (if it was in the worktree), and clean up the worktree (Step 5).

#### Option 2: Push and Create PR

```bash
# Push branch
git push -u origin <feature-branch>

# Create PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Report: "PR created. Branch <name> and worktree preserved."

**Don't cleanup worktree.**

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation.

If confirmed — delete the branch **from the canonical checkout**, then clean up the worktree:
```bash
# In the canonical checkout (primary worktree), NOT the session's worktree:
git branch -D <feature-branch>
```

Then: Cleanup worktree (Step 5).

### Step 5: Cleanup Worktree

**For Options 1, 4:**

Removing a worktree whose session is still inside it is not safe, so do this in two parts:

1. **If the session is in the worktree**, move it back to the canonical checkout first (`session_move` to the primary worktree path — see using-git-worktrees). A worktree that is the active session Location cannot be removed cleanly.
2. **Remove the worktree.** For an opencode v2 worktree (created by `worktree_create`), use the native `worktree_remove` tool with the worktree `directory`. `git worktree remove <path>` is only for plain-git worktrees that opencode does not record. Never set `force` unless the user has confirmed the uncommitted work should be discarded.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | ✓ | - | - | ✓ |
| 2. Create PR | - | ✓ | ✓ | - |
| 3. Keep as-is | - | - | ✓ | - |
| 4. Discard | - | - | - | ✓ (force) |

## Common Mistakes

**Skipping test verification**
- **Problem:** Merge broken code, create failing PR
- **Fix:** Always verify tests before offering options

**Open-ended questions**
- **Problem:** "What should I do next?" → ambiguous
- **Fix:** Present exactly 4 structured options

**Automatic worktree cleanup**
- **Problem:** Remove worktree when might need it (Option 2, 3)
- **Fix:** Only cleanup for Options 1 and 4

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation
- Force-push without explicit request

**Always:**
- Verify tests before offering options
- Present exactly 4 options
- Get typed confirmation for Option 4
- Clean up worktree for Options 1 & 4 only

## Integration

**Called by:**
- **subagent-driven-development** — after the final code review, once all tasks are complete
- **executing-plans** (Step 7: Hand Off) — after all batches complete

**Pairs with:**
- **using-git-worktrees** - Cleans up worktree created by that skill
