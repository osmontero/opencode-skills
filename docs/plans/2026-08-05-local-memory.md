# Local Memory System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a memory plugin and schedules plugin skeleton to the repo, with install-script deployment, so the agent has persistent factual and episodic memory across sessions.

**Architecture:** Two V2 plugins using `Plugin.define({ id, setup })` — `memory` (full: factual CRUD tools + context injection, episodic SQLite + ONNX + RAG + collector) and `schedules` (skeleton only). Deployed via updated install scripts to `~/.config/opencode/plugins/`. Build prompt receives a Memory section.

**Tech Stack:** `@opencode-ai/plugin` V2, `better-sqlite3`, `sqlite-vec`, `onnxruntime-node`, `tiktoken` (cl100k_base).

---

## File Structure

| File | Responsibility |
|------|---------------|
| `plugins/memory/package.json` | Plugin metadata + deps: `@opencode-ai/plugin`, `better-sqlite3`, `sqlite-vec`, `onnxruntime-node`, `tiktoken` |
| `plugins/memory/index.js` | V2 `Plugin.define` entry — registers tools, context hook, episodic RAG injection, starts collector |
| `plugins/memory/context.js` | Factual memory path resolution, fact file CRUD, category scanning |
| `plugins/memory/tools.js` | V2 tool definitions (JSON Schema) registered via `ctx.tool.transform` — write, update, delete, create_category |
| `plugins/memory/episodic.js` | SQLite + sqlite-vec init, ONNX embedding via onnxruntime-node, vector search |
| `plugins/memory/collector.js` | Session turn capture, inactivity timer, conversation summarization, episode storage |
| `plugins/memory/assets/` | `model.onnx`, `tokenizer.json`, `vocab.txt` — all-MiniLM-L6-v2 ONNX assets downloaded from HuggingFace |
| `plugins/schedules/package.json` | Minimal: `@opencode-ai/plugin` dependency |
| `plugins/schedules/index.js` | V2 `Plugin.define` skeleton — no tools, no hooks |
| `install.sh` | Add plugins/ deployment block (bash) |
| `install.ps1` | Add plugins/ deployment block (PowerShell) |
| `.opencode/prompts/build.txt` | Append `# Memory` section |

---

### Task 1: Plugin Infrastructure — Folder Structure &amp; Package Files

**Files:**
- Create: `plugins/memory/package.json`
- Create: `plugins/schedules/package.json`

- [ ] **Step 1: Create directory structure**

```powershell
New-Item -ItemType Directory -Path "plugins\memory\assets" -Force | Out-Null
New-Item -ItemType Directory -Path "plugins\schedules" -Force | Out-Null
```

- [ ] **Step 2: Write `plugins/memory/package.json`**

```json
{
  "name": "@opencode-skill/memory-plugin",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js",
  "dependencies": {
    "@opencode-ai/plugin": "latest",
    "better-sqlite3": "^11.10.0",
    "sqlite-vec": "^0.1.6-alpha.3",
    "onnxruntime-node": "^1.21.0",
    "tiktoken": "^1.0.21"
  }
}
```

- [ ] **Step 3: Write `plugins/schedules/package.json`**

```json
{
  "name": "@opencode-skill/schedules-plugin",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js",
  "dependencies": {
    "@opencode-ai/plugin": "latest"
  }
}
```

- [ ] **Step 4: npm install in both plugin directories**

```powershell
cd plugins/memory && npm install && cd ..\..
cd plugins/schedules && npm install && cd ..\..
```

- [ ] **Step 5: Commit**

```bash
git add plugins/
git commit -m "feat: add plugin infrastructure with memory and schedules scaffolds"
```

---

### Task 2: Memory Plugin Entry Point (`index.js`)

**Files:**
- Create: `plugins/memory/index.js`

- [ ] **Step 1: Write the plugin entry point**

