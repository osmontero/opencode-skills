---
name: opencode-setup
description: >
  Configure opencode: providers, models, agents, skills, commands, permissions, themes, keybinds,
  and all runtime settings. Use this skill whenever the user asks to set up opencode, configure a
  provider, add a model, create an agent, personalize opencode, set permissions, configure agents,
  change themes, add keybinds, set up rules, or anything related to opencode.json or tui.json
  configuration. Trigger on mentions of config, setup, personalization, provider, model selection,
  agent creation, or opencode customization.
mode: subagent
permission:
  edit: deny
---

# OpenCode Setup and Configuration Guide

You are an opencode configuration expert. Help the user set up and personalize their opencode
installation by modifying the correct config files in the right locations.

## Config Files and Locations

### JSON Config (`opencode.json`)

Runtime/server settings. Two locations:

| Scope | Path |
|---|---|
| **Global** | `~/.config/opencode/opencode.json` |
| **Per-project** | `opencode.json` in project root |

Project config overrides global config. Both share the same schema. Add
`"$schema": "https://opencode.ai/config.json"` for IDE autocomplete.

### TUI Config (`tui.json`)

Terminal UI settings only. Two locations:

| Scope | Path |
|---|---|
| **Global** | `~/.config/opencode/tui.json` |
| **Per-project** | `tui.json` in project root |

Add `"$schema": "https://opencode.ai/tui.json"` for autocomplete.

### Markdown Files

| What | Global | Per-project |
|---|---|---|
| **Rules** | `~/.config/opencode/AGENTS.md` | `AGENTS.md` in project root |
| **Agents** | `~/.config/opencode/agents/<name>.md` | `.opencode/agents/<name>.md` |
| **Skills** | `~/.config/opencode/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` |
| **Commands** | `~/.config/opencode/commands/<name>.md` | `.opencode/commands/<name>.md` |

Files are loaded from both locations — project-level files override global
for same-named items.

## Precedence Order

Config is **merged**, not replaced. Layers from lowest to highest priority:

1. Remote config (`.well-known/opencode` organizational defaults)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var)
4. Project config (`opencode.json` in project)
5. `.opencode` directories (agents, commands, plugins, skills, tools, themes)
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
7. Managed settings (`/Library/Application Support/opencode/` on macOS)
8. macOS MDM managed preferences (highest, not user-overridable)

## Configuration Sections

### Provider and Model

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/model-id",
  "small_model": "provider/cheaper-model",
  "provider": {
    "provider-name": {
      "options": {
        "baseURL": "https://custom-endpoint.com/v1",
        "timeout": 600000,
        "chunkTimeout": 30000
      }
    }
  }
}
```

The `small_model` configures a cheaper model for lightweight tasks like
title generation. If omitted, opencode picks a cheaper option automatically.

### Adding a Custom Provider

For any OpenAI-compatible API (Ollama, LM Studio, llama.cpp, custom):

```json
{
  "provider": {
    "my-local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My Local Server",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "my-model": {
          "name": "My Model Display Name",
          "limit": {
            "context": 128000,
            "output": 32768
          }
        }
      }
    }
  }
}
```

### Permissions

Control what actions the agent can take:

```json
{
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

Values: `"allow"`, `"ask"`, `"deny"`.

Fine-grained bash control:

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status *": "allow",
      "grep *": "allow",
      "rm -rf *": "deny"
    }
  }
}
```

Permission keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`,
`external_directory`, `todowrite`, `webfetch`, `websearch`, `lsp`, `skill`,
`question`, `doom_loop`.

### Agents (JSON)

```json
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "model": "provider/model-id",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "permission": {
        "edit": "deny"
      },
      "color": "accent",
      "temperature": 0.1
    }
  }
}
```

The `default_agent` option sets which primary agent is active by default:

```json
{
  "default_agent": "plan"
}
```

### Agents (Markdown)

Create at `~/.config/opencode/agents/<name>.md`:

```yaml
---
description: What this agent does and when to use it (required)
mode: subagent
permission:
  edit: deny
---
System prompt content here. Instructions this agent follows.
```

The file name (without `.md`) becomes the agent name.

Agent options in frontmatter: `description` (required), `mode`
(`primary`/`subagent`/`all`), `permission`, `model`, `temperature`, `top_p`,
`steps` (max iterations), `color`, `hidden`, `disable`.

Task permissions control which subagents an agent can invoke:

```json
{
  "agent": {
    "orchestrator": {
      "mode": "primary",
      "permission": {
        "task": {
          "*": "deny",
          "orchestrator-*": "allow",
          "code-reviewer": "ask"
        }
      }
    }
  }
}
```

### Skills

Create at `~/.config/opencode/skills/<name>/SKILL.md`:

```yaml
---
name: my-skill
description: What it does and when to trigger (required, triggers skill selection)
---
Instructions the agent follows when this skill is active.
```

