---
name: evolving-apis-and-schemas
description: Use when changing anything other systems or stored data already depend on — editing a .proto file, writing a database migration, adding or dropping a column, renaming a field, changing a response shape, changing an enum, or altering a queue message format. Triggers include "will this break clients", "is this backward compatible", "buf breaking", "ALTER TABLE", "migration", "deprecate this endpoint", and any change to a published API version.
---

# Evolving APIs and Schemas

## Overview

A schema change is a distributed-systems problem wearing a one-line diff. The code that reads your data is not only the code you are about to deploy — it is also the version still running during the rollout, the client you do not control, and the rows written by last year's binary.

**Core principle:** Old readers and new readers must both be correct at every instant of the rollout. If there is a moment when that is false, the change needs more steps, not more confidence.

**Companion skills:** `writing-plans` for sequencing multi-release changes, `verifying-before-completion` before running anything destructive.

## The Iron Law

```
ADDITIVE FIRST, DESTRUCTIVE LAST — NEVER IN THE SAME DEPLOY
```

Adding is reversible. Dropping, renaming, and narrowing are not. Between them must sit at least one fully deployed release where both shapes work, plus enough time to be sure you will not roll back across it.

**No exceptions:**
- Not for "the old column is definitely unused" — prove it with a query, not a grep
- Not for "we deploy everything together" — rollouts are not atomic, and rollbacks are not either
- Not for "it's a tiny table"
- Not for renames. A rename is a drop and an add, and it is the single most common way to take an outage

## Step 1: Identify Your Consumers

Before classifying the change, list who reads this shape. The answer determines whether expand/contract is optional or mandatory.

| Consumer | Can you redeploy it atomically with the producer? | Consequence |
|---|---|---|
| Same binary, same struct | Yes | Ordinary refactor — compiler catches it |
| Another service you own | **No** — rolling deploys mean both versions run at once | Expand/contract required |
| A client you do not control (SDK, mobile app, third party) | **No, ever** | Version it; the old shape is permanent |
| **Persisted data** | **No — you cannot redeploy a row** | Old-format rows outlive every deploy |
| A queue or event log | No — in-flight messages were written by the old code | Both formats must parse |
| A replica or a peer in a cluster | No — mixed versions during upgrade | Both directions must interoperate |

**The row most often forgotten is persisted data.** Every value already on disk was written by code you no longer run. If the new code cannot read it, you have shipped a corruption bug that only appears on old records.

## Step 2: Classify the Change

| Class | Examples | Requires |
|---|---|---|
| **Safe** | Add an optional field; add a new endpoint, table, or RPC; add an index; widen a type | Ship it |
| **Expand/contract** | Add a required field; rename; change a type; split or merge; drop anything | The three-phase sequence below |
| **Breaking — must version** | Change the meaning of an existing name; remove from a published API; narrow accepted input | A new version, plus a deprecation window |

The distinction between rows two and three: expand/contract works when *you* can eventually update every reader. When you cannot — a shipped mobile app, a public API — the old shape must keep working for as long as the support window says it will.

## Step 3: The Expand/Contract Sequence

Three deploys, in order. Each is independently releasable and independently revertible.

```
1. EXPAND    Add the new shape. Nothing reads it yet.
             Writers write BOTH old and new.        ← revertible
             ─── deploy, verify, let it soak ───
2. MIGRATE   Backfill existing data into the new shape.
             Switch readers to the new shape.
             Writers still write both.              ← revertible
             ─── deploy, verify, let it soak ───
3. CONTRACT  Stop writing the old shape. Drop it.   ← the point of no return
```

**Gates between phases, not just time:** before contracting, confirm with a query that nothing writes the old shape and nothing reads it — application logs, `pg_stat_statements`, or an explicit counter you added in phase 1. "It has been two weeks" is not evidence.

**Backfill is not a migration.** Schema changes (DDL) go in the migration; moving data (DML) goes in a separate, resumable, batched job. A single `UPDATE` over ten million rows holds locks, blows out the WAL, and cannot be resumed after it times out.

Worked recipes for the common cases — add a NOT NULL column, rename, change a type, split a table, SQLite's rebuild procedure: [references/migration-recipes.md](references/migration-recipes.md).

## Protobuf and gRPC

The field **number** is the wire identity. The name is not.

| Change | Verdict |
|---|---|
| Add a field with a new number | Safe |
| Add an RPC, message, or enum value | Safe for readers that tolerate unknowns |
| Delete a field | Safe **only** with `reserved` on both number and name |
| **Reuse a deleted field number** | **Never.** Old data decodes into the wrong field, silently |
| Rename a field | Wire-safe; breaks JSON/text encoding and every generated client |
| Change a field's type | Only within a compatible family; `int32`↔`int64` yes, `int32`↔`sint32` no |
| `singular` ↔ `repeated` | Treat as breaking — the semantics change even where the wire format survives |
| Add `optional` to an existing field | Wire-safe; gives you presence, changes nothing on the wire |
| Renumber an enum value | Breaking |
| Change a message or package name | Breaking — it is part of the service path and the `Any` type URL |
| Remove or rename an RPC | Breaking |