```js
import { Plugin } from "@opencode-ai/plugin";

import { registerFactualTools } from "./tools.js";
import { buildMemoryFactsBlock } from "./context.js";
import { initEpisodicDb, queryEpisodes } from "./episodic.js";
import { startCollector, stopCollector } from "./collector.js";
import { countTokens } from "./context.js";

const DEFAULT_MODEL_INPUT_LIMIT = 204800;

export default Plugin.define({
  id: "memory",
  setup: async (ctx) => {
    // --- 1. Register factual tools ---
    await ctx.tool.transform(t => {
      const factualTools = registerFactualTools();
      for (const toolDef of factualTools) {
        t.add(toolDef.name, toolDef.schema, toolDef.handler);
      }
    });

    // --- 2. Context hook — inject facts + episodes ---
    await ctx.session.hook("context", async (event) => {
      const modelLimit = ctx.options?.model?.limit?.input ?? DEFAULT_MODEL_INPUT_LIMIT;
      const budget = Math.floor(modelLimit * 0.1);

      let factsBlock = "";
      try {
        factsBlock = buildMemoryFactsBlock(event.workspace);
      } catch (e) {
        console.error("[memory] failed to load facts:", e.message);
      }

      let episodes = [];
      try {
        const lastUser = event.messages.filter(m => m.role === "user").pop();
        if (lastUser) {
          episodes = await queryEpisodes(lastUser.content, event.workspace);
        }
      } catch (e) {
        console.error("[memory] failed to query episodes:", e.message);
      }

      const episodesBlock = episodes.map(e => e.summary).join("\n\n") || "(none)";

      let memoryBlock = `<memory>
<memory-facts>
${factsBlock}
</memory-facts>
<memory-episodes>
${episodesBlock}
</memory-episodes>
</memory>`;

      // Budget enforcement
      const tokenCount = countTokens(memoryBlock);
      if (tokenCount > budget) {
        // Cut episodes to 1
        if (episodes.length > 1) {
          memoryBlock = memoryBlock.replace(
            /<memory-episodes>[\s\S]*<\/memory-episodes>/,
            `<memory-episodes>\n${episodes[0].summary}\n</memory-episodes>`
          );
        }
        // If still over, truncate facts to budget
        const overhead = countTokens(memoryBlock.replace(/<memory-facts>[\s\S]*<\/memory-facts>/, "<memory-facts></memory-facts>"));
        const maxFactsTokens = budget - overhead;
        const factsLines = factsBlock.split("\n");
        let truncatedFacts = "";
        for (const line of factsLines) {
          truncatedFacts += line + "\n";
          if (countTokens(truncatedFacts) > maxFactsTokens) break;
        }
        memoryBlock = memoryBlock.replace(
          /<memory-facts>[\s\S]*<\/memory-facts>/,
          `<memory-facts>\n${truncatedFacts.trim()}\n</memory-facts>`
        );
      }

      event.system = event.system + "\n" + memoryBlock;
    });

    // --- 3. Initialize episodic DB ---
    try { initEpisodicDb(); } catch (e) { console.error("[memory] init episodes failed:", e.message); }

    // --- 4. Start session collector ---
    startCollector(ctx);

    return () => { stopCollector(); };
  },
});
```

- [ ] **Step 2: Commit**

```bash
git add plugins/memory/index.js
git commit -m "feat(memory): plugin entry point with context hook, tool registration, collector"
```

---

### Task 3: Factual Memory Tools (`tools.js`)

**Files:**
- Create: `plugins/memory/tools.js`

- [ ] **Step 1: Write the tools module**

```js
import { writeFact, updateFact, deleteFact, createCategory } from "./context.js";

export function registerFactualTools() {
  return [
    {
      name: "memory.write",
      schema: {
        type: "object",
        properties: {
          category: { type: "string", description: "Memory category (preferences, facts, conventions, people)" },
          key: { type: "string", description: "Unique key within the category" },
          value: { type: "string", description: "The factual content to store" }
        },
        required: ["category", "key", "value"]
      },
      handler: async ({ category, key, value }) => {
        writeFact(category, key, value);
        return `Stored: ${category}/${key}`;
      }
    },
    {
      name: "memory.update",
      schema: {
        type: "object",
        properties: {
          category: { type: "string", description: "Memory category" },
          key: { type: "string", description: "Key of the entry to update" },
          patch: { type: "string", description: "Text to append to the existing value" }
        },
        required: ["category", "key", "patch"]
      },
      handler: async ({ category, key, patch }) => {
        updateFact(category, key, patch);
        return `Updated: ${category}/${key}`;
      }
    },
    {
      name: "memory.delete",
      schema: {
        type: "object",
        properties: {
          category: { type: "string", description: "Memory category" },
          key: { type: "string", description: "Key of the entry to delete" }
        },
        required: ["category", "key"]
      },
      handler: async ({ category, key }) => {
        deleteFact(category, key);
        return `Deleted: ${category}/${key}`;
      }
    },
    {
      name: "memory.create_category",
      schema: {
        type: "object",
        properties: {
          name: { type: "string", description: "Name for the new memory category" },
          description: { type: "string", description: "Human-readable description of the category" }
        },
        required: ["name", "description"]
      },
      handler: async ({ name, description }) => {
        createCategory(name, description);
        return `Created category: ${name}`;
      }
    }
  ];
}
```

