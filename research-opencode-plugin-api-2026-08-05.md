# OpenCode Plugin API — Comprehensive Reference

## Executive Summary

OpenCode has **two plugin API generations** coexisting today:

1. **V1 (stable)** — The current production API. Plugins are JS/TS modules that export named functions returning a `Hooks` object. Loaded via `opencode.json` `"plugin"` array or auto-discovered from `.opencode/plugins/`. Provides 25+ event hooks, custom tool registration, auth hooks, and provider hooks.

2. **V2 (beta)** — A restructured API using `Plugin.define({ id, setup })` with imperative hook registration via `ctx.<domain>.transform()` and `ctx.<domain>.hook()`. Splits capabilities into **transform hooks** (modify configuration state) and **runtime hooks** (intercept live operations). Two entrypoints: Promise-based (`@opencode-ai/plugin/v2/promise`) and Effect-based (`@opencode-ai/plugin/v2/effect`). Configured via `"plugins"` (plural) in `opencode.json`.

Both APIs are well-documented and actively used. The V2 API is the future direction but is explicitly marked beta with the caveat that entrypoints, hooks, and configuration may change.

---

## 1. Tool Injection — Can Plugins Add Custom Tools?

**Yes.** Both V1 and V2 support full tool injection. This is one of the primary plugin capabilities.

### V1 — Returning `tool` in the Hooks object

```ts
import { tool } from "@opencode-ai/plugin"

export const MyPlugin = async (ctx) => ({
  tool: {
    mytool: tool({
      description: "This is a custom tool",
      args: {
        foo: tool.schema.string().describe("foo parameter"),
        count: tool.schema.number().optional().describe("optional count"),
      },
      async execute(args, context) {
        // context: { sessionID, messageID, agent, directory, worktree, abort, metadata(), ask() }
        return `Hello ${args.foo}! Count: ${args.count || 1}`
      },
    }),
  },
})
```

The `tool()` helper uses Zod (`tool.schema === z`) for argument validation. The tool name becomes `<plugin>_<export>` or just the export name. Tools appear alongside built-in tools. If a plugin tool shares a name with a built-in tool, **the plugin tool takes precedence**.

### V2 — Using `ctx.tool.transform()` with `tools.add()`

```ts
import { Plugin } from "@opencode-ai/plugin"

export default Plugin.define({
  id: "acme.greeting",
  setup: async (ctx) => {
    await ctx.tool.transform((tools) => {
      tools.add("greeting", {
        description: "Create a greeting",
        input: {
          type: "object",
          properties: { name: { type: "string" } },
          required: ["name"],
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: { greeting: { type: "string" } },
          required: ["greeting"],
          additionalProperties: false,
        },
        execute: async ({ name }) => ({
          output: { greeting: `Hello, ${name}!` },
          content: `Hello, ${name}!`,
        }),
      }, { namespace: "acme", codemode: true })
    })
  },
})
```

V2 tools use JSON Schema (not Zod) for `input`/`output`. The third optional argument to `tools.add()` configures `{ namespace, codemode }`:
- `namespace` — prefixes and groups the exposed tool name
- `codemode` — defaults to `true`; set to `false` to expose directly to the provider instead of through the `execute` CodeMode tool

The executor receives a second context argument with `id`, `sessionID`, `agent`, `messageID`, and `progress`.

### `session.hook("context", ...)` — Modifying `event.tools`

In V2, the `ctx.session.hook("context", callback)` runtime hook fires **immediately before model dispatch** and receives an event with mutable `system`, `messages`, and `tools` fields:

```ts
await ctx.session.hook("context", (event) => {
  // event.tools is a record of tool definitions
  delete event.tools.write  // Remove a tool from the request
  event.tools.myCustomTool = { ... }  // Add a tool dynamically
})
```

This is different from `ctx.tool.transform()` which registers tools structurally. The context hook lets you **dynamically add/remove tools per-request** based on session state, model, or any other condition. You can also modify existing tool definitions (descriptions, parameters) on a per-request basis.

