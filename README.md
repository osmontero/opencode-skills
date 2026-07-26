# opencode-skills

Adapted skills and agents for the opencode agent ecosystem.

## Contents

**33 skills** covering development workflows, design and UX, accessibility, security, performance, schema evolution, document processing, code review, testing, debugging, and more.

**11 global agents** for implementation, review, and evaluation.

### Design & UX cluster

Four skills that compose into a full interface workflow, plus a review agent:

| Skill | Covers |
|---|---|
| `designing-frontend-interfaces` | Visual craft — aesthetic direction, type scales, color ramps, layout, motion. Five reference files including a catalog of 12 parameterized aesthetic directions. |
| `designing-user-experience` | Behavior — flows, the empty/loading/error/partial state matrix, forms, microcopy, destructive actions, touch. |
| `building-accessible-interfaces` | WCAG 2.2 AA in practice — semantics, keyboard, focus management, ARIA, contrast, live regions, component patterns. |
| `reviewing-interface-quality` | Critique rubric tying the three together, with an evidence requirement and severity grading. |

`applying-themes` supplies ten contrast-verified palettes with semantic tokens and a `check_contrast.py` gate. The `interface-reviewer` agent runs the review rubric as a subagent.

### Engineering rigor cluster

Four skills for the failure modes that cost the most to undo, each built around one refusal:

| Skill | Refuses |
|---|---|
| `reviewing-security` | A finding without a traced path from attacker-controlled input to impact. Sink table, authorization checklist, scanner reachability, plus a vulnerability-patterns reference. |
| `evolving-apis-and-schemas` | Additive and destructive changes in the same deploy. Expand/contract sequencing, proto and SQL compatibility rules, migration recipes. |
| `investigating-performance` | An optimization without a measurement that names the bottleneck. Characterization table, profiling per dimension, tail-latency causes. |
| `writing-release-notes` | An entry that describes the code instead of the reader's change. |

The `security-reviewer` agent runs the security rubric as a subagent.

## License

This repository is licensed under **MIT** (see [LICENSE](LICENSE)).

### Third-Party Licenses and Attributions

Some skills and components incorporate work from other sources under different licenses:

#### Apache License 2.0 (Anthropic, PBC)

The following skills are licensed under Apache 2.0 and adapted from Anthropic's Claude projects:

- `creating-algorithmic-art` — Generative art creation with p5.js
- `designing-canvas-art` — Visual design for static documents
- `coauthoring-docs` — Structured documentation collaboration workflow
- `writing-internal-comms` — Internal communications templates and guidance
- `building-mcp-servers` — Model Context Protocol server development
- `creating-skills` — Skill development, testing, and benchmarking lifecycle
- `creating-slack-gifs` — Animated GIF creation for Slack
- `applying-themes` — Thematic styling for artifacts and documents
- `building-web-artifacts` — Multi-component HTML artifact creation
- `testing-webapps` — Playwright-based web application testing

#### MIT License (Jesse Vincent / obra/superpowers)

The following skills are MIT-licensed adaptations from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent:

- `brainstorming` — Creative exploration and requirements gathering
- `dispatching-parallel-agents` — Parallel task execution across independent agents
- `executing-plans` — Plan execution with review checkpoints
- `finishing-a-development-branch` — Branch completion and merge guidance
- `receiving-code-review` — Code review feedback processing and implementation
- `requesting-code-review` — Pre-merge code review verification
- `subagent-driven-development` — Multi-agent implementation workflow
- `systematic-debugging` — Structured bug investigation and resolution
- `test-driven-development` — TDD implementation workflow
- `using-git-worktrees` — Git worktree isolation for feature development
- `using-superpowers` — Skill discovery and activation
- `verifying-before-completion` — Pre-commit verification and evidence gathering
- `writing-plans` — Implementation plan creation from specs

#### MIT License (sst/opencode)

The agent prompts in `.opencode/prompts/` are adapted from opencode's own built-in agent prompts ([sst/opencode](https://github.com/sst/opencode), MIT), extracted from the opencode 1.18.4 binary:

