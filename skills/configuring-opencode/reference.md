# OpenCode Configuration Reference

Bundled reference for the configuring-opencode skill. Contains complete tables and schemas
that are too large for the main SKILL.md.

## Built-in LSP Servers

Set `lsp: true` to enable all, `lsp: false` to disable all, or configure per-server:

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

| ID | Language | File Extensions |
|---|---|---|
| `deno` | Deno | .ts, .tsx, .js, .jsx, .mjs |
| `typescript` | TypeScript | .ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts |
| `vue` | Vue | .vue |
| `eslint` | ESLint | .ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue |
| `oxlint` | Oxlint | .ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue, .astro, .svelte |
| `biome` | Biome | .ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .json, .jsonc, .vue, .astro, .svelte, .css, .graphql, .gql, .html |
| `gopls` | Go | .go |
| `ruby-lsp` | Ruby | .rb, .rake, .gemspec, .ru |
| `ty` | Python (experimental) | .py, .pyi |
| `pyright` | Python | .py, .pyi |
| `elixir-ls` | Elixir | .ex, .exs |
| `zls` | Zig | .zig, .zon |
| `csharp` | C# | .cs, .csx |
| `razor` | Razor | .razor, .cshtml |
| `fsharp` | F# | .fs, .fsi, .fsx, .fsscript |
| `sourcekit-lsp` | Swift/Objective-C | .swift, .objc, objcpp |
| `rust` | Rust | .rs |
| `clangd` | C/C++ | .c, .cpp, .cc, .cxx, .c++, .h, .hpp, .hh, .hxx, .h++ |
| `svelte` | Svelte | .svelte |
| `astro` | Astro | .astro |
| `jdtls` | Java | .java |
| `kotlin-ls` | Kotlin | .kt, .kts |
| `yaml-ls` | YAML | .yaml, .yml |
| `lua-ls` | Lua | .lua |
| `php intelephense` | PHP | .php |
| `prisma` | Prisma | .prisma |
| `dart` | Dart | .dart |
| `ocaml-lsp` | OCaml | .ml, .mli |
| `bash` | Bash | .sh, .bash, .zsh, .ksh |
| `terraform` | Terraform | .tf, .tfvars |
| `texlab` | LaTeX | .tex, .bib |
| `dockerfile` | Dockerfile | .dockerfile, Dockerfile |
| `gleam` | Gleam | .gleam |
| `clojure-lsp` | Clojure | .clj, .cljs, .cljc, .edn |
| `nixd` | Nix | .nix |
| `tinymist` | Typst | .typ, .typc |
| `haskell-language-server` | Haskell | .hs, .lhs |
| `julials` | Julia | .jl |

## Keybinds

Customize in `tui.json`. Run `opencode keybinds` to see current bindings. Structure:

```json
{
  "keybinds": {
    "app_exit": "ctrl-c",
    "session_new": "ctrl-n",
    "model_list": "ctrl-m"
  }
}
```

### App

| Keybind | Action |
|---|---|
| `leader` | Leader key (default: `ctrl+x`) |
| `app_exit` | Exit application |
| `editor_open` | Open external editor |
| `theme_list` | List available themes |
| `sidebar_toggle` | Toggle sidebar |
| `scrollbar_toggle` | Toggle scrollbar |
| `username_toggle` | Toggle username display |
| `status_view` | Show status view |
| `tips_toggle` | Toggle tips on home screen |
| `plugin_manager` | Open plugin manager |
| `display_thinking` | Toggle thinking display |

### Session

| Keybind | Action |
|---|---|
| `session_export` | Export session |
| `session_new` | New session |
| `session_list` | List sessions |
| `session_timeline` | View session timeline |
| `session_fork` | Fork session from message |
| `session_rename` | Rename session |
| `session_delete` | Delete session |
| `session_share` | Share session (default: none) |
| `session_unshare` | Unshare session (default: none) |
| `session_interrupt` | Interrupt current generation |
| `session_compact` | Compact session manually |
| `session_child_first` | Jump to first child session |
| `session_child_cycle` | Cycle to next child session |
| `session_child_cycle_reverse` | Cycle to previous child session |
| `session_parent` | Return to parent session |
| `stash_delete` | Delete stash entry |