- [ ] **Step 2: Commit**

```bash
git add plugins/memory/tools.js
git commit -m "feat(memory): factual memory tool definitions (write, update, delete, create_category)"
```

---

### Task 4: Factual Memory Context (`context.js`)

**Files:**
- Create: `plugins/memory/context.js`

- [ ] **Step 1: Write the context module — path resolution + token counting**

```js
import fs from "node:fs";
import path from "node:path";
import { createEncoder } from "tiktoken";

const GLOBAL_OPencode_DIR = path.join(process.env.USERPROFILE || process.env.HOME, ".opencode");
const DEFAULT_CATEGORIES = ["preferences", "facts", "conventions", "people"];

export function getGlobalFactsDir() {
  return path.join(GLOBAL_OPencode_DIR, "memory", "facts");
}

export function getWorkspaceFactsDir(workspace) {
  if (!workspace) return null;
  return path.join(workspace, ".opencode", "memory", "facts");
}

function getEncoder() {
  return createEncoder("cl100k_base");
}

export function countTokens(text) {
  const encoder = getEncoder();
  return encoder.encode(text).length;
}
```

- [ ] **Step 2: Write fact file CRUD operations**

```js
// Append this to the end of context.js:

export function writeFact(category, key, value) {
  const globalDir = getGlobalFactsDir();
  ensureDir(globalDir);
  const filePath = path.join(globalDir, `${category}.md`);

  let content = "";
  if (fs.existsSync(filePath)) {
    content = fs.readFileSync(filePath, "utf8");
  }

  if (!content || content.trim() === "") {
    content = `Category: ${category}\n---\n`;
  }

  const lines = content.split("\n");
  const sepIdx = lines.indexOf("---");
  const keyRegex = new RegExp(`^${escapeRegex(key)}:\\s*`);
  const existingIdx = sepIdx >= 0 ? lines.slice(sepIdx + 1).findIndex(l => keyRegex.test(l)) : -1;

  if (existingIdx >= 0) {
    lines[sepIdx + 1 + existingIdx] = `${key}: ${value}`;
  } else {
    lines.push(`${key}: ${value}`);
  }

  fs.writeFileSync(filePath, lines.join("\n") + "\n");
}

export function updateFact(category, key, patch) {
  const globalDir = getGlobalFactsDir();
  const filePath = path.join(globalDir, `${category}.md`);
  if (!fs.existsSync(filePath)) return;

  let content = fs.readFileSync(filePath, "utf8");
  const keyPattern = new RegExp(`^(${escapeRegex(key)}:\\s*)(.+)$`, "m");
  const match = content.match(keyPattern);
  if (!match) return;

  const newValue = match[2] + " " + patch.trimStart();
  content = content.replace(keyPattern, `$1${newValue}`);
  fs.writeFileSync(filePath, content);
}

export function deleteFact(category, key) {
  const globalDir = getGlobalFactsDir();
  const filePath = path.join(globalDir, `${category}.md`);
  if (!fs.existsSync(filePath)) return;

  let content = fs.readFileSync(filePath, "utf8");
  const keyLine = new RegExp(`^${escapeRegex(key)}:.*\n?`, "m");
  content = content.replace(keyLine, "");
  fs.writeFileSync(filePath, content);
}

export function createCategory(name, description) {
  const globalDir = getGlobalFactsDir();
  ensureDir(globalDir);
  const filePath = path.join(globalDir, `${name}.md`);
  if (fs.existsSync(filePath)) return;

  fs.writeFileSync(filePath, `Category: ${name}\nDescription: ${description}\n---\n`);
}
```

- [ ] **Step 3: Write category scanning + memory block builder**

