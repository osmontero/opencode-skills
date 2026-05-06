# opencode-skills

Adapted skills and agents for the opencode agent ecosystem.

## Contents

**27 skills** covering development workflows, document generation, code review, testing, debugging, design, and more.

**8 global agents** for implementation, review, and evaluation.

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

| Agent | Purpose |
|-------|---------|
| `implementer` | Executes plan tasks with TDD, self-review, status reporting |
| `spec-reviewer` | Verifies implementation matches spec (nothing more, nothing less) |
| `code-quality-reviewer` | Code quality review after spec compliance passes |
| `code-reviewer` | General production-readiness code review |
| `grader` | Evaluates skill test expectations with pass/fail verdicts |
| `comparator` | Blind A/B comparison of skill outputs |
| `analyzer` | Post-hoc analysis + benchmark pattern detection |
| `internet-researcher` | Web research, fact-checking, and source gathering |

## Skills

| Skill | Category |
|-------|----------|
| `algorithmic-art` | Design |
| `brainstorming` | Workflow |
| `brand-guidelines` | Design |
| `canvas-design` | Design |
| `dispatching-parallel-agents` | Workflow |
| `doc-coauthoring` | Documents |
| `executing-plans` | Workflow |
| `finishing-a-development-branch` | Workflow |
| `frontend-design` | Design |
| `internal-comms` | Documents |
| `mcp-builder` | Development |
| `opencode-setup` | Configuration |
| `pdf` | Documents |
| `receiving-code-review` | Workflow |
| `requesting-code-review` | Workflow |
| `skill-creator` | Development |
| `slack-gif-creator` | Design |
| `subagent-driven-development` | Workflow |
| `systematic-debugging` | Development |
| `test-driven-development` | Development |
| `theme-factory` | Design |
| `using-git-worktrees` | Workflow |
| `using-superpowers` | Workflow |
| `verification-before-completion` | Workflow |
| `webapp-testing` | Development |
| `web-artifacts-builder` | Development |
| `writing-plans` | Workflow |
 
