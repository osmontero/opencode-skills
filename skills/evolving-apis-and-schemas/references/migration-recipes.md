# Migration Recipes

Worked expand/contract sequences for the changes that come up most. Each phase is a separate, independently deployable release.

## Contents

- Add a NOT NULL column
- Rename a column
- Change a column's type
- Split one column into two
- Drop a column
- SQLite: the table rebuild procedure
- Add a proto field with presence
- Remove a proto field
- Batched backfill pattern

## Add a NOT NULL Column

The direct form rewrites the table and rejects every existing row.

```sql
-- Phase 1 — EXPAND: nullable, cheap, revertible
ALTER TABLE documents ADD COLUMN tenant_id uuid;
-- Application: write tenant_id on every insert/update. Read paths tolerate NULL.

-- Phase 2 — MIGRATE: backfill in batches (see the pattern at the end), then
-- constrain without a long exclusive lock:
ALTER TABLE documents
  ADD CONSTRAINT documents_tenant_id_not_null
  CHECK (tenant_id IS NOT NULL) NOT VALID;          -- instant, no scan
ALTER TABLE documents VALIDATE CONSTRAINT documents_tenant_id_not_null;
                                                    -- scans under a weak lock
ALTER TABLE documents ALTER COLUMN tenant_id SET NOT NULL;
                                                    -- PG 12+: uses the constraint, no scan
ALTER TABLE documents DROP CONSTRAINT documents_tenant_id_not_null;
```

## Rename a Column

There is no safe in-place rename. It is an add, a dual-write, and a drop.

```sql
-- Phase 1 — EXPAND
ALTER TABLE users ADD COLUMN display_name text;
-- Application: write BOTH display_name and name. Read name.

-- Phase 2 — MIGRATE
UPDATE users SET display_name = name WHERE display_name IS NULL;  -- batched
-- Application: read display_name, still write both.

-- Phase 3 — CONTRACT (only after confirming nothing reads or writes `name`)
ALTER TABLE users DROP COLUMN name;
```

The tempting shortcut — a view or a generated column aliasing the old name — leaves you with two names forever and does not remove the coordination problem, only hides it.

## Change a Column's Type

Same shape as a rename; the new column carries the new type.

```sql
-- Phase 1
ALTER TABLE events ADD COLUMN payload_jsonb jsonb;
-- Application: write both payload (text) and payload_jsonb.

-- Phase 2: backfill with explicit, validated conversion
UPDATE events SET payload_jsonb = payload::jsonb
 WHERE payload_jsonb IS NULL AND id BETWEEN $1 AND $2;
-- Rows that fail to convert are the finding. Do not silently skip them —
-- record them and decide deliberately.

-- Phase 3
ALTER TABLE events DROP COLUMN payload;
ALTER TABLE events RENAME COLUMN payload_jsonb TO payload;   -- optional 4th deploy
```

Widening (`int` → `bigint`, `varchar(50)` → `text`) is the exception: it is a metadata-only change in PostgreSQL when no index or constraint depends on the width. Narrowing never is.

## Split One Column Into Two

```sql
-- Phase 1
ALTER TABLE contacts ADD COLUMN given_name text, ADD COLUMN family_name text;
-- Application: on write, populate all three (full_name plus the two parts).

-- Phase 2: backfill, then switch reads. The split logic is lossy —
-- decide what happens to "Maria de la Cruz Santos" BEFORE running it,
-- and keep full_name as the source of truth until you have sampled the output.

-- Phase 3: drop full_name.
```

Any backfill involving parsing needs a sampled review of the output before phase 3. This is the case where "the migration succeeded" and "the data is right" differ most.

## Drop a Column

```sql
-- Phase 1: remove every read from the application. Deploy. Verify.
-- Phase 2: remove every write. Deploy. Verify with a query, not a grep:
SELECT count(*) FROM documents
 WHERE legacy_flag IS NOT NULL AND updated_at > now() - interval '7 days';
-- Phase 3:
ALTER TABLE documents DROP COLUMN legacy_flag;
```

In PostgreSQL, `DROP COLUMN` is fast and does not reclaim space — the data remains until a rewrite. That is not a backup, and it is not accessible through SQL.

## SQLite: The Table Rebuild Procedure

SQLite supports only `ADD COLUMN`, `RENAME COLUMN`, `RENAME TABLE`, and `DROP COLUMN`. Anything else — changing a type, adding `NOT NULL` to an existing column, adding or removing a constraint, reordering — requires a rebuild. The ordering below is the one from the SQLite documentation; deviating from it with foreign keys enabled can silently drop rows.

```sql
PRAGMA foreign_keys = OFF;      -- must be outside the transaction
BEGIN;

-- 1. Create the new table under a temporary name, with the desired shape
CREATE TABLE documents_new (
  id         INTEGER PRIMARY KEY,
  tenant_id  TEXT NOT NULL,
  title      TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

-- 2. Copy the data, supplying values for anything newly required
INSERT INTO documents_new (id, tenant_id, title, created_at)
SELECT id, COALESCE(tenant_id, 'default'), title, created_at FROM documents;

-- 3. Swap
DROP TABLE documents;
ALTER TABLE documents_new RENAME TO documents;

-- 4. Recreate indexes, triggers, and views — DROP TABLE took them with it
CREATE INDEX idx_documents_tenant ON documents(tenant_id);

COMMIT;
PRAGMA foreign_keys = ON;
```

`PRAGMA foreign_key_check;` before committing is worth the extra statement — it is the only thing that will tell you the rebuild orphaned a reference.

Note `ADD COLUMN` restrictions: no `NOT NULL` without a non-null default, no `PRIMARY KEY`, no `UNIQUE`, and any default must be a constant. `ALTER TABLE ADD COLUMN ... DEFAULT CURRENT_TIMESTAMP` is rejected.

## Add a Proto Field With Presence

```proto
message Document {
  string id = 1;
  string title = 2;

  // New. `optional` gives real presence — you can distinguish
  // "not sent by an old client" from "explicitly set to empty".
  optional string summary = 10;
}
```

Pick a number above anything ever used, including reserved ranges. Server code must treat absence as "the client is old", not as "the user cleared it" — that distinction is the entire reason for `optional`.

## Remove a Proto Field

```proto
message Document {
  // Phase 1: mark deprecated, stop reading it, keep writing it.
  string legacy_owner = 4 [deprecated = true];
}

message Document {
  // Phase 2 (after every client is updated): remove the field and
  // reserve both the number and the name. Forever.
  reserved 4;
  reserved "legacy_owner";
}
```

Reusing number 4 later means old messages on the wire — or in a persisted log — decode their old `legacy_owner` bytes into the new field. There is no error; the value is simply wrong.

## Batched Backfill Pattern

Resumable, bounded, and safe to stop at any point.

```sql
-- Repeat until zero rows are affected. Key off the primary key, not OFFSET.
UPDATE documents SET tenant_id = o.tenant_id
  FROM orgs o
 WHERE documents.org_id = o.id
   AND documents.tenant_id IS NULL
   AND documents.id IN (
       SELECT id FROM documents WHERE tenant_id IS NULL ORDER BY id LIMIT 5000
   );
```

Rules that make the difference:

- **Batch size in the low thousands.** Large enough to finish, small enough that each statement's locks are brief.
- **Sleep between batches** on a busy table — replication lag is the usual casualty of a tight loop.
- **Idempotent**: the `IS NULL` predicate means a re-run after a crash is free.
- **Track progress** in a table or log, so the job can be resumed rather than restarted.
- **Never `OFFSET`**: it re-scans, so the job gets slower with every batch.