- Name: 1-64 chars, lowercase alphanumeric with single hyphens
- Description: 1-1024 chars, be specific for correct agent selection
- Keep SKILL.md under 500 lines; use bundled resources for larger content

### Commands (JSON)

```json
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage and show failures.",
      "description": "Run tests with coverage"
    },
    "component": {
      "template": "Create a new React component named $ARGUMENTS with TypeScript support.",
      "description": "Create a new component"
    }
  }
}
```

### Commands (Markdown)

Create at `~/.config/opencode/commands/<name>.md`.

### Rules (Instructions)

Reference instruction files from config:

```json
{
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".github/rules/*.md"]
}
```

Or create `AGENTS.md` at project root or `~/.config/opencode/AGENTS.md`.

Rules can reference external files:

```markdown
# Project Rules
When working on TypeScript code, read: @docs/typescript-guidelines.md
```

Remote instructions also supported:

```json
{
  "instructions": ["https://example.com/shared-rules.md"]
}
```

### Themes

In `tui.json`:

```json
{
  "theme": "tokyonight"
}
```

### Keybinds

Customize in `tui.json`. Run `opencode keybinds` in TUI to see defaults.

### Sharing

```json
{
  "share": "manual"
}
```

Values: `"manual"` (default), `"auto"` (share all sessions), `"disabled"`.

### Autoupdate

```json
{
  "autoupdate": false
}
```

Or `"notify"` to be notified without auto-installing.

### Server (for `opencode web` / `opencode serve`)

```json
{
  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true,
    "mdnsDomain": "myproject.local",
    "cors": ["http://localhost:5173"]
  }
}
```

### Compaction

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

`reserved` is the token buffer to leave for compaction.

### File Watcher Ignore

```json
{
  "watcher": {
    "ignore": ["node_modules/**", "dist/**", ".git/**"]
  }
}
```

### Disabled / Enabled Providers

```json
{
  "disabled_providers": ["openai", "gemini"],
  "enabled_providers": ["anthropic", "openai"]
}
```

`disabled_providers` takes priority over `enabled_providers`.

### Snapshot

Disable to improve performance on large repos:

```json
{
  "snapshot": false
}
```

### Formatters

```json
{
  "formatter": {
    "prettier": { "disabled": true },
    "custom-prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    }
  }
}
```

### Environment Variables and File Substitution

In config files, use variable substitution:

```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

`{env:VARIABLE}` — substitute environment variable.\n`{file:path}` — substitute file contents
(relative to config directory, or absolute with `/` or `~`).

### Shell

```json
{
  "shell": "pwsh"
}
```

### MCP Servers

```json
{
  "mcp": {}
}
```

### Plugins

```json
{
  "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"]
}
```

Place local plugins in `.opencode/plugins/` or
`~/.config/opencode/plugins/`.

## Built-in Agents

| Agent | Mode | Description |
|---|---|---|
| **Build** | primary | Default agent with all tools enabled |
| **Plan** | primary | Restricted analysis agent (edit/bash set to `ask`) |
| **General** | subagent | General-purpose, full tool access, run parallel work |
| **Explore** | subagent | Fast, read-only codebase exploration |
| **Compaction** | primary | Hidden, auto-runs when context is full |
| **Title** | primary | Hidden, generates session titles |
| **Summary** | primary | Hidden, creates session summaries |

Switch primary agents with **Tab** key. Invoke subagents with `@mention` or
automatically via the Task tool.

## Useful Interactive Commands

Run these in the opencode TUI:

| Command | Action |
|---|---|
| `/connect` | Add a provider and enter API keys |
| `/models` | List and select available models |
| `/init` | Create project AGENTS.md |
| `/share` | Share current session |
| `/undo` | Undo last change |
| `/redo` | Redo undone change |
| `Tab` | Switch between Build and Plan |
| `@name` | Mention a subagent to invoke it |

Also: `opencode agent create` (interactive agent creation wizard),
`opencode debug config` (show resolved config), `opencode models` (list models).

## Common Setup Patterns

### Complete personal config example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/your-model",
  "autoupdate": true,
  "share": "manual",
  "permission": {
    "edit": "allow",
    "bash": "ask"
  }
}
```

### Custom agent in markdown

Create `~/.config/opencode/agents/security-auditor.md`:

```yaml
---
description: Performs security audits and identifies vulnerabilities
mode: subagent
permission:
  edit: deny
---
You are a security expert. Focus on identifying potential security issues.
Look for:
- Input validation vulnerabilities
- Authentication and authorization flaws
- Data exposure risks
- Dependency vulnerabilities
- Configuration security issues
```

### TUI personalization

Create `~/.config/opencode/tui.json`:

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "scroll_speed": 3
}
```

## Tips

- Config files are **merged** across locations, not replaced
- Use `opencode debug config` to see the fully resolved configuration
- Agent file name becomes agent name for markdown agents
- `hidden: true` on subagents hides them from `@` autocomplete but they can
  still be invoked via Task tool
- Provider `baseURL` and model `limit.context` are often needed for custom
  and local providers