### Messages

| Keybind | Action |
|---|---|
| `messages_page_up` | Page up in messages |
| `messages_page_down` | Page down in messages |
| `messages_line_up` | Scroll up one line |
| `messages_line_down` | Scroll down one line |
| `messages_half_page_up` | Scroll up half page |
| `messages_half_page_down` | Scroll down half page |
| `messages_first` | Jump to first message |
| `messages_last` | Jump to last message |
| `messages_next` | Next message |
| `messages_previous` | Previous message |
| `messages_last_user` | Jump to last user message |
| `messages_copy` | Copy message content |
| `messages_undo` | Undo last message change |
| `messages_redo` | Redo undone message change |
| `messages_toggle_conceal` | Toggle concealing message |

### Tools

| Keybind | Action |
|---|---|
| `tool_details` | Toggle tool details visibility |

### Model

| Keybind | Action |
|---|---|
| `model_list` | List available models |
| `model_cycle_recent` | Cycle to next recent model |
| `model_cycle_recent_reverse` | Cycle to previous recent model |
| `model_cycle_favorite` | Cycle to next favorite model |
| `model_cycle_favorite_reverse` | Cycle to previous favorite model |
| `model_provider_list` | Open provider list from model dialog |
| `model_favorite_toggle` | Toggle model favorite status |
| `variant_cycle` | Cycle model variants |
| `variant_list` | List model variants |

### Agent / Command

| Keybind | Action |
|---|---|
| `command_list` | List available commands |
| `agent_list` | List available agents |
| `agent_cycle` | Cycle to next agent |
| `agent_cycle_reverse` | Cycle to previous agent |

### Input

| Keybind | Action |
|---|---|
| `input_clear` | Clear input |
| `input_paste` | Paste into input |
| `input_submit` | Submit input |
| `input_newline` | Insert newline in input |
| `input_move_left` | Move cursor left |
| `input_move_right` | Move cursor right |
| `input_move_up` | Move cursor up |
| `input_move_down` | Move cursor down |
| `input_line_home` | Move to start of line |
| `input_line_end` | Move to end of line |
| `input_visual_line_home` | Move to start of visual line |
| `input_visual_line_end` | Move to end of visual line |
| `input_buffer_home` | Move to start of buffer |
| `input_buffer_end` | Move to end of buffer |
| `input_select_left` | Select left |
| `input_select_right` | Select right |
| `input_select_up` | Select up |
| `input_select_down` | Select down |
| `input_select_line_home` | Select to start of line |
| `input_select_line_end` | Select to end of line |
| `input_select_visual_line_home` | Select to start of visual line |
| `input_select_visual_line_end` | Select to end of visual line |
| `input_select_buffer_home` | Select to start of buffer |
| `input_select_buffer_end` | Select to end of buffer |
| `input_delete_line` | Delete line |
| `input_delete_to_line_start` | Delete to start of line |
| `input_delete_to_line_end` | Delete to end of line |
| `input_backspace` | Backspace |
| `input_delete` | Delete character |
| `input_delete_word_backward` | Delete previous word |
| `input_delete_word_forward` | Delete next word |
| `input_word_backward` | Move back one word |
| `input_word_forward` | Move forward one word |
| `input_select_word_backward` | Select word backward |
| `input_select_word_forward` | Select word forward |
| `history_previous` | Previous command in history |
| `history_next` | Next command in history |
| `input_undo` | Undo in input |
| `input_redo` | Redo in input |

### Terminal

| Keybind | Action |
|---|---|
| `terminal_suspend` | Suspend terminal |
| `terminal_title_toggle` | Toggle terminal title |

## Environment Variables