### Standalone Custom Tools (no plugin needed)

OpenCode also supports standalone tool files in `.opencode/tools/` or `~/.config/opencode/tools/`. A `.ts`/`.js` file that exports a `tool()` call becomes a tool named after the filename. Multiple named exports from one file become `<filename>_<exportname>`.

---

## 2. Plugin System Structure

### Where Plugin Files Live

| Location | Scope | Auto-discovered? |
|----------|-------|------------------|
| `.opencode/plugins/` (project) | Current project | Yes — direct `.ts`/`.js` children |
| `~/.config/opencode/plugins/` (global) | All projects | Yes — same rules |
| npm packages (in config) | All projects | No — must be listed in config |

For auto-discovery:
- Direct `.ts` and `.js` children of the plugins directory are loaded
- An immediate child **directory** is also loaded if it has a resolvable `exports`, `module`, `main`, or `index.ts`/`index.js`
- A `plugins/` directory beside a project-root `opencode.json` is **NOT** auto-discovered — put it under `.opencode/` or add it explicitly

### How Plugins Are Configured

**V1** — `"plugin"` (singular) in `opencode.json`:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "opencode-helicone-session",
    "@my-org/custom-plugin",
    ["@vectorize-io/opencode-hindsight", { "hindsightApiUrl": "https://api.hindsight.vectorize.io" }]
  ]
}
```

Items can be:
- A string: npm package name or local path (`./plugins/local.ts`)
- A 2-element array: `[package, optionsObject]`

**V2** — `"plugins"` (plural) in `opencode.json`:
```json
{
  "plugins": [
    "opencode-acme-plugin@1.2.0",
    "@acme/opencode-plugin",
    "./plugins/local.ts",
    { "package": "./plugins/reviewer.ts", "options": { "agent": "reviewer", "strict": true } }
  ]
}
```

V2 supports versioned package specifiers, absolute paths, `file://` URLs, and the object form for passing options.

### Disable plugins (V2 only):
```json
{
  "plugins": ["./plugins/reviewer.ts", "-acme.reviewer", "-opencode.provider.*", "opencode.provider.openai"]
}
```
A string starting with `-` disables by plugin `id`. `*` matches all. `.*` suffix matches by prefix.

### Load Order
1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin directory (`~/.config/opencode/plugins/`)
4. Project plugin directory (`.opencode/plugins/`)

Hooks run sequentially in registration order. Later hooks observe earlier mutations.

### Dependencies

npm plugins: OpenCode auto-installs via Bun at startup. Cached in `~/.cache/opencode/node_modules/`. No lifecycle scripts are run.

Local plugins: Install deps via `package.json` in the config directory. OpenCode runs `bun install` at startup.

### Config Schema Field

From `https://opencode.ai/config.json`:
```json
"plugin": {
  "type": "array",
  "items": {
    "anyOf": [
      { "type": "string" },
      {
        "type": "array",
        "prefixItems": [{ "type": "string" }, { "type": "object" }],
        "maxItems": 2,
        "minItems": 2
      }
    ]
  }
}
```

Note: The config schema defines `"plugin"` (singular, V1). V2's `"plugins"` (plural) is handled by the V2 server and is not in the current JSON schema.

---

## 3. Plugin Entry Point

### V1 Entry Point

A module exporting **one or more named functions**:

```ts
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Hook implementations
  }
}
```

The `Plugin` type is: `(input: PluginInput, options?: PluginOptions) => Promise<Hooks>`

The `PluginInput` context provides:
- `client` — OpenCode SDK client for API calls
- `project` — Current project information
- `directory` — Current working directory
- `worktree` — Git worktree path
- `$` — Bun's shell API (`Bun.$`)
- `serverUrl` — Server URL
- `experimental_workspace` — Workspace adapter registration

### V2 Entry Point

A module with a **default export** from `Plugin.define()`:

```ts
import { Plugin } from "@opencode-ai/plugin"

export default Plugin.define({
  id: "acme.reviewer",
  setup: async (ctx) => {
    // Register hooks imperatively
    await ctx.agent.transform((agents) => { ... })
    await ctx.session.hook("context", (event) => { ... })
  },
})
```