```js
// Append this to the end of context.js:

function scanCategories(dir) {
  if (!dir || !fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.endsWith(".md"))
    .map(f => f.replace(".md", ""))
    .sort();
}

function readFactEntries(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  return content
    .split("\n")
    .filter(line => line && !line.startsWith("Category:") && !line.startsWith("Description:") && line !== "---" && line.trim() !== "")
    .map(line => line.trim())
    .join("\n");
}

export function buildMemoryFactsBlock(workspace) {
  const globalDir = getGlobalFactsDir();
  const workspaceDir = getWorkspaceFactsDir(workspace);

  const categories = [...new Set([
    ...scanCategories(globalDir),
    ...scanCategories(workspaceDir)
  ])].sort();

  if (categories.length === 0) {
    return "Categories: (none)";
  }

  const lines = [];
  lines.push(`Categories: ${categories.join(", ")}`);
  lines.push("---");

  for (const name of categories) {
    lines.push(`\n### ${name}`);

    const globalFile = path.join(globalDir, `${name}.md`);
    if (fs.existsSync(globalFile)) {
      lines.push(readFactEntries(globalFile));
    }

    if (workspaceDir) {
      const wsFile = path.join(workspaceDir, `${name}.md`);
      if (fs.existsSync(wsFile)) {
        lines.push(readFactEntries(wsFile));
      }
    }
  }

  return lines.join("\n");
}

// Helpers
function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
```

- [ ] **Step 4: Commit**

```bash
git add plugins/memory/context.js
git commit -m "feat(memory): factual memory context — CRUD, category scanning, fact block builder, token counting"
```

---

### Task 5: Episodic Memory — SQLite + Vector Search (`episodic.js`)

**Files:**
- Create: `plugins/memory/episodic.js`

- [ ] **Step 1: Write DB initialization and schema**

```js
import fs from "node:fs";
import path from "node:path";
import Database from "better-sqlite3";
import sqliteVec from "sqlite-vec";

const GLOBAL_OPencode_DIR = path.join(process.env.USERPROFILE || process.env.HOME, ".opencode");
const EPISODES_DIR = path.join(GLOBAL_OPencode_DIR, "memory", "episodes");

let db = null;
let wsDbs = new Map(); // workspace -> db

export function initEpisodicDb(workspace) {
  const base = workspace || EPISODES_DIR;
  if (db && !workspace) return db;

  const epDir = workspace
    ? path.join(workspace, ".opencode", "memory", "episodes")
    : EPISODES_DIR;

  fs.mkdirSync(epDir, { recursive: true });

  const gitignore = path.join(epDir, ".gitignore");
  if (!fs.existsSync(gitignore)) {
    fs.writeFileSync(gitignore, "episodes.db\n");
  }

  const dbPath = path.join(epDir, "episodes.db");
  const newDb = new Database(dbPath);
  sqliteVec.initUnsafe(newDb);

  newDb.exec(`
    CREATE TABLE IF NOT EXISTS episodes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      summary TEXT NOT NULL,
      embedding BLOB NOT NULL,
      workspace TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS episodes_vec USING vec0(
      id INTEGER PRIMARY KEY,
      embedding F32[384]
    );
  `);

  if (!workspace) {
    db = newDb;
  } else {
    wsDbs.set(workspace, newDb);
  }

  return newDb;
}
```

- [ ] **Step 2: Write ONNX embedding function**

```js
// Append to episodic.js:

import { InferenceSession, Tensor } from "onnxruntime-node";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
let onnxSession = null;

export async function getEmbedding(text) {
  if (!onnxSession) {
    const modelPath = path.join(__dirname, "assets", "model.onnx");
    onnxSession = await InferenceSession.create(modelPath);
  }

  const tokens = tokenizeSimple(text);
  const inputTensor = new Tensor("int64", tokens, [1, tokens.length]);
  const feeds = { input_ids: inputTensor };
  const results = await onnxSession.run(feeds);
  const outputTensor = results[Object.keys(results)[0]];

  const raw = Array.from(outputTensor.data);
  const magn = Math.sqrt(raw.reduce((s, v) => s + v * v, 0)) || 1;
  return raw.map(v => v / magn);
}