| Variable | Purpose |
|---|---|
| `OPENCODE_CONFIG` | Path to custom config file |
| `OPENCODE_CONFIG_CONTENT` | Inline JSON config content |
| `OPENCODE_CONFIG_DIR` | Custom config directory |
| `OPENCODE_TUI_CONFIG` | Custom TUI config file path |
| `OPENCODE_PERMISSION` | Inline JSON permission override |
| `OPENCODE_DISABLE_PROJECT_CONFIG` | Skip project-level config loading |
| `OPENCODE_DISABLE_AUTOUPDATE` | Disable auto-update checks |
| `OPENCODE_DISABLE_AUTOCOMPACT` | Disable automatic compaction |
| `OPENCODE_DISABLE_PRUNE` | Disable pruning of old tool outputs |
| `OPENCODE_DISABLE_LSP_DOWNLOAD` | Prevent auto-downloading LSP servers |
| `OPENCODE_DISABLE_MODELS_FETCH` | Skip fetching model list from models.dev |
| `OPENCODE_DISABLE_MOUSE` | Disable mouse support in TUI |
| `OPENCODE_DISABLE_EXTERNAL_SKILLS` | Disable loading external/remote skills |
| `OPENCODE_DISABLE_DEFAULT_PLUGINS` | Skip loading default plugins |
| `OPENCODE_EXPERIMENTAL` | Enable all experimental features |
| `OPENCODE_EXPERIMENTAL_FILEWATCHER` | Enable experimental file watcher |
| `OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER` | Disable file watcher |
| `OPENCODE_EXPERIMENTAL_LSP_TY` | Enable experimental Ty Python LSP |
| `OPENCODE_EXPERIMENTAL_LSP_TOOL` | Enable experimental LSP tool |
| `OPENCODE_EXPERIMENTAL_PLAN_MODE` | Enable experimental plan mode |
| `OPENCODE_EXPERIMENTAL_OXFMT` | Enable experimental oxfmt formatter |
| `OPENCODE_EXPERIMENTAL_HTTPAPI` | Enable new effect-httpapi server backend (on by default for dev/beta/local) |
| `OPENCODE_EXPERIMENTAL_WORKSPACES` | Enable experimental workspaces |
| `OPENCODE_EXPERIMENTAL_EVENT_SYSTEM` | Enable experimental event system |
| `OPENCODE_EXPERIMENTAL_ICON_DISCOVERY` | Enable icon discovery |
| `OPENCODE_EXPERIMENTAL_DISABLE_COPY_ON_SELECT` | Disable copy on select |
| `OPENCODE_EXPERIMENTAL_EXA` | Enable Exa web search (alternate flag) |
| `OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS` | Bash default timeout in ms |
| `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` | Output token max |
| `OPENCODE_EXPERIMENTAL_MARKDOWN` | Enable markdown experiments |
| `OPENCODE_AUTO_HEAP_SNAPSHOT` | Auto heap snapshot |
| `OPENCODE_GIT_BASH_PATH` | Git Bash path |
| `OPENCODE_ALWAYS_NOTIFY_UPDATE` | Always notify of updates |
| `OPENCODE_DISABLE_TERMINAL_TITLE` | Disable terminal title |
| `OPENCODE_ENABLE_EXPERIMENTAL_MODELS` | Enable experimental models |
| `OPENCODE_DISABLE_CLAUDE_CODE` | Disable Claude Code integration |
| `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` | Disable Claude Code prompt |
| `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` | Disable Claude Code skills |
| `OPENCODE_FAKE_VCS` | Fake VCS (testing) |
| `OPENCODE_DISABLE_EMBEDDED_WEB_UI` | Disable embedded web UI |
| `OPENCODE_DISABLE_CHANNEL_DB` | Disable channel DB |
| `OPENCODE_SKIP_MIGRATIONS` | Skip DB migrations |
| `OPENCODE_STRICT_CONFIG_DEPS` | Strict config deps |
| `OPENCODE_WORKSPACE_ID` | Workspace ID |
| `OPENCODE_PLUGIN_META_FILE` | Plugin meta file path |
| `OPENCODE_SERVER_PASSWORD` | Web UI password |
| `OPENCODE_SERVER_USERNAME` | Web UI username |
| `OPENCODE_MODELS_URL` | Custom models.dev URL |
| `OPENCODE_MODELS_PATH` | Custom models cache file path |
| `OPENCODE_DB` | Custom database path |
| `OPENCODE_PURE` | Pure mode (no side effects) |
| `OPENCODE_CLIENT` | Client identifier (default: "cli") |
| `OPENCODE_AUTO_SHARE` | Auto-share sessions |
| `OPENCODE_SHOW_TTFD` | Show time-to-first-delta metric |
| `OPENCODE_ENABLE_EXA` | Enable Exa web search |
| `OPENCODE_ENABLE_QUESTION_TOOL` | Enable question tool |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry endpoint |
| `OTEL_EXPORTER_OTLP_HEADERS` | OpenTelemetry headers |

