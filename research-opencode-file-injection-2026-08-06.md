# Opencode CLI - File Injection into System Prompt / Agent Context

## Executive Summary

OpenCode (opencode.ai) provides **seven distinct mechanisms** for injecting file contents into the agent's system prompt or conversation context. The most powerful and directly relevant for persistent system-level injection are:

1. **`{file:path}` config variable substitution** — injects file contents anywhere in `opencode.json`, including the agent `prompt` field.
2. **`{file:path}` in agent `prompt`** — the canonical way to replace an agent's system prompt with an external file.
3. **`instructions` config key** — loads arbitrary files (local paths, globs, or remote URLs) and injects them into the system prompt prefixed with `Instructions from: <path>`.
4. **Instruction file discovery** — auto-discovers `AGENTS.md` / `CLAUDE.md` files up the directory tree and injects them into the system prompt; additionally discovers nested instruction files during tool `read` execution.
5. **Command template `@filename` syntax** — includes file contents in user prompt (not system prompt) when a custom command is executed.
6. **Command template ``!`command` `` syntax** — injects shell command output into the command's prompt template.
7. **References** — makes external directories or Git repos available to the agent, with resolution paths included in system context.

Additionally, third-party plugins exist that inject recalled memories from vector databases into the system prompt on session start or during compaction.

---

## Key Findings

### 1. `{file:}` Config Variable Substitution (Most Direct Match)

**Location:** `opencode.json` (config file)
**Syntax:** `{file:path/to/file}`

OpenCode supports variable substitution in config files. File paths can be:
- Relative to the config file directory
- Absolute paths starting with `/`
- Home-relative paths starting with `~`

[Source: opencode.ai/docs/config/ — "Variables > Files" section]

**Example:**
```json
{
  "agent": {
    "build": {
      "prompt": "{file:./prompts/build.txt}"
    }
  }
}
```

**Key detail from official docs (Aug 5, 2026):** The `prompt` field on an agent accepts `{file:./prompts/code-review.txt}` — the file contents **fully replace** the agent's system prompt. Path is relative to where the config file is located.

**Caveat:** The path is resolved relative to the config file location (global or project), not the working directory.

**Status:** Officially documented, stable feature.

---

### 2. Agent-level `prompt` with `{file:}` (System Prompt Replacement)

**Location:** `opencode.json` → `agent.<name>.prompt`
**Also available in:** Markdown agent files via YAML frontmatter

When an agent's `prompt` is set to `{file:...}`, the file contents **replace the provider-specific prompt entirely**. From the prompt construction gist [Source: rmk40/cde7a98c1c90614a27478216cc01551f]:

> "If the active agent defines its own prompt (like `explore` or `compaction`), that replaces the provider prompt entirely."

**Example:**
```json
{
  "agent": {
    "review": {
      "prompt": "{file:./prompts/code-review.txt}"
    }
  }
}
```

**Status:** Officially documented, stable.

---

### 3. `instructions` Config Key (Multiple Files + Remote URLs)

**Location:** `opencode.json` → `instructions`
**Syntax:** Array of paths, glob patterns, or URLs

