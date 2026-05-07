# opencode-skills

Adapted skills and agents for the opencode agent ecosystem.

## Contents

**26 skills** covering development workflows, document generation, code review, testing, debugging, design, and more.

**8 global agents** for implementation, review, and evaluation.

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

See individual `skills/<name>/LICENSE.txt` files for full license text and attribution notices.

## Examples

### ThreatWinds Vision MCP Server

A [FastMCP](https://github.com/modelcontextprotocol/python-sdk) server that analyzes scanned PDFs and images through the [ThreatWinds AI API](https://threatwinds.com). Supports arbitrary extraction prompts and three input modes: local file paths, remote URLs, and base64 payloads.

See [`mcp_servers/threatwinds_vision/README.md`](mcp_servers/threatwinds_vision/README.md) for setup and usage.

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
| `applying-themes`                | Design        |
| `brainstorming`                  | Workflow      |
| `building-mcp-servers`           | Development   |
| `building-web-artifacts`         | Development   |
| `coauthoring-docs`               | Documents     |
| `configuring-opencode`           | Configuration |
| `creating-algorithmic-art`       | Design        |
| `creating-skills`                | Development   |
| `creating-slack-gifs`            | Design        |
| `designing-canvas-art`           | Design        |
| `designing-frontend-interfaces`  | Design        |
| `dispatching-parallel-agents`    | Workflow      |
| `executing-plans`                | Workflow      |
| `finishing-a-development-branch` | Workflow      |
| `processing-pdf`                 | Documents     |
| `receiving-code-review`          | Workflow      |
| `requesting-code-review`         | Workflow      |
| `subagent-driven-development`    | Workflow      |
| `systematic-debugging`           | Development   |
| `test-driven-development`        | Development   |
| `testing-webapps`                | Development   |
| `using-git-worktrees`            | Workflow      |
| `using-superpowers`              | Workflow      |
| `verifying-before-completion`    | Workflow      |
| `writing-internal-comms`         | Documents     |
| `writing-plans`                  | Workflow      |
 