Or with Effect:
```ts
import { Plugin } from "@opencode-ai/plugin/effect"
import { Effect } from "effect"

export default Plugin.define({
  id: "acme.reviewer-effect",
  effect: (ctx) => Effect.gen(function* () {
    yield* ctx.agent.transform((agents) => { ... })
  }),
})
```

The `setup` function runs each time the plugin is activated. It may return a cleanup function that OpenCode calls on disable/reload/shutdown. Hook registrations are released automatically with the plugin scope.

### V2 Plugin Context (`ctx`)

The V2 context is essentially an OpenCode server client with plugin-only extensions:

| Capability | Operations |
|---|---|
| `ctx.agent` | `list`, `get`, `transform`, `reload` |
| `ctx.catalog.provider` | `list`, `get` |
| `ctx.catalog.model` | `list`, `get`, `default` |
| `ctx.catalog` | `transform`, `reload` |
| `ctx.command` | `list`, `transform`, `reload` |
| `ctx.integration` | `list`, `get`, `connect`, `attempt`, `transform`, `reload`, connection lookup/resolution |
| `ctx.plugin` | `list` (active plugin IDs) |
| `ctx.reference` | `list`, `transform`, `reload` |
| `ctx.session` | `create`, `get`, `prompt`, `command`, `rename`, `synthetic`, `interrupt`, `wait`, `hook` |
| `ctx.skill` | `list`, `transform`, `reload` |
| `ctx.tool` | `transform`, `hook` |
| `ctx.aisdk` | `hook` |
| `ctx.event` | `subscribe` to server event stream |
| `ctx.options` | Readonly options from config object |

---

## 4. Available Hooks

### V1 Hooks (return in the `Hooks` object)

#### Tool Hooks
| Hook | Signature | Purpose |
|------|-----------|---------|
| `tool` | `{ [name]: ToolDefinition }` | Register custom tools |
| `"tool.execute.before"` | `(input: {tool, sessionID, callID}, output: {args})` | Intercept/modify tool args before execution. Throw to block. |
| `"tool.execute.after"` | `(input: {tool, sessionID, callID, args}, output: {title, output, metadata})` | Post-execution — modify output |
| `"tool.definition"` | `(input: {toolID}, output: {description, parameters})` | Modify tool definitions sent to LLM |

#### Chat/Message Hooks
| Hook | Signature | Purpose |
|------|-----------|---------|
| `"chat.message"` | `(input, output: {message, parts})` | Called when a new message is received |
| `"chat.params"` | `(input, output: {temperature, topP, topK, maxOutputTokens, options})` | Modify LLM parameters |
| `"chat.headers"` | `(input, output: {headers})` | Modify request headers to provider |
| `"experimental.chat.messages.transform"` | `(input, output: {messages: [{info, parts}]})` | Transform full message history |
| `"experimental.chat.system.transform"` | `(input: {sessionID, model}, output: {system: string[]})` | Inject/modify system prompt |

#### Session Hooks
| Hook | Signature | Purpose |
|------|-----------|---------|
| `"experimental.session.compacting"` | `(input: {sessionID}, output: {context: string[], prompt?: string})` | Customize compaction prompt/context |
| `"experimental.compaction.autocontinue"` | `(input, output: {enabled: boolean})` | Control auto-continue after compaction |
| `"experimental.text.complete"` | `(input, output: {text})` | Post-process completed text |

#### Permission Hooks
| Hook | Signature | Purpose |
|------|-----------|---------|
| `"permission.ask"` | `(input: Permission, output: {status})` | Auto-allow/deny permissions |

#### Command Hooks
| Hook | Signature | Purpose |
|------|-----------|---------|
| `"command.execute.before"` | `(input: {command, sessionID, arguments}, output: {parts})` | Pre-process command execution |