[Source: opencode.ai/docs/rules/ and opencode.ai/docs/config/]

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md",
    "https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"
  ]
}
```

**How it works (from the prompt construction gist [Source: rmk40/cde7a98c1c90614a27478216cc01551f]):**

> "At system prompt time: it walks from the working directory up to the worktree root, checks global config directories and ~/.claude/CLAUDE.md, and resolves any paths or URLs from the `instructions` config key. Each file is prefixed with `Instructions from: <path>`."

**Key behaviors:**
- Supports glob patterns (e.g., `.cursor/rules/*.md`)
- Supports remote URLs (fetched with 5-second timeout)
- Files are combined with AGENTS.md content
- Each file is prefixed with `Instructions from: <path>`
- Resolved at system prompt time, injected into the system prompt array

**Caveat:** A GitHub issue ([anomalyco/opencode#18037](https://github.com/anomalyco/opencode/issues/18037)) documents that when a project has a large AGENTS.md (or CLAUDE.md/CONTEXT.md) file, OpenCode "injects the entire file contents into the system prompt on every loop() iteration with no size guard." This means a 331KB file (~83K tokens) can consume 81% of a 128K context window. This is the acknowledged behavior for instruction files.

**Status:** Officially documented, stable.

---

### 4. Instruction File Discovery (AGENTS.md / CLAUDE.md)

**How it works (from prompt construction gist [Source: rmk40/cde7a98c1c90614a27478216cc01551f]):**

OpenCode's `instruction.ts` module handles `AGENTS.md`, `CLAUDE.md`, and `CONTEXT.md` (deprecated) at two points:

**At system prompt time:**
- Walks from working directory up to worktree root
- Checks global config directories
- Checks `~/.claude/CLAUDE.md`
- Resolves paths/URLs from `instructions` config key
- Each file prefixed with `Instructions from: <path>`

**During tool execution:**
- When the `read` tool accesses a file in a subdirectory, it walks up from that file's directory looking for instruction files not already loaded
- These are injected into tool output as `<system-reminder>` blocks
- A per-message claim system prevents the same file from being injected twice in one turn

**Precedence (from docs [Source: opencode.ai/docs/rules/]):**
1. Local files traversing up from current directory (`AGENTS.md`, then `CLAUDE.md`)
2. Global file at `~/.config/opencode/AGENTS.md`
3. Claude Code fallback at `~/.claude/CLAUDE.md`

**Status:** Core feature, documented.

---

### 5. Command Template `@filename` Syntax (User Prompt Injection)

**Location:** Command markdown files (`.opencode/commands/*.md`) or JSON command templates
**Syntax:** `@` followed by the filename

[Source: opencode.ai/docs/commands/ — "File references" section, Aug 5, 2026]

```markdown
---
description: Review component
---
Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

**Important:** This injects file content into the **user prompt** (the command template), NOT the system prompt. The file content "gets included in the prompt automatically."

**Status:** Officially documented, stable feature.

---

### 6. Command Template ``!`command` `` Syntax (Shell Output Injection)

**Location:** Command markdown files or JSON templates
**Syntax:** `` !`command` `` (backtick-wrapped shell command after `!`)

[Source: opencode.ai/docs/commands/ — "Shell output" section]

```markdown
---
description: Analyze test coverage
---
Here are the current test results:!`npm test`
Based on these results, suggest improvements.
```

**Behavior:**
- Commands run in the project's root directory
- Their stdout becomes part of the prompt
- This is the user prompt, not system prompt

**Status:** Officially documented, stable.

---

### 7. References (External Directories in Agent Context)

**Location:** `opencode.json` → `references`
**Purpose:** Gives agent access to local directories or Git repos outside the current project

[Source: opencode.ai/docs/references/, Aug 5, 2026]

```json
{
  "references": {
    "docs": {
      "path": "../product-docs",
      "description": "Use for product behavior and documentation conventions"
    },
    "sdk": {
      "repository": "anomalyco/opencode-sdk-js",
      "branch": "main",
      "description": "Use for JavaScript SDK implementation details"
    }
  }
}
```

**How it injects context:**
- References **with descriptions** are included in agent system context — the resolved paths + descriptions appear in the system prompt
- Without descriptions, references remain available via `@` autocomplete but are not advertised in system context
- "Hidden" references with descriptions still get system context injection but skip autocomplete

**Status:** Officially documented, stable.

---

### 8. Plugin-Based System Prompt Injection (Third-Party)

Several third-party plugins inject content into the system prompt:

**`experimental.chat.system.transform` hook** (built-in mechanism):
From the prompt construction gist [Source: rmk40/cde7a98c1c90614a27478216cc01551f]:
> "After assembly, a plugin hook (`experimental.chat.system.transform`) gives plugins a chance to mutate the system array — adding, removing, or replacing entries."

**Memory plugins** that use this hook:
- **@vectorize-io/opencode-hindsight** — recalls relevant project context on session start, injects into system prompt via system transform hook [Source: hindsight.vectorize.io/sdks/integrations/opencode]
- **opencode-supermemory** — on session start, relevant memories are fetched and injected into the agent's context [Source: supermemory.ai/docs/integrations/opencode]
- **@knikolov/opencode-plugin-simple-memory** — when autoLoad is enabled, injects a compact memory block into system context before each response [Source: github.com/cnicolov/opencode-plugin-simple-memory]
- **opencode-working-memory** — preserves project decisions across compactions by injecting workspace memory [Source: github.com/sdwolf4103/opencode-working-memory]

**Status:** Plugin ecosystem is active; the transform hook itself is marked `experimental`.

---

### 9. `{env:}` for Config Variable Substitution (Related)

Alongside `{file:}`, OpenCode supports environment variable substitution:

```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

[Source: opencode.ai/docs/config/ — "Variables > Env vars"]

This is NOT file injection but is part of the same config interpolation system.

---

### 10. `systemPrompt` per Model (Provider-Level)

In some configurations, you can set a `systemPrompt` at the model level within a provider:

```json
{
  "provider": {
    "ollama": {
      "models": {
        "qwen2.5-coder:7b": {
          "name": "qwen2.5-coder:7b",
          "systemPrompt": "Your system prompt goes here"
        }
      }
    }
  }
}
```

[Source: Reddit r/opencodeCLI discussion, Aug 2026]

Note: The model-specific `systemPrompt` is the field name used in provider model configs, which maps to the agent `prompt` field in the official docs.

---

## Conflicting Information

- **`prompt` vs `systemPrompt`:** The official docs use `prompt` as the field name for agent-level system prompt customization. Some community examples use `systemPrompt` at the provider/model level. Both appear to work; `prompt` is the officially documented key for agents, while `systemPrompt` appears in provider model configurations.
- **CLI feature request still open:** GitHub issue [#16089](https://github.com/anomalyco/opencode/issues/16089) requests a CLI flag to dynamically inject content into the system prompt at runtime. As of the search date, this feature has not been implemented — users must use config-based approaches instead.

## Confidence Notes

- The `{file:}` syntax for config variable substitution is confirmed by the official documentation at opencode.ai/docs/config/ (last updated Aug 5, 2026).
- The `instructions` key behavior is confirmed by both the official docs and the prompt construction gist.
- The incremental instruction file discovery during `read` tool execution is from the community gist (rmk40) which traces source code paths — high confidence but not officially documented in the user-facing docs.
- The `system Prompt` vs `prompt` field naming is from a Reddit discussion; the official docs use `prompt` for agents. The `systemPrompt` field may be provider-level or legacy.

## Open Questions

- Exact behavior when combining `{file:}` in `prompt` with `instructions` config — do they stack or does `prompt` replace everything? The prompt construction pipeline suggests `prompt` replaces the provider prompt but instructions are separate, so they likely stack.
- Whether `{file:}` supports glob patterns or only single file paths (the `instructions` key supports globs; `{file:}` docs only show single paths).
- Size limits on `{file:}` substitution in config values.
- Whether the `{file:}` variable substitution works in the `instructions` key itself (e.g., `"instructions": ["{file:./file-list.txt}"]`) — the docs don't address this nesting case.

## Sources

| # | Title | URL | Relevance |
|---|-------|-----|-----------|
| 1 | OpenCode Config Docs | https://opencode.ai/docs/config/ | Official docs: `{file:}` and `{env:}` variables, `instructions` key |
| 2 | OpenCode Agents Docs | https://opencode.ai/docs/agents/ | Official docs: agent `prompt` with `{file:}` syntax |
| 3 | OpenCode Commands Docs | https://opencode.ai/docs/commands/ | Official docs: `@filename` and ``!`command` `` template syntax |
| 4 | OpenCode Rules Docs | https://opencode.ai/docs/rules/ | Official docs: AGENTS.md discovery, `instructions` config |
| 5 | OpenCode References Docs | https://opencode.ai/docs/references/ | Official docs: references in system context |
| 6 | Prompt Construction Gist | https://gist.github.com/rmk40/cde7a98c1c90614a27478216cc01551f | Deep technical analysis of system prompt assembly pipeline |
| 7 | GitHub Issue #18037 | https://github.com/anomalyco/opencode/issues/18037 | Confirms no size guard on instruction file injection |
| 8 | GitHub Issue #16089 | https://github.com/anomalyco/opencode/issues/16089 | CLI flag for system prompt injection — requested but not yet implemented |
| 9 | Hindsight Plugin Docs | https://hindsight.vectorize.io/sdks/integrations/opencode | Memory injection via `experimental.chat.system.transform` hook |
| 10 | OpenCode System Prompts Guide | https://github.com/bgauryy/open-docs/blob/main/docs/opencode/05-system-prompts.md | Community guide on AGENTS.md hierarchy and prompt assembly order |