- `build.txt`, `plan.txt` — from opencode's default agent system prompt
- `compaction.txt` — from opencode's built-in compaction prompt

All three have since been substantially rewritten to be general-purpose rather than coding-specific (see `AGENTS.md`). What remains derived is the structure plus a small amount of verbatim text: the opencode self-help block, the code-reference example, and two lines of the compaction anchoring contract.

#### MIT License (this repository)

The following are original to this repository and carry the repository's MIT license:

- `designing-user-experience` — Interaction design, state coverage, forms, microcopy
- `building-accessible-interfaces` — Practical WCAG 2.2 AA guidance and component patterns
- `reviewing-interface-quality` — Interface critique and QA rubric
- `reviewing-security` — Path-based security review with a vulnerability-patterns reference
- `evolving-apis-and-schemas` — Backward-compatible proto, SQL, and API evolution
- `investigating-performance` — Measurement-first performance investigation and profiling
- `writing-release-notes` — Changelogs, release notes, and upgrade guides
- `configuring-opencode` — opencode configuration reference
- `agents/interface-reviewer.md` — UI review subagent
- `agents/security-reviewer.md` — Security review subagent

See individual `skills/<name>/LICENSE.txt` files for full license text and attribution notices.

## Install

```bash
# Clone
git clone https://github.com/osmontero/opencode-skills.git

# Install
./install.sh
```

Or install manually:

```bash
# Skills
cp -r skills/* ~/.config/opencode/skills/

# Agents
cp agents/* ~/.config/opencode/agents/
```

## Agents

| Agent                   | Purpose                                                           |
|-------------------------|-------------------------------------------------------------------|
| `implementer`           | Executes plan tasks with TDD, self-review, status reporting       |
| `spec-reviewer`         | Verifies implementation matches spec (nothing more, nothing less) |
| `code-quality-reviewer` | Code quality review after spec compliance passes                  |
| `code-reviewer`         | General production-readiness code review                          |
| `security-reviewer`     | Security audit: traced exploit paths, severity by exploitability  |
| `grader`                | Evaluates skill test expectations with pass/fail verdicts         |
| `comparator`            | Blind A/B comparison of skill outputs                             |
| `analyzer`              | Post-hoc analysis + benchmark pattern detection                   |
| `interface-reviewer`    | UI quality audit: visual, UX, and accessibility, with rendered evidence |
| `internet-researcher`   | Web research, fact-checking, and source gathering                 |
| `pdf-extractor`         | Full PDF extraction via image conversion and OCR                  |

## Skills

| Skill                            | Category      |
|----------------------------------|---------------|
| `applying-themes`                | Design        |
| `brainstorming`                  | Workflow      |
| `building-accessible-interfaces` | Design        |
| `building-mcp-servers`           | Development   |
| `building-web-artifacts`         | Development   |
| `coauthoring-docs`               | Documents     |
| `configuring-opencode`           | Configuration |
| `creating-algorithmic-art`       | Design        |
| `creating-skills`                | Development   |
| `creating-slack-gifs`            | Design        |
| `designing-canvas-art`           | Design        |
| `designing-frontend-interfaces`  | Design        |
| `designing-user-experience`      | Design        |
| `dispatching-parallel-agents`    | Workflow      |
| `evolving-apis-and-schemas`      | Development   |
| `executing-plans`                | Workflow      |
| `finishing-a-development-branch` | Workflow      |
| `investigating-performance`      | Development   |
| `processing-pdf`                 | Documents     |
| `receiving-code-review`          | Workflow      |
| `requesting-code-review`         | Workflow      |
| `reviewing-interface-quality`    | Design        |
| `reviewing-security`             | Development   |
| `subagent-driven-development`    | Workflow      |
| `systematic-debugging`           | Development   |
| `test-driven-development`        | Development   |
| `testing-webapps`                | Development   |
| `using-git-worktrees`            | Workflow      |
| `using-superpowers`              | Workflow      |
| `verifying-before-completion`    | Workflow      |
| `writing-internal-comms`         | Documents     |
| `writing-plans`                  | Workflow      |
| `writing-release-notes`          | Documents     |
 