#### Shell Hooks
| Hook | Signature | Purpose |
|------|-----------|---------|
| `"shell.env"` | `(input: {cwd, sessionID, callID}, output: {env})` | Inject environment variables into shell |

#### Provider/Auth Hooks
| Hook | Type | Purpose |
|------|------|---------|
| `auth` | `AuthHook` | Register custom auth providers (OAuth, API key) |
| `provider` | `ProviderHook` | Register custom model providers |
| `"experimental.provider.small_model"` | Hook | Override small model selection |

#### Event Bus
| Hook | Signature | Purpose |
|------|-----------|---------|
| `event` | `(input: {event: Event}) => void` | Subscribe to all events |

#### Config Hook
| Hook | Signature | Purpose |
|------|-----------|---------|
| `config` | `(input: Config) => void` | Modify runtime config |

#### V1 Event Types (accessible via `event` hook)

**Command Events:** `command.executed`

**File Events:** `file.edited`, `file.watcher.updated`

**Installation Events:** `installation.updated`

**LSP Events:** `lsp.client.diagnostics`, `lsp.updated`

**Message Events:** `message.part.removed`, `message.part.updated`, `message.removed`, `message.updated`

**Permission Events:** `permission.asked`, `permission.replied`

**Server Events:** `server.connected`

**Session Events:** `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated`

**Shell Events:** `shell.env`

**Todo Events:** `todo.updated`

**Tool Events:** `tool.execute.after`, `tool.execute.before`

**TUI Events:** `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`

**Important caveat from GitHub issue #418:** `session.created` and `tui.prompt.append` exist as bus events but are **NOT dispatched to plugin hooks** via the `trigger()` mechanism. They are internal UI events. The correct hooks for those use cases are:
- Session init logic → run in the plugin factory function (executes once per session at load)
- User prompt interception → use `chat.message` hook
- System prompt injection → use `experimental.chat.system.transform` hook

### V2 Hooks

V2 splits hooks into two categories:

#### Transform Hooks (modify configuration state)

| Transform | Draft Operations |
|-----------|-----------------|
| `ctx.agent.transform((agents) => ...)` | `list`, `get`, `default`, `update`, `remove` |
| `ctx.catalog.transform((catalog) => ...)` | Provider: `list`, `get`, `update`, `remove`; Model: `get`, `update`, `remove`; Default model: `get`, `set` |
| `ctx.command.transform((commands) => ...)` | `list`, `get`, `update`, `remove` |
| `ctx.integration.transform((integrations) => ...)` | Integration: `list`, `get`, `update`, `remove`; Method: `list`, `update`, `remove` |
| `ctx.reference.transform((refs) => ...)` | `add`, `remove`, `list` |
| `ctx.skill.transform((skills) => ...)` | `source`, `list` |
| `ctx.tool.transform((tools) => ...)` | `add` |

After any transform, call `ctx.<domain>.reload()` to replay all transforms and rebuild the domain.

#### Runtime Hooks (intercept live operations)

| Hook | Mutable Fields | Purpose |
|------|---------------|---------|
| `ctx.aisdk.hook("sdk", callback)` | `sdk` (after inspecting `model`, `package`, `options`) | Replace AI SDK instance for a model |
| `ctx.aisdk.hook("language", callback)` | `language` (after inspecting `model`, `sdk`, `options`) | Replace language model instance |
| `ctx.session.hook("context", callback)` | `system`, `messages`, `tools` record | Modify context before model dispatch |
| `ctx.session.hook("http", callback)` | `use(request, next)` middleware chain | Intercept HTTP requests/responses to providers |
| `ctx.tool.hook("execute.before", callback)` | `input` | Intercept tool args before execution |
| `ctx.tool.hook("execute.after", callback)` | `result` (success) or `error` (failure) | Post-execution tool result |

HTTP hooks apply to native models only; AI SDK models do not pass through this hook.

---

## 5. Full Plugin Lifecycle

### V1 Lifecycle

