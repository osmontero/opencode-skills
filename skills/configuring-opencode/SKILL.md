---
name: configuring-opencode
description: >
  Use when configuring opencode: providers, models, agents, skills, commands, permissions, themes, keybinds,
  LSP servers, MCP servers, formatters, and all runtime settings. Triggers include requests to set up opencode, configure a provider, add a model, create an agent, personalize
  opencode, set permissions, configure agents, change themes, add keybinds, set up rules, configure
  LSP or MCP servers, or anything related to opencode.json, tui.json, or opencode.jsonc
  configuration.
mode: subagent
permission:
  edit: deny
---

# OpenCode Setup and Configuration Guide

You are an opencode configuration expert. Help the user set up and personalize their opencode
installation by modifying the correct config files in the right locations.

**Official documentation:**
- Config schema: <https://opencode.ai/docs/config>
- TUI config: <https://opencode.ai/docs/tui>
- Agents: <https://opencode.ai/docs/agents>
- Skills: <https://opencode.ai/docs/skills>
- Commands: <https://opencode.ai/docs/commands>
- MCP servers: <https://opencode.ai/docs/mcp>
- Providers & models: <https://opencode.ai/docs/providers>
- Environment variables: <https://opencode.ai/docs/environment>
- JSON schema: `https://opencode.ai/config.json` / `https://opencode.ai/tui.json`

## Config Files and Locations

### JSON Config (`opencode.json` / `opencode.jsonc`)

Runtime/server settings. Two locations:

| Scope | Path |
|---|---|
| **Global** | `~/.config/opencode/opencode.json` |
| **Per-project** | `opencode.json` in project root |

Both `opencode.json` and `opencode.jsonc` are supported. JSONC allows comments and trailing
commas. In the same directory, `config.json`, `opencode.json`, then `opencode.jsonc` are loaded
in order (later overrides earlier).

Project config overrides global config. Both share the same schema. Add
`"$schema": "https://opencode.ai/config.json"` for IDE autocomplete (auto-added if missing).

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

Files are loaded from both locations -- project-level files override global
for same-named items.

## Precedence Order

Config is **merged**, not replaced. Layers from lowest to highest priority:

1. Remote config (`.well-known/opencode` organizational defaults)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var)
4. Project config (`opencode.json` in project)
5. `.opencode` directory config (`.opencode/opencode.json` or `.opencode/opencode.jsonc`)
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
7. Managed settings (`/Library/Application Support/opencode/` on macOS)
8. macOS MDM managed preferences (highest, not user-overridable)

### Deprecated Config Fields

These still work but will be removed in a future version:

| Field | Replacement |
|---|---|
| `mode` (top-level) | Use `agent` field instead |
| `autoshare` | Use `share` field instead |
| `layout` | Always uses stretch layout now |
| `agent.*.tools` | Use `permission` field instead |
| `agent.*.maxSteps` | Use `steps` field instead |

## Configuration Sections

### Provider and Model

```json
{
  "model": "provider/model-id",
  "small_model": "provider/cheaper-model",
  "provider": {
    "provider-name": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Display Name",
      "env": ["PROVIDER_API_KEY"],
      "whitelist": ["model-a"],
      "blacklist": ["model-b"],
      "options": {
        "baseURL": "https://custom-endpoint.com/v1",
        "timeout": 600000,
        "setCacheKey": false
      },
      "models": {
        "my-model": {
          "name": "My Model",
          "attachment": true,
          "reasoning": true,
          "tool_call": true,
          "limit": { "context": 128000, "input": 100000, "output": 32768 },
          "modalities": { "text": true, "image": true },
          "variants": {
            "thinking": {
              "options": { "thinking": { "type": "enabled", "budget_tokens": 8192 } }
            }
          },
          "options": { "temperature": 0.7, "topP": 0.95 }
        }
      }
    }
  }
}
```

`small_model` configures a cheaper model for lightweight tasks. If omitted, opencode picks one.

Provider fields: `npm` (NPM package), `name`, `api`, `env` (API key env vars), `id`,
`whitelist`, `blacklist`. `options.timeout` can be a number (ms) or `false` to disable
(default: 300000).

Model fields: `id`, `name`, `family`, `attachment`, `reasoning`,
`temperature`, `tool_call`, `interleaved`, `cost`, `limit`, `modalities`, `experimental`,
`status`, `options`, `headers`, `variants`.

`modalities` uses nested `input`/`output` arrays: `{ "input": ["text", "image"], "output": ["text"] }`.
`cost.context_over_200k` is a nested object with `input`, `output`, `cache_read`, `cache_write`.
`variants` and `options` accept arbitrary additional fields beyond those documented.

Full provider and model schemas in `{file:./reference.md}`.

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

