# Local Memory System via opencode Plugins

> **SUPERSEDED (2026-08-18).** Not implemented, and not to be implemented as written.
> Memory now ships as two `MEMORY.md` files loaded through the `instructions` array in
> `.opencode/opencode.json`, driven by the **Memory** section of `.opencode/prompts/build.txt`.
> See `AGENTS.md` → *Memory is two MEMORY.md files wired through `instructions`*.
> The plan derived from this spec, `docs/plans/2026-08-05-local-memory.md`, is superseded too.
> Kept for the design rationale on episodic recall and context budgeting, which the current
> approach does not cover.

**Date:** 2026-08-05
**Topic:** Memory and schedules plugin infrastructure with persistent, filesystem-backed memory

## Goal

Give the opencode agent persistent memory across sessions — factual knowledge always in context, and episodic recall by semantic similarity — and establish a plugin folder structure for extending opencode with custom plugins (starting with memory, then schedules).

## Current State

The build prompt (`build.txt`) has no mechanism for persistent memory. Compaction (`compaction.txt`) is lossy — it summarizes and drops detail permanently when context overflows. `AGENTS.md` provides static instructions but is not maintained by the agent during sessions. There is no plugin directory or plugin infrastructure in this repo.

## Design

### Plugin Infrastructure

A `plugins/` directory is added to the repo root. The install scripts (`install.sh`, `install.ps1`) deploy plugins to `~/.config/opencode/plugins/` where opencode auto-discovers them.

```
plugins/
  memory/
    package.json
    index.js
    context.js
    tools.js
    episodic.js
    collector.js
    assets/
      model.onnx
      tokenizer.json
      vocab.txt
  schedules/
    package.json
    index.js
```

Both installers gain a plugins deployment block — same pattern as skills and agents: copy from repo, remove stale plugins no longer in the repo.

### Memory Plugin

A single V2 plugin (`Plugin.define({ id: "memory", setup(ctx) })`) handling two memory subsystems: **factual** (file-based, always injected) and **episodic** (SQLite + vector search, RAG-injected).

#### Factual Memory

Structured markdown files in `facts/` directories. Every entry is loaded and injected into the system prompt on every turn.

**Storage layout:**

```
~/.opencode/memory/facts/        ← global (user-level)
  preferences.md
  facts.md
  conventions.md
  people.md
<workspace>/.opencode/memory/facts/  ← project-level
  <category>.md
```

Default categories (`preferences`, `facts`, `conventions`, `people`) ship as template files. New categories are created via `memory.create_category`.

**Injected format** (appended to `event.system` via `session.hook("context")`):

```xml
<memory>
<memory-facts>
Categories: preferences, facts, conventions, people
---
[category entries, global then workspace]
</memory-facts>
<memory-episodes>
[top-3 semantically similar episodes]
</memory-episodes>
</memory>
```

**Workspace definition:** The "workspace" is the current working directory of the opencode session — the directory the user opened opencode in. The plugin resolves this from the V2 session context. Per-project memory lives in `<workspace>/.opencode/memory/`.

Category files that exist but are empty still appear in the category list but contribute no entries — the agent knows what slots exist without wasting tokens on blank files.

**Injected tools** (via `ctx.tool.transform(t => t.add(...))`):

| Tool | Purpose | Input |
|------|---------|-------|
| `memory.write` | Add or update an entry | `category` (string), `key` (string), `value` (string) |
| `memory.update` | Modify an existing entry | `category`, `key`, `patch` (string — text to append) |
| `memory.delete` | Remove an entry | `category`, `key` |
| `memory.create_category` | Create a new category file | `name`, `description` |

No `memory.read` tool — facts are always injected and visible to the agent in the system prompt. No `list_categories` tool — the category list is always present in the injected `<memory-facts>` block.

#### Episodic Memory

Automatically collected during agent runs. No tools exposed — the agent never interacts with episodes directly.

**Storage layout:**

```
~/.opencode/memory/episodes/        ← global
  episodes.db
  .gitignore
<workspace>/.opencode/memory/episodes/  ← project-level
  episodes.db
  .gitignore
```

SQLite database with `sqlite-vec` extension for vector similarity search.

**Collection:** The plugin captures conversation turns during the session. On session end (or after 5 minutes of inactivity), it summarizes the segment via a compacting call to the model, embeds the summary with a local ONNX model, and stores (summary, embedding, timestamp, workspace path) in SQLite.

**RAG injection:** On every `session.hook("context")` call, the current user message is embedded and used as a vector query. Top-3 matching episodes from both global and workspace `episodes.db` are merged and injected into `<memory-episodes>`.

**Embedding model:** `all-MiniLM-L6-v2` via `onnxruntime-node` — 22M parameters, 80-dim embeddings, ~20ms per vector. Model files (`model.onnx`, `tokenizer.json`, `vocab.txt`) are bundled as static assets in `plugins/memory/assets/`.

#### Context Budget

The plugin reads the active model's `limit.input` from the V2 context and sets the injection budget to **10 % of that value** (e.g., ~20 480 tokens for the default model). This adapts automatically when the user switches models.

Tokens are counted locally using the `cl100k_base` BPE tokenizer (via the `tiktoken` npm package) — no network call, sub-millisecond per string.

When injected memory exceeds the budget:
1. Factual entries are truncated oldest-first (by last-modified timestamp on the category file)
2. Episodic results are reduced from top-3 to top-1

#### Error Handling

| Failure | Behavior |
|---------|----------|
| Facts files missing | Created on first write |
| SQLite DB missing | Created on first run, table initialized |
| Model load failure | Episodic injection silently skipped; factual injection continues; logged to console |
| Embedding failure mid-session | That episode skipped; collection continues for future segments |
| Context overflow | Dynamic cap at 10 % of model input, oldest facts first, episodes reduced |
| Workspace not a project (no `.opencode/`) | Only global memory loaded; no per-project directory created |

### Schedules Plugin

Skeleton placeholder for the next plugin. Same V2 structure: `Plugin.define({ id: "schedules", setup(ctx) })`, tool injection via `ctx.tool.transform`, context injection via `session.hook("context")`. No implementation detail at this stage — exists to reserve the slot in the folder structure.

### Build Prompt Changes

A new `# Memory` section is added to `build.txt`, instructing the agent to:

1. Use `memory.write` to store new facts, preferences, conventions discovered during work
2. Use `memory.update` to correct or expand existing entries
3. Use `memory.delete` to retire stale entries
4. Use `memory.create_category` when a new memory dimension is needed
5. Treat `<memory-facts>` as ground truth — don't contradict stored preferences
6. Treat `<memory-episodes>` as contextual recall — apply patterns from past sessions

No instruction is needed for episodic memory — it is automatic.

## Dependencies

| Package | Purpose |
|---------|---------|
| `onnxruntime-node` | Local embedding inference |
| `better-sqlite3` | Synchronous SQLite access |
| `sqlite-vec` | Vector similarity search in SQLite |
| `tiktoken` | Local BPE token counting (cl100k_base) |

## What Is Not In Scope

- Schedules plugin implementation (next iteration)
- Embedding model fine-tuning (default MiniLM is sufficient for RAG recall)
- Memory export/import between machines
- Memory versioning or rollback