1. **Discovery** — OpenCode scans config files and plugin directories at startup
2. **Install** — npm packages are installed via Bun into `~/.cache/opencode/node_modules/` (no lifecycle scripts)
3. **Resolve** — Each plugin spec is resolved to a filesystem entrypoint
4. **Import** — Module is dynamically imported via `import(entry)`
5. **Execute** — Each exported function is called with `PluginInput` and optional `options`
6. **Hook registration** — Returned `Hooks` object is registered with the event system
7. **Runtime** — Hooks fire as events occur during session execution
8. **Dispose** — If a hook returns a `dispose` function, it's called on shutdown

### V2 Lifecycle

1. **Discovery** — Same as V1, plus support for versioned packages, absolute paths, `file://` URLs
2. **Install** — Same as V1
3. **Resolve** — Plugin resolved to entrypoint; V2 checks for default export with `Plugin.define()`
4. **Import** — Module dynamically imported
5. **Setup** — `setup(ctx)` or `effect(ctx)` is called. Plugin registers hooks imperatively via `ctx.<domain>.transform()` and `ctx.<domain>.hook()`
6. **Transform apply** — Each transform hook contributes to its domain's draft state. Domains are rebuilt from scratch, running all transforms in registration order
7. **Runtime** — Runtime hooks fire on live operations. Hooks run sequentially in registration order
8. **Reload** — When data changes, `ctx.<domain>.reload()` replays all transforms
9. **Cleanup** — `setup` may return a cleanup function. OpenCode awaits it on disable/reload/shutdown. Hook registrations are released automatically with plugin scope

### Hot Reload

Configuration and discovered plugin files under watched config directories are reloaded when they change. Reloading replaces the active plugin generation and releases its scoped registrations. For npm package version changes or local dependency changes, restart OpenCode.

---

## 6. Config Schema — `plugin` Field

From `https://opencode.ai/config.json`:

```json
"plugin": {
  "type": "array",
  "items": {
    "anyOf": [
      { "type": "string" },
      {
        "type": "array",
        "prefixItems": [
          { "type": "string" },
          { "type": "object" }
        ],
        "maxItems": 2,
        "minItems": 2
      }
    ]
  }
}
```

This is the V1 schema. Each item is either:
- A string (npm package name or local path)
- A 2-element tuple: `[string, object]` where the string is the package and the object is plugin options

The V2 `"plugins"` field (plural) is not yet in the JSON schema — it's handled by the V2 server directly.

---

## 7. Key Differences: V1 vs V2

| Aspect | V1 | V2 |
|--------|----|----|
| Config key | `"plugin"` | `"plugins"` |
| Entry point | Named export functions | Default export via `Plugin.define()` |
| Hook registration | Return hooks object | Imperative calls in `setup()` |
| Tool injection | `tool: { name: tool({...}) }` in returned object | `ctx.tool.transform(t => t.add(...))` |
| Tool schema | Zod (`tool.schema`) | JSON Schema + Effect Schema |
| Context hook | `experimental.chat.messages.transform` | `ctx.session.hook("context", ...)` with mutable `tools` |
| Plugin ID | Implicit (from export name) | Explicit `id` field |
| Options | Passed as second arg to function | Available as `ctx.options` |
| Async model | Promises only | Promises OR Effect |
| Status | Stable | Beta — may change |
| Disable syntax | Not supported | `"-"` prefix with wildcards |
| Versioned packages | Not supported | `"package@1.2.0"` |

---

## Sources

