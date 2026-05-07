# opencode-skills

Adapted skills and agents for the opencode agent ecosystem.

## Contents

**27 skills** covering development workflows, document generation, code review, testing, debugging, design, and more.

**8 global agents** for implementation, review, and evaluation.

## License

This repository is licensed under **MIT** (see [LICENSE](LICENSE)).

### Third-Party Licenses and Attributions

Some skills and components incorporate work from other sources under different licenses:

#### Apache License 2.0 (Anthropic, PBC)

The following skills are licensed under Apache 2.0 and adapted from Anthropic's Claude projects:

- `algorithmic-art` — Generative art creation with p5.js
- `brand-guidelines` — Brand color and typography application
- `canvas-design` — Visual design for static documents
- `doc-coauthoring` — Structured documentation collaboration workflow
- `internal-comms` — Internal communications templates and guidance
- `mcp-builder` — Model Context Protocol server development
- `skill-creator` — Skill development, testing, and benchmarking lifecycle
- `slack-gif-creator` — Animated GIF creation for Slack
- `theme-factory` — Thematic styling for artifacts and documents
- `web-artifacts-builder` — Multi-component HTML artifact creation
- `webapp-testing` — Playwright-based web application testing

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
- `verification-before-completion` — Pre-commit verification and evidence gathering
- `writing-plans` — Implementation plan creation from specs

See individual `skills/<name>/LICENSE.txt` files for full license text and attribution notices.

## Examples

### ThreatWinds Vision MCP Server

A [FastMCP](https://github.com/modelcontextprotocol/python-sdk) server that analyzes scanned PDFs and images through the [ThreatWinds AI API](https://threatwinds.com). Supports arbitrary extraction prompts and three input modes: local file paths, remote URLs, and base64 payloads.

See [`skills/mcp_builder/examples/threatwinds_vision_mcp/README.md`](skills/mcp_builder/examples/threatwinds_vision_mcp/README.md) for setup and usage.

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
| `grader`                | Evaluates skill test expectations with pass/fail verdicts         |
| `comparator`            | Blind A/B comparison of skill outputs                             |
| `analyzer`              | Post-hoc analysis + benchmark pattern detection                   |
| `internet-researcher`   | Web research, fact-checking, and source gathering                 |

## Skills

| Skill                            | Category      |
|----------------------------------|---------------|
| `algorithmic-art`                | Design        |
| `brainstorming`                  | Workflow      |
| `brand-guidelines`               | Design        |
| `canvas-design`                  | Design        |
| `dispatching-parallel-agents`    | Workflow      |
| `doc-coauthoring`                | Documents     |
| `executing-plans`                | Workflow      |
| `finishing-a-development-branch` | Workflow      |
| `frontend-design`                | Design        |
| `internal-comms`                 | Documents     |
| `mcp-builder`                    | Development   |
| `opencode-setup`                 | Configuration |
| `pdf`                            | Documents     |
| `receiving-code-review`          | Workflow      |
| `requesting-code-review`         | Workflow      |
| `skill-creator`                  | Development   |
| `slack-gif-creator`              | Design        |
| `subagent-driven-development`    | Workflow      |
| `systematic-debugging`           | Development   |
| `test-driven-development`        | Development   |
| `theme-factory`                  | Design        |
| `using-git-worktrees`            | Workflow      |
| `using-superpowers`              | Workflow      |
| `verification-before-completion` | Workflow      |
| `webapp-testing`                 | Development   |
| `web-artifacts-builder`          | Development   |
| `writing-plans`                  | Workflow      |
 