```proto
// Deleting a field: reserve BOTH, forever
message Document {
  reserved 4, 7 to 9;
  reserved "legacy_owner", "old_status";
}
```

```bash
buf breaking --against '.git#branch=main'    # wire this into review, not just CI
```

Enum zero values are the default for anything unset — make the zero value `UNSPECIFIED`, never a meaningful state, or you cannot distinguish "not set" from "set to the first option".

## SQL Schema Changes

The danger is rarely correctness; it is **lock duration**. A statement that needs a brief exclusive lock will queue behind a long-running read, and everything else queues behind it.

```sql
SET lock_timeout = '3s';   -- fail fast instead of blocking the whole table
```

**PostgreSQL:**

| Operation | Cost | Safe form |
|---|---|---|
| `ADD COLUMN` nullable, or with a constant default | Brief lock, no rewrite (PG 11+) | Ship it |
| `ADD COLUMN` with a volatile default | Full rewrite | Add nullable, backfill in batches, then set the default |
| `SET NOT NULL` | Full scan under an exclusive lock | `ADD CONSTRAINT ... CHECK (c IS NOT NULL) NOT VALID` → `VALIDATE CONSTRAINT` → then `SET NOT NULL` is cheap |
| `CREATE INDEX` | Blocks writes for the build | `CREATE INDEX CONCURRENTLY` — outside a transaction; check for an `INVALID` index if it fails |
| `ADD FOREIGN KEY` | Locks both tables to validate | `NOT VALID`, then `VALIDATE CONSTRAINT` |
| `ALTER COLUMN TYPE` | Full rewrite, exclusive | Expand/contract via a new column |
| `DROP COLUMN` | Fast, irreversible | Contract phase only |

**SQLite** supports only `ADD COLUMN`, `RENAME COLUMN`, `RENAME TABLE`, and `DROP COLUMN` — and `ADD COLUMN` rejects `NOT NULL` without a default, `PRIMARY KEY`, and `UNIQUE`. Everything else requires the create-copy-drop-rename rebuild. See the recipes reference for the correct ordering, which matters: getting it wrong with foreign keys enabled silently drops rows.

## HTTP and JSON APIs

- Adding an optional response field is safe **only if** consumers ignore unknown fields. A client validating with `additionalProperties: false` breaks on additions — check before assuming.
- Adding a required request field breaks every existing caller. Add it optional with a default.
- Never repurpose a name. `status` meaning something new is worse than `status_v2`, because nothing fails loudly.
- Error codes and pagination shapes are part of the contract even when they are not in the schema.
- Version at the resource, not the whole API — a global `/v2` forces a rewrite of endpoints that did not change.

## Reversibility

Every migration answers: **how do I undo this at 3am?**

- Additive migrations: the down is a drop. Write it.
- Destructive migrations: there is no down. State that explicitly in the migration file, along with what recovery actually requires — restore from backup, replay from the event log, re-derive from another table.
- Never write a down migration that silently loses data. A migration that "reverses" a drop by recreating an empty column is worse than one that refuses.
- Test the down path against a copy of production data, not an empty dev database.

## Verification

```bash
buf breaking --against '.git#branch=main'                       # proto
migrate up && migrate down 1 && migrate up                      # round-trip
psql -c "EXPLAIN (ANALYZE, BUFFERS) <the query the new index serves>"
```

- Run the migration against a **restored copy of production**, timed. A migration that takes 40ms on 200 dev rows can take 40 minutes on the real table.
- During phase 2, dual-read and compare: read both shapes, log any divergence, and let it run under real traffic before trusting the new one.
- Confirm the old binary still passes its tests against the new schema. That is the rollback path, and it is the one nobody tests.

## Red Flags

- A migration file containing both `ADD` and `DROP`
- `ALTER TABLE ... RENAME` in a codebase with more than one deployable
- A single `UPDATE` with no `WHERE` and no batching
- "The old field is unused" backed by a grep instead of a query
- `CREATE INDEX` without `CONCURRENTLY` on a table anyone is writing to
- A reused proto field number
- A down migration you have never run
- Deploying a schema change and the code that depends on it in the same release

**All of these mean: split it into more deploys.**

## Common Mistakes

**Renaming in place.** The compiler will tell you about your own code and nothing about the other binary that is still running.

**Treating the deploy as atomic.** During a rolling deploy both versions serve traffic — often for many minutes, and indefinitely if the rollout stalls.

**Forgetting old rows.** New code must parse every format ever written, until you have provably rewritten them all.

**Backfilling inside the schema migration.** It holds locks for the duration and cannot be resumed.

**Trusting the ORM's auto-migration.** It generates the destructive form because it does not know about your other readers.

**Skipping the soak.** Phase 3 is irreversible; the only thing protecting you is having run phase 2 long enough to be sure.