## Model Capability Schema

Under `provider.<name>.models.<model-id>`:

| Field | Type | Description |
|---|---|---|
| `id` | string | Model ID override |
| `name` | string | Display name |
| `family` | string | Model family grouping |
| `release_date` | string | Release date |
| `attachment` | boolean | Supports file attachments |
| `reasoning` | boolean | Supports extended thinking/reasoning |
| `temperature` | boolean | Supports temperature control |
| `tool_call` | boolean | Supports tool calling |
| `interleaved` | boolean \| `{ field: string }` | Interleaved content support (reasoning_content or reasoning_details) |
| `cost` | object | Cost info: `input`, `output`, `cache_read`, `cache_write`, `context_over_200k` (nested object with same fields) |
| `limit` | object | Limits: `context`, `input` (optional), `output` |
| `modalities` | object | Nested `{ input: string[], output: string[] }` with values: `text`, `audio`, `image`, `video`, `pdf` |
| `experimental` | boolean | Mark as experimental |
| `status` | `"alpha"` \| `"beta"` \| `"deprecated"` | Model status |
| `provider` | object | `npm` and `api` fields for model-level provider override |
| `options` | Record\<string, any\> | Arbitrary model-specific options (temperature, topP, etc.) |
| `headers` | Record\<string, string\> | Per-model custom headers |
| `variants` | Record\<string, object\> | Variant-specific config, each with `disabled` (boolean) plus arbitrary additional fields |

Example with variants:

```json
{
  "provider": {
    "my-provider": {
      "models": {
        "claude-sonnet-4-20250514": {
          "name": "Claude Sonnet 4",
          "variants": {
            "thinking": {
              "options": {
                "thinking": { "type": "enabled", "budget_tokens": 8192 }
              }
            }
          }
        }
      }
    }
  }
}
```

## Provider Option Schema

Under `provider.<name>`:

| Field | Type | Description |
|---|---|---|
| `npm` | string | NPM package for custom providers (e.g., `@ai-sdk/openai-compatible`) |
| `name` | string | Display name |
| `api` | string | API endpoint override |
| `env` | string[] | Environment variable names to check for API keys |
| `id` | string | Provider ID override |
| `whitelist` | string[] | Only allow these models from this provider |
| `blacklist` | string[] | Block these models from this provider |
| `options.baseURL` | string | Base URL for API requests |
| `options.apiKey` | string | Direct API key |
| `options.enterpriseUrl` | string | GitHub Enterprise URL for copilot auth |
| `options.setCacheKey` | boolean | Enable promptCacheKey (default false) |
| `options.timeout` | number \| false | Request timeout in milliseconds (default: 300000). Set to `false` to disable. |
| `options.chunkTimeout` | number | Chunk timeout in milliseconds |

## Agent Variant and Options

Agent config supports:

| Field | Type | Description |
|---|---|---|
| `variant` | string | Default model variant for this agent (e.g., `"thinking"`) |
| `options` | Record\<string, any\> | Arbitrary options passed to the model provider |

Example:

```json
{
  "agent": {
    "deep-thinker": {
      "model": "anthropic/claude-sonnet-4-20250514",
      "variant": "thinking",
      "options": {
        "thinking": { "type": "enabled", "budget_tokens": 16384 }
      }
    }
  }
}
```