| # | Title | URL | Relevance |
|---|-------|-----|-----------|
| 1 | V2 Plugins docs | https://opencode.ai/v2/docs/build/plugins | Primary V2 API documentation |
| 2 | V1 Plugins docs | https://opencode.ai/docs/plugins/ | Primary V1 API documentation |
| 3 | Custom Tools docs | https://opencode.ai/docs/custom-tools/ | Standalone tool definition |
| 4 | Config schema | https://opencode.ai/config.json | JSON Schema for `plugin` field |
| 5 | Plugin index.ts | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/index.ts | V1 `Hooks` interface, `Plugin` type, `PluginInput` |
| 6 | Plugin tool.ts | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/tool.ts | V1 `tool()` helper, `ToolDefinition`, `ToolContext` |
| 7 | V2 promise/README.md | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/v2/promise/README.md | V2 Promise API guide |
| 8 | V2 effect/README.md | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/v2/effect/README.md | V2 Effect API guide |
| 9 | V2 context.ts | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/v2/promise/context.ts | V2 `PluginContext` interface |
| 10 | V2 registration.ts | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/v2/promise/registration.ts | `Registration`, `Reload`, `Hooks<Spec>` types |
| 11 | V2 plugin.ts | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/v2/promise/plugin.ts | `Plugin.define()`, `Plugin` interface |
| 12 | V2 aisdk.ts | https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/v2/promise/aisdk.ts | AI SDK hook types |
| 13 | Plugin loader.ts | https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/plugin/loader.ts | Plugin loading pipeline |
| 14 | Plugin directory | https://github.com/anomalyco/opencode/tree/dev/packages/plugin/src/v2 | V2 source structure |
| 15 | OpenCode School — Plugins | https://opencode.school/lessons/plugins/ | Tutorial with examples |
| 16 | GitHub issue #418 — wrong hooks | https://github.com/JuliusBrussee/caveman/issues/418 | `session.created`/`tui.prompt.append` not dispatched to plugins |
| 17 | GitHub issue #16626 — session.stopping | https://github.com/anomalyco/opencode/issues/16626 | Feature request for `session.stopping` hook |
| 18 | Hindsight integration docs | https://hindsight.vectorize.io/sdks/integrations/opencode | Real-world V1 plugin example |
| 19 | OpenCode Book — Hook System | https://www.opencodebook.xyz/en/chapter_15_oh-my-opencode_deep_dive/15.5_hook_system | 53 hooks detailed in oh-my-opencode |
| 20 | npm @opencode-ai/plugin | https://www.npmjs.com/package/@opencode-ai/plugin | Package info — v1.18.10, 8.3M downloads |

---

## Conflicting Information

- **`session.created` as a plugin hook:** The V1 docs list `session.created` under Session Events, but GitHub issue #418 confirms it is published as a bus event and **never dispatched to plugin hooks**. Use `chat.message` for user prompt interception or run logic in the plugin factory function for session init.

- **`tui.prompt.append` as a pre-send hook:** Same issue — it's a TUI input-field event (inserts text into the prompt widget), not a pre-send hook. Not dispatched to plugins.

- **V1 vs V2 coexistence:** The config schema defines `"plugin"` (V1, singular) but V2 uses `"plugins"` (plural). Both appear to work in practice, but the schema only validates V1.

---

## Confidence Notes

- **V2 API stability:** Explicitly marked beta. The docs state "Entrypoints, hooks, draft shapes, and configuration may change before the stable release." All V2 findings should be treated as current but potentially transient.

- **`session.hook("context", ...)` event.tools:** The V2 docs show `delete event.tools.write` as an example of modifying the tools record. The exact shape of `event.tools` (Record\<string, ToolDefinition\>?) is inferred from the docs and source types but not exhaustively documented.

- **Event dispatch completeness:** The official V1 docs list 25+ events, but at least 2 (`session.created`, `tui.prompt.append`) are confirmed not to fire for plugins. There may be others with the same issue.

---

## Open Questions

1. **What is the exact type of `event.tools` in `session.hook("context", ...)`?** The docs show deletion works, but the full tool definition shape in the event is not typed in the public SDK.

2. **Does V2 have an equivalent to V1's `event` bus hook?** The V2 context has `ctx.event.subscribe()` for the server event stream, but it's unclear if this covers the same events as V1's `event` hook.

3. **Is there a `session.stopping` hook in V2?** GitHub issue #16626 requests this for both APIs — it doesn't exist yet. The `session.idle` event fires after the agent loop has already broken.

4. **How do V1 and V2 plugins interact when both are loaded?** The docs don't address cross-generation plugin interactions.

5. **What's the timeline for V2 stable?** No release date or milestone is mentioned in any source.