function tokenizeSimple(text) {
  return text
    .toLowerCase()
    .split(/[\s,./;:'"?!()\-]+/)
    .filter(t => t.length > 0)
    .map(t => {
      let h = 5381;
      for (let i = 0; i < t.length; i++) {
        h = ((h << 5) + h) ^ t.charCodeAt(i);
      }
      return Math.abs(h) % 30000;
    });
}
```

- [ ] **Step 3: Write store and query operations**

```js
// Append to episodic.js:

export async function storeEpisode(summary, workspace) {
  const targetDb = initEpisodicDb(workspace);
  const embedding = await getEmbedding(summary);
  const embeddingBuf = new Float32Array(embedding).buffer;

  const stmt = targetDb.prepare(`
    INSERT INTO episodes (summary, embedding, workspace)
    VALUES (?, ?, ?)
  `);
  const id = stmt.run(summary, embeddingBuf, workspace || null).lastInsertRowid;

  const syncStmt = targetDb.prepare(`
    INSERT INTO episodes_vec (id, embedding)
    VALUES (?, ?)
  `);
  syncStmt.run(id, embeddingBuf);
}

export async function queryEpisodes(userMessage, workspace) {
  const queryEmbedding = await getEmbedding(userMessage);
  const queryBuf = new Float32Array(queryEmbedding).buffer;

  const results = [];

  // Global episodes
  const globalDb = initEpisodicDb();
  const globalRows = globalDb.prepare(`
    SELECT e.summary, e.workspace
    FROM episodes e
    JOIN episodes_vec ev ON ev.id = e.id
    ORDER BY vec_distance_cosine(ev.embedding, ?)
    LIMIT 3
  `).all(queryBuf);
  results.push(...globalRows);

  // Workspace-specific episodes
  if (workspace) {
    const wsDb = initEpisodicDb(workspace);
    const wsRows = wsDb.prepare(`
      SELECT e.summary, e.workspace
      FROM episodes e
      JOIN episodes_vec ev ON ev.id = e.id
      ORDER BY vec_distance_cosine(ev.embedding, ?)
      LIMIT 3
    `).all(queryBuf);
    results.push(...wsRows);
  }

  // Deduplicate and limit to 3
  const seen = new Set();
  return results.filter(r => {
    if (seen.has(r.summary)) return false;
    seen.add(r.summary);
    return true;
  }).slice(0, 3);
}
```

- [ ] **Step 4: Commit**

```bash
git add plugins/memory/episodic.js
git commit -m "feat(memory): episodic memory — SQLite + sqlite-vec init, ONNX embedding, vector search, RAG query"
```

---

### Task 6: Session Collector (`collector.js`)

**Files:**
- Create: `plugins/memory/collector.js`

- [ ] **Step 1: Write the collector module**

```js
import { storeEpisode } from "./episodic.js";

let turns = [];
let inactivityTimer = null;
let ctxRef = null;
const INACTIVITY_MS = 5 * 60 * 1000;

export function startCollector(ctx) {
  ctxRef = ctx;

  ctx.session.hook("context", (event) => {
    const lastUser = [...event.messages].reverse().find(m => m.role === "user");
    if (lastUser) {
      turns.push(lastUser.content);
      resetInactivity();
    }
  });
}

export function stopCollector() {
  clearTimeout(inactivityTimer);
  flushTurns();
}

function resetInactivity() {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(flushTurns, INACTIVITY_MS);
}

async function flushTurns() {
  if (turns.length === 0) return;
  const segment = turns.join("\n\n");
  turns = [];

  try {
    const summary = await summarizeSegment(segment);
    if (!summary) return;
    await storeEpisode(summary, null);
    console.log("[memory:collector] stored episode:", summary.substring(0, 80) + "...");
  } catch (e) {
    console.error("[memory:collector] failed to store episode:", e.message);
  }
}

async function summarizeSegment(segment) {
  if (!ctxRef) return segment.substring(0, 500);

  try {
    const result = await ctxRef.session.prompt({
      noReply: true,
      messages: [{
        role: "user",
        content: `Summarize this conversation segment in 2-3 sentences. Focus on key decisions, facts discovered, and actions taken:\n\n${segment.substring(0, 4000)}`
      }]
    });
    if (result && result.content) return result.content;
  } catch (e) {
    console.error("[memory:collector] summarization failed:", e.message);
  }
  return segment.substring(0, 500);
}
```

- [ ] **Step 2: Commit**

```bash
git add plugins/memory/collector.js
git commit -m "feat(memory): session collector — turn capture, inactivity timer, compacting summary"
```

---

### Task 7: Embedding Model Assets

**Files:**
- Create: `plugins/memory/assets/model.onnx`
- Create: `plugins/memory/assets/tokenizer.json`
- Create: `plugins/memory/assets/vocab.txt`

- [ ] **Step 1: Install huggingface_hub**

```powershell
pip install huggingface_hub
```

- [ ] **Step 2: Download ONNX model from HuggingFace**

```python
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='sentence-transformers/all-MiniLM-L6-v2',
    allow_patterns=['onnx/model.onnx', 'tokenizer.json', 'vocab.txt'],
    local_dir='plugins/memory/assets',
    local_dir_use_symlinks=False
)
"
```

- [ ] **Step 3: Rename the ONNX file to match the expected path**

```powershell
if (Test-Path "plugins\memory\assets\onnx\model.onnx") {
    Move-Item "plugins\memory\assets\onnx\model.onnx" "plugins\memory\assets\model.onnx"
    Remove-Item "plugins\memory\assets\onnx" -Recurse -Force
}
```

- [ ] **Step 4: Verify assets are present and non-empty**

```powershell
Get-ChildItem "plugins\memory\assets\" | ForEach-Object {
    Write-Host "$($_.Name): $($_.Length) bytes"
}
# Expected: model.onnx ~47MB, tokenizer.json ~700KB, vocab.txt ~232KB
```

- [ ] **Step 5: Commit**

```bash
git add plugins/memory/assets/*.onnx plugins/memory/assets/*.json plugins/memory/assets/*.txt
git commit -m "feat(memory): bundle all-MiniLM-L6-v2 ONNX model assets"
```

---

### Task 8: Build Prompt Memory Section

**Files:**
- Modify: `.opencode/prompts/build.txt` (append after the `# Environment Notes` section, before the closing `<example>`)

- [ ] **Step 1: Append the Memory section**

Insert this block after line 91 (`# Environment Notes`) of `.opencode/prompts/build.txt`:

```text
# Memory

You have access to injected memory tools and context blocks:

**Factual memory tools** — use these to manage persistent knowledge:
- `memory.write` — store a new fact, preference, or convention
- `memory.update` — append or modify an existing entry
- `memory.delete` — retire a stale entry
- `memory.create_category` — create a new category when existing ones don't fit

**Memory blocks in your system prompt:**
- `<memory-facts>` — factual knowledge you stored in past sessions. Treat as ground truth; don't contradict stored preferences.
- `<memory-episodes>` — relevant past conversations injected by semantic similarity. Use patterns and decisions from these episodes to inform your current work.

Episodic memory is automatic — you do not need to manage it. The plugin captures and recalls relevant past sessions on your behalf.

```

- [ ] **Step 2: Verify the section was appended correctly**

Read `.opencode/prompts/build.txt` and confirm the `# Memory` section appears after `# Environment Notes` and before the closing `<example>`.

- [ ] **Step 3: Commit**

```bash
git add .opencode/prompts/build.txt
git commit -m "docs(build): add Memory section to build prompt"
```

---

### Task 9: Schedules Plugin Skeleton

**Files:**
- Create: `plugins/schedules/index.js`

- [ ] **Step 1: Write the skeleton**

```js
import { Plugin } from "@opencode-ai/plugin";

export default Plugin.define({
  id: "schedules",
  setup: async (ctx) => {
    // TODO: schedules plugin implementation
    // Planned tools: schedule.add, schedule.list, schedule.complete
    // Planned context: inject upcoming items into system prompt
  },
});
```

- [ ] **Step 2: Commit**

```bash
git add plugins/schedules/index.js
git commit -m "feat: add schedules plugin skeleton"
```

---

### Task 10: Install Scripts — Plugin Deployment

**Files:**
- Modify: `install.sh` (add plugins block after MCP servers block, before opencode.json config block)
- Modify: `install.ps1` (add plugins block after MCP servers block, before opencode.json config block)

- [ ] **Step 1: Add plugins block to `install.sh`**

Insert after the MCP servers block (`fi` at line ~53), before the opencode.json config block (`# Install opencode.json config`):

```bash
# Install plugins
echo "Installing plugins to $CONFIG_DIR/plugins/..."
if [ -d "$SCRIPT_DIR/plugins" ]; then
  mkdir -p "$CONFIG_DIR/plugins"
  for d in "$CONFIG_DIR/plugins"/*/; do
    [ ! -d "$d" ] && continue
    name="$(basename "$d")"
    if [ ! -d "$SCRIPT_DIR/plugins/$name" ]; then
      echo "  Removing $name (no longer in repo)"
      rm -rf "$d"
    fi
  done
  for d in "$SCRIPT_DIR/plugins"/*/; do
    [ ! -d "$d" ] && continue
    name="$(basename "$d")"
    rm -rf "$CONFIG_DIR/plugins/$name"
    cp -r "$d" "$CONFIG_DIR/plugins/$name"
  done
fi
```

- [ ] **Step 2: Add plugins block to `install.ps1`**

Insert after the MCP servers block (`}` at line ~72), before the opencode.json config block (`# Install opencode.json config`):

```powershell
# Install plugins
Write-Host "Installing plugins to $CONFIG_DIR\plugins\..."
if (Test-Path -LiteralPath "$SCRIPT_DIR\plugins") {
    New-Item -ItemType Directory -Path "$CONFIG_DIR\plugins" -Force | Out-Null
    $repoPlugins = Get-ChildItem -Directory -LiteralPath "$SCRIPT_DIR\plugins"
    $configPlugins = Get-ChildItem -Directory -LiteralPath "$CONFIG_DIR\plugins" -ErrorAction SilentlyContinue

    foreach ($d in $configPlugins) {
        $name = $d.Name
        if (-not ($repoPlugins.Name -contains $name)) {
            Write-Host "  Removing $name (no longer in repo)"
            Remove-Item -LiteralPath $d.FullName -Recurse -Force
        }
    }

    foreach ($d in $repoPlugins) {
        $name = $d.Name
        $dest = "$CONFIG_DIR\plugins\$name"
        if (Test-Path -LiteralPath $dest) {
            Remove-Item -LiteralPath $dest -Recurse -Force
        }
        Copy-Item -LiteralPath $d.FullName -Destination $dest -Recurse -Force
    }
}
```

- [ ] **Step 3: Update the final count in both scripts**

In `install.sh`, replace the last `echo "Done..."` line:

```bash
echo "Done. $(ls -d "$CONFIG_DIR/skills/"*/ 2>/dev/null | wc -l) skills, $(ls "$CONFIG_DIR/agents/"*.md 2>/dev/null | wc -l) agents, $(ls -d "$CONFIG_DIR/plugins/"*/ 2>/dev/null | wc -l) plugins installed."
```

In `install.ps1`, replace the last `Write-Host "Done..."` line:

```powershell
$s = (Get-ChildItem -Directory -LiteralPath "$CONFIG_DIR\skills" -ErrorAction SilentlyContinue).Count
$agentCount = (Get-ChildItem -File -Filter "*.md" -LiteralPath "$CONFIG_DIR\agents" -ErrorAction SilentlyContinue).Count
$pluginCount = (Get-ChildItem -Directory -LiteralPath "$CONFIG_DIR\plugins" -ErrorAction SilentlyContinue).Count
Write-Host "Done. $s skills, $agentCount agents, $pluginCount plugins installed."
```

- [ ] **Step 4: Commit**

```bash
git add install.sh install.ps1
git commit -m "ops: add plugins deployment to install scripts"
```

---

### Task 11: Update `.gitignore`

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Append plugin ignores**

Add these lines to the end of `.gitignore`:

```gitignore
# Plugin local deps
plugins/*/node_modules/
plugins/*/.cache/

