# opencode-setup Skill Comprehensive Update Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the opencode-setup skill to cover all 19+ missing configuration features from the actual OpenCode schema, splitting into SKILL.md + reference.md.

**Architecture:** Split the existing 530-line SKILL.md into a comprehensive main guide (~550 lines) covering all config sections with concise examples, and a new reference.md (~400 lines) with complete tables (LSP servers, keybinds, env vars, model/provider schemas). SKILL.md references reference.md via `{file:./reference.md}`.

**Tech Stack:** Markdown configuration files, OpenCode config schema

---

## File Structure

| File | Responsibility |
|---|---|
| `SKILL.md` | Main configuration guide: all sections, concise examples, cross-references to reference.md |
| `reference.md` | Bundled resource: complete LSP table, keybinds list, env vars, model/provider schemas |

## Task Decomposition

### Task 1: Create reference.md (LSP Servers + Keybinds + Env Vars)

**Files:**
- Create: `skills/opencode-setup/reference.md`

Steps:
1. Write file skeleton with all section headers
2. Fill in LSP servers table (30 built-in servers)
3. Fill in keybinds list (70+ organized by category)
4. Fill in environment variables list (30+)
5. Review and verify completeness

### Task 2: Create reference.md (Model/Provider Schemas)

**Files:**
- Modify: `skills/opencode-setup/reference.md`

Steps:
1. Fill in model capability schema section
2. Fill in provider option schema section
3. Fill in agent variant and options section
4. Review and verify completeness

### Task 3: Rewrite SKILL.md (Header through Precedence)

**Files:**
- Modify: `skills/opencode-setup/SKILL.md`

Steps:
1. Write updated frontmatter and header through config files/locations (add JSONC support)
2. Update precedence order section (add missing layers)

### Task 4: Rewrite SKILL.md (Provider/Model + Custom Provider)

**Files:**
- Modify: `skills/opencode-setup/SKILL.md`

Steps:
1. Update provider/model section with new options (npm, env, whitelist/blacklist, api, setCacheKey)
2. Update custom provider section with model capabilities (attachment, reasoning, cost, modalities, variants)
3. Add model-level options subsection

### Task 5: Rewrite SKILL.md (Permissions through Commands)

**Files:**
- Modify: `skills/opencode-setup/SKILL.md`

Steps:
1. Update permissions section (add `write` key, arbitrary custom keys)
2. Update agents JSON section (add variant, options)
3. Update agents Markdown section (add variant, options, name)
4. Update skills section (add JSON config: paths, urls)
5. Update commands section (add model, subtask, agent)

### Task 6: Rewrite SKILL.md (Rules through TUI Config)

**Files:**
- Modify: `skills/opencode-setup/SKILL.md`

Steps:
1. Update themes section (minimal)
2. Rewrite keybinds section (structure example + reference link)
3. Update TUI personalization (add diff_style, mouse, scroll_acceleration, plugin, plugin_enabled)

### Task 7: Rewrite SKILL.md (New Sections + MCP + LSP + End)

**Files:**
- Modify: `skills/opencode-setup/SKILL.md`

Steps:
1. Add new sections: logLevel, username, tool_output, experimental, enterprise
2. Rewrite LSP section (full schema with env, initialization, boolean shorthand, reference link)
3. Rewrite MCP section (local + remote with OAuth, headers, timeout)
4. Update remaining sections (formatters with environment, compaction with tail_turns/preserve_recent_tokens, plugins with tuple format)
5. Update tips section
6. Final review of complete SKILL.md

### Task 8: Verify and Install

**Files:**
- Verify: `skills/opencode-setup/SKILL.md`
- Verify: `skills/opencode-setup/reference.md`

Steps:
1. Verify line counts are within limits
2. Run install.sh to sync to global config
3. Verify skill loads correctly