**Important: insertion order matters.** opencode evaluates the LAST matching
rule, so put broad rules first and narrow rules last. For example, `"*": "ask"`
should come before specific `"git status *": "allow"` so the narrow rule wins.

`permission: "allow"` (a string at the top level) is shorthand for "allow
everything" and is rarely what you want.

Permission keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`,
`external_directory`, `todowrite`, `webfetch`, `websearch`, `lsp`, `skill`,
`question`, `doom_loop`, plus arbitrary custom keys for tools not listed.
`write` maps to `edit`. Some keys (`todowrite`, `question`, `webfetch`,
`websearch`, `doom_loop`) only accept a flat action, not a per-pattern object.

`external_directory` patterns are filesystem paths (use `~/`, absolute paths,
or globs like `~/secrets/**`).

Per-agent `permission:` overrides top-level `permission:`. Plan Mode lives on
the `plan` agent's permission ruleset (`edit: deny`).

### Agents (JSON)

```json
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "model": "provider/model-id",
      "variant": "thinking",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "permission": {
        "edit": "deny"
      },
      "color": "accent",
      "temperature": 0.1,
      "options": {
        "thinking": { "type": "enabled", "budget_tokens": 8192 }
      }
    }
  }
}
```

Agent fields: `description`, `mode` (`primary`/`subagent`/`all`), `model`,
`variant` (model variant like `"thinking"`), `prompt`, `permission`, `color`,
`temperature`, `top_p`, `steps` (max iterations), `hidden`, `disable`,
`options` (arbitrary model options).

`color` accepts theme color names (`"primary"`, `"secondary"`, `"accent"`,
`"success"`, `"warning"`, `"error"`, `"info"`) or any hex code (`"#FF5733"`).

Deprecated: `tools` (use `permission` instead), `maxSteps` (use `steps` instead).

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
name: my-agent          # explicit name override (optional, defaults to filename)
description: What this agent does (required)
mode: subagent
permission:
  edit: deny
variant: thinking
options:
  thinking:
    type: enabled
    budget_tokens: 8192
---
System prompt content here. Instructions this agent follows.
```

The file name (without `.md`) becomes the agent name unless `name` is set.

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

File-based: Create at `~/.config/opencode/skills/<name>/SKILL.md`:

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

JSON config for additional skill paths and remote skills:

```json
{
  "skills": {
    "paths": ["/absolute/path/to/skills", "~/my-skills"],
    "urls": ["https://example.com/.well-known/skills/"]
  }
}
```

**External skills auto-loading:** opencode also auto-discovers skills from
`~/.claude/skills/<name>/SKILL.md` and `~/.agents/skills/<name>/SKILL.md`.
Set `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` or `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`
to skip these scans.

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
    },
    "review": {
      "template": "Review the changes in $ARGUMENTS.",
      "description": "Review code changes",
      "model": "anthropic/claude-sonnet-4-20250514",
      "subtask": true
    }
  }
}
```

Command fields: `template` (required), `description`, `model` (specific model for this command),
`subtask` (run as subtask), `agent` (specific agent for this command).

### Commands (Markdown)

Create at `~/.config/opencode/commands/<name>.md`.

### References

References make local directories and Git repositories outside the active
project available as supporting context. Configure them under `references`,
keyed by the alias used in `@` autocomplete:

```json
{
  "references": {
    "docs": {
      "path": "../product-docs",
      "description": "Use for product behavior and terminology"
    },
    "effect": {
      "repository": "Effect-TS/effect",
      "branch": "main",
      "description": "Use for Effect implementation details"
    }
  }
}
```

Local `path` values may be relative to the declaring config, absolute, or use
`~/`. Git `repository` values accept Git URLs, host/path references, and GitHub
`owner/repo` shorthand; `branch` is optional. Both forms support optional
`description` and `hidden` fields.

- Only references with a `description` are advertised to agents in system context.
- `hidden: true` removes a reference from TUI `@` autocomplete only. It remains
  available to agents and by direct path.
- Reference directories are automatically allowed through the external-directory
  boundary; normal read/edit/tool permissions still apply.
- String shorthand is supported: `"docs": "../docs"` for local paths or
  `"effect": "Effect-TS/effect"` for Git repositories.

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

Customize in `tui.json`. Run `opencode keybinds` in TUI to see all 70+ defaults. Structure:

```json
{
  "keybinds": {
    "app_exit": "ctrl-c",
    "session_new": "ctrl-n",
    "model_list": "ctrl-m"
  }
}
```

Full keybinds list organized by category (app, session, messages, model, agent, input,
terminal) in `{file:./reference.md}`.

### TUI Configuration

Beyond `theme` and `keybinds`, `tui.json` supports:

| Field | Type | Description |
|---|---|---|
| `scroll_speed` | number | Scroll speed multiplier (default: 1) |
| `scroll_acceleration` | `{ enabled: boolean }` | Enable scroll acceleration |
| `diff_style` | `"auto"` \| `"stacked"` | Control diff rendering style |
| `mouse` | boolean | Enable/disable mouse capture (default: true) |
| `plugin` | array | TUI-specific plugins |
| `plugin_enabled` | Record\<string, boolean\> | Enable/disable TUI plugins by name |

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

### Log Level

Controls internal logging verbosity:

```json
{ "logLevel": "DEBUG" }
```

Values: `"DEBUG"`, `"INFO"`, `"WARN"`, `"ERROR"`.

### Username

Custom display name in conversations (defaults to system username):

```json
{ "username": "Osmany" }
```

### Tool Output Truncation

Control when tool output is truncated (defaults: 2000 lines, 51200 bytes):

```json
{
  "tool_output": { "max_lines": 2000, "max_bytes": 51200 }
}
```

### Experimental Features

```json
{
  "experimental": {
    "disable_paste_summary": false,
    "batch_tool": false,
    "openTelemetry": false,
    "primary_tools": [],
    "continue_loop_on_deny": false,
    "mcp_timeout": 10000
  }
}
```

Set `OPENCODE_EXPERIMENTAL` env var to enable all at once.

### Enterprise

```json
{ "enterprise": { "url": "https://enterprise.example.com" } }
```

### Shell

```json
{ "shell": "pwsh" }
```

### Snapshot

Disable to improve performance on large repos:

```json
{ "snapshot": false }
```

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
    "reserved": 10000,
    "tail_turns": 2,
    "preserve_recent_tokens": 0
  }
}
```

`reserved` = token buffer. `tail_turns` = recent turns kept verbatim.

### File Watcher Ignore

```json
{ "watcher": { "ignore": ["node_modules/**", "dist/**", ".git/**"] } }
```

### Disabled / Enabled Providers

```json
{
  "disabled_providers": ["openai", "gemini"],
  "enabled_providers": ["anthropic", "openai"]
}
```

`disabled_providers` takes priority.

### Formatters

```json
{
  "formatter": {
    "prettier": { "disabled": true },
    "custom-prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "extensions": [".js", ".ts", ".jsx", ".tsx"],
      "environment": { "PRETTIER_CONFIG": "~/.prettierrc" }
    }
  }
}
```

### LSP Servers

Set `lsp: true` to enable all built-in LSP servers, `lsp: false` to disable all,
or configure per-server:

```json
{
  "lsp": {
    "typescript": { "disabled": true },
    "gopls": {
      "command": ["gopls"],
      "extensions": [".go"],
      "env": { "GOPROXY": "https://proxy.golang.org" },
      "initialization": { "completion": { "resolveProvider": true } }
    }
  }
}
```

Per-server fields: `disabled`, `command`, `extensions` (required for custom servers),
`env` (environment variables), `initialization` (LSP initialization options).

30 built-in LSP servers are available. Full list in `{file:./reference.md}`.

### MCP Servers

Local MCP (stdio) and remote MCP (HTTP/SSE):

```json
{
  "mcp": {
    "local-tool": {
      "enabled": true,
      "type": "local",
      "command": ["npx", "-y", "@brave/brave-search-mcp-server"],
      "environment": { "BRAVE_API_KEY": "{env:BRAVE_API_KEY}" },
      "timeout": 10000
    },
    "remote-tool": {
      "enabled": true,
      "type": "remote",
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer {env:MCP_TOKEN}" },
      "oauth": { "clientId": "my-client", "clientSecret": "{env:MCP_SECRET}", "scope": "read write", "redirectUri": "http://127.0.0.1:19876/mcp/oauth/callback" },
      "timeout": 10000
    }
  }
}
```

Set `oauth: false` to disable OAuth auto-detection. Legacy `{ "enabled": false }` form
also supported to disable a server.

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

`{env:VARIABLE}` — substitute environment variable.
`{file:path}` — substitute file contents (relative to config directory, or absolute
with `/` or `~`).

Many runtime behaviors can be controlled via environment variables. Full list (30+)
in `{file:./reference.md}`. Common ones:

| Variable | Purpose |
|---|---|
| `OPENCODE_CONFIG` | Path to custom config file |
| `OPENCODE_CONFIG_CONTENT` | Inline JSON config content |
| `OPENCODE_CONFIG_DIR` | Custom config directory |
| `OPENCODE_DISABLE_LSP_DOWNLOAD` | Prevent auto-downloading LSP servers |
| `OPENCODE_DISABLE_AUTOUPDATE` | Disable auto-update checks |
| `OPENCODE_EXPERIMENTAL` | Enable all experimental features |
| `OPENCODE_SERVER_PASSWORD` | Web UI password |

### Escape Hatches for Broken Config

When a config error prevents opencode from starting, use these env vars to
recover:

| Variable | Purpose |
|---|---|
| `OPENCODE_DISABLE_PROJECT_CONFIG=1` | Skip the project's local `opencode.json`; start from globals only. Use this to load opencode, fix the broken file, then restart without the flag |
| `OPENCODE_CONFIG=/path/to/file.json` | Load an additional explicit config file |
| `OPENCODE_CONFIG_CONTENT='{"$schema":"..."}'` | Inject inline JSON as a final local-scope merge |
| `OPENCODE_DISABLE_DEFAULT_PLUGINS=1` | Skip default plugins |
| `OPENCODE_PURE=1` | Skip external plugins entirely |
| `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` | Skip external skill scans under `~/.claude/` and `~/.agents/` |
| `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` | Skip only the `~/.claude/` skill scan |

### Shell

```json
{
  "shell": "pwsh"
}
```

### Plugins

```json
{
  "plugin": [
    "opencode-helicone-session",
    ["@my-org/custom-plugin", { "apiKey": "{env:PLUGIN_KEY}" }]
  ]
}
```

Plugins can be simple strings or `[name, config]` tuples. Place local plugins in
`.opencode/plugins/` or `~/.config/opencode/plugins/` for auto-discovery (any
`*.ts` or `*.js` file is loaded automatically).

Plugin entries support:

```json
"plugin": [
  "opencode-gemini-auth",            // npm spec, latest
  "opencode-foo@1.2.3",              // npm spec, pinned
  "./local-plugin.ts",               // file path, relative to the declaring config
  "file:///abs/path/plugin.js",      // file URL
  ["opencode-bar", { "key": "val" }] // tuple form with options
]
```

A plugin module exports a function of type
`Plugin = (input: PluginInput, options?) => Promise<Hooks>`. The export is a
function (not a plain object), returning a hooks object (return `{}` if nothing
to register):

```ts
import type { Plugin } from "@opencode-ai/plugin"

export default (async ({ client, project, directory, $ }) => {
  return {
    config: (cfg) => {
      // cfg is the live merged config; mutate fields here.
    },
    "tool.execute.before": async (input, output) => {
      // mutate output.args before the tool runs
    },
  }
}) satisfies Plugin
```

**Available hooks** (mutate `output` in place; return `void`):

| Hook | Fires |
|---|---|
| `event(input)` | Every bus event |
| `config(cfg)` | Once on init with the merged config |
| `chat.message` | Before each chat message is sent |
| `chat.params` | Before chat params are built |
| `chat.headers` | Before chat HTTP headers are set |
| `tool.execute.before` | Before a tool runs |
| `tool.execute.after` | After a tool runs |
| `tool.definition` | When tool definitions are built |
| `command.execute.before` | Before a command runs |
| `shell.env` | Before shell environment is built |
| `permission.ask` | When permission prompt is shown |
| `experimental.chat.messages.transform` | Transform messages before sending |
| `experimental.chat.system.transform` | Transform system prompt |
| `experimental.session.compacting` | During session compaction |
| `experimental.compaction.autocontinue` | After auto-continue compaction |
| `experimental.text.complete` | During text completion |

Special object-shaped hooks (not callbacks): `tool: { my_tool: { ... } }`,
`auth: { ... }`, `provider: { ... }`.

**Note:** Plugins are TypeScript or JavaScript only — no Go or compiled binary
support. If you need Go, write an MCP server in Go and have a thin TS plugin
call it via HTTP.

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

| Command | Action |
|---|---|
| `/connect` | Add a provider and enter API keys |
| `/models` | List and select available models |
| `/init` | Create project AGENTS.md |
| `/share` | Share current session |
| `/undo` / `/redo` | Undo/redo last change |
| `Tab` | Switch between Build and Plan |
| `@name` | Mention a subagent to invoke it |

CLI: `opencode agent create`, `opencode debug config`, `opencode models`, `opencode keybinds`.

## Tips

- **Config is not hot-reloaded.** After saving changes to `opencode.json`, an
  agent file, a skill, a plugin, or any other config-time file, tell the user to
  quit and restart opencode for changes to take effect. The running session keeps
  using the already-loaded config until then.
- Config files are **merged** across locations, not replaced
- Use `opencode debug config` to see the fully resolved configuration
- Agent file name becomes agent name for markdown agents
- `hidden: true` on subagents hides them from `@` autocomplete but they can
  still be invoked via Task tool
- Provider `baseURL` and model `limit.context` are often needed for custom
  and local providers
- Use `opencode.jsonc` for configs with comments and trailing commas
- Run `opencode keybinds` to see all 70+ customizable keybinds
- Use `{file:./reference.md}` for complete LSP servers, keybinds, env vars,
  and model/provider schemas
- For latest info, always check the official docs at <https://opencode.ai/docs>