# Episode databases (generated at runtime)
*.db
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "ops: add plugin-specific entries to .gitignore"
```

---

### Task 12: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update the Repository Structure section**

In `AGENTS.md`, replace the existing structure block:

```markdown
## Repository Structure

```
skills/          — 34 skill directories (each: SKILL.md + optional scripts/, references/, assets/)
agents/          — 11 agent definition files (YAML-frontmatter Markdown, *.md) + LICENSE.txt
plugins/         — 2 plugin definitions (memory: full; schedules: skeleton)
.opencode/       — Local opencode config (opencode.json, prompts/, command/)
```
```

- [ ] **Step 2: Add a plugin infrastructure section**

Insert after `## Key Facts`, before `### Skills are Markdown files, not code`:

```markdown
### Plugin infrastructure

`plugins/` contains V2 plugin definitions deployed to `~/.config/opencode/plugins/` by the install scripts. Opencode auto-discovers plugins in that directory. Each plugin is a Node.js ESM package with `package.json` and `index.js` that exports `Plugin.define({ id, setup })`.

**Plugins in this repo:**
- `memory` — factual CRUD tools + context injection, episodic SQLite + ONNX vector search + RAG injection, session collector
- `schedules` — skeleton placeholder (next iteration)

The install scripts deploy plugins the same way as skills: copy from repo to config dir, remove stale plugins no longer in the repo.
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: document plugin infrastructure in AGENTS.md"
```