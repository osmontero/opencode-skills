---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
compatibility: opencode
---

# Requesting Code Review

Dispatch code-reviewer sub-agent using the `task` tool to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history. This keeps the reviewer focused on the work product, not your thought process, and preserves your own context for continued work.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch `code-reviewer` or `code-quality-reviewer` global agent using the `task` tool:**

The `code-reviewer` and `code-quality-reviewer` agents are registered globally with appropriate review checklists. Invoke with context about what was implemented, plan reference, and git diff range. The agent will use `git diff {BASE_SHA}..{HEAD_SHA}` to inspect changes.

**Context to include in your Task tool prompt:**
- What you just built (brief summary)
- What it should do (plan or requirements reference)
- Starting commit SHA (`BASE_SHA`)
- Ending commit SHA (`HEAD_SHA`)

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code-reviewer sub-agent using the `task` tool]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 from docs/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Sub-agent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Choosing the Reviewer

| Agent | Use when | Refuses to |
|---|---|---|
| `spec-reviewer` | Immediately after implementation — does the code match the spec, nothing more, nothing less? | Comment on style or quality |
| `code-quality-reviewer` | **After** spec compliance passes — decomposition, naming, error handling, test quality | Re-litigate scope |
| `code-reviewer` | End of a feature or before merge — production readiness across the whole change | — |
| `reviewing-interface-quality` (skill) | The change includes user-facing UI | — |

**Order matters.** Running quality review before spec compliance wastes effort polishing code that may not be what was asked for. See subagent-driven-development.

## Writing the Dispatch Prompt

The reviewer starts with **no context**. What you write is everything they know — never your session history. A reviewer given a vague prompt returns vague findings.

The prompt contains, in this order:

1. **What was built** — two sentences
2. **What it should do** — the requirement or plan task text, pasted in full, not a file reference
3. **The diff range** — `BASE_SHA` and `HEAD_SHA`
4. **Where to look** — the files that changed
5. **What you already know** — deviations you made, and why
6. **What you want back** — the report format

**Paste the requirement text.** Telling the reviewer to read `docs/plans/x.md` costs a tool call and risks them reading the wrong task. You already have the text.

**Do not tell them what you think.** "I think the error handling is solid" biases the review toward agreement. State facts, ask for findings.

```
Review the implementation of Task 2 from the auth plan.

REQUIREMENT (verbatim from the plan):
  Add verifyIndex() and repairIndex() to src/index/verify.ts. verifyIndex()
  returns a list of issues across 4 types: orphaned, stale, duplicate,
  missing. repairIndex() fixes each type. Report progress every 100 items.

DIFF: git diff a7981ec..3df7661
FILES: src/index/verify.ts, src/index/types.ts, tests/index/verify.test.ts

KNOWN DEVIATION: used a WeakMap rather than the Map the plan specified,
so entries are collected with their request objects. Behavior identical.

Return: PASS or FAIL with file:line references for each finding.
```

## Acting on Feedback

**REQUIRED SUB-SKILL:** Use receiving-code-review before implementing any suggestion. Reviewers are sometimes wrong, and blind implementation of a wrong suggestion is worse than no review.

| Severity | Action |
|---|---|
| Critical | Fix before doing anything else |
| Important | Fix before the next task |
| Minor | Note it; fix if cheap, defer if not |

**Then re-review.** A reviewer that found issues has not approved the fixes. Re-dispatch with the same context plus what changed. Skipping the re-review is how "fixed" issues survive to merge.

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback
- Make the reviewer read the plan file instead of pasting the task text
- Include your own assessment in the prompt (biases the review)
- Accept a fix as done without re-review
- Review uncommitted work — commit first so the diff range is real

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

## Common Mistakes

**Dispatching with session context.** The reviewer inherits your assumptions and reviews your reasoning rather than the code.

**No diff range.** The reviewer reads the whole file and comments on pre-existing code that is not part of this change.

**Reviewing before committing.** No stable range to diff, and the reviewer may see a half-saved state.

**One reviewer for both spec and quality.** They are different questions and merging them means the scope question gets less attention than it needs.

**Treating the review as a formality.** If every review returns "approved, no issues", either the prompt is biasing it or the wrong reviewer is being used.
