---
name: writing-release-notes
description: Use when preparing anything that announces a release to the people who consume it — CHANGELOG entries, GitHub release descriptions, version announcements, upgrade or migration guides, or deprecation notices. Triggers include "write the changelog", "release notes for v2.3", "summarize what changed since the last release", "what do users need to know about this upgrade", and cutting a tag.
---

# Writing Release Notes

## Overview

The default failure is a pasted commit log. It is accurate, complete, and useless — because it describes what happened to the code, and the reader needs to know what happened to them.

**Core principle:** The reader is deciding two things — should I upgrade, and what will break if I do. Every line either serves one of those decisions or is noise.

**Companion skills:** `writing-internal-comms` for audiences inside the org, `coauthoring-docs` for the documentation an entry links to, `evolving-apis-and-schemas` when the release contains a breaking change.

## The Iron Law

```
EVERY ENTRY STATES WHAT CHANGED FOR THE READER, NOT WHAT CHANGED IN THE CODE
```

`Refactored the auth middleware to use the new token store` is a commit message. `Sessions now survive a server restart` is a release note. Same change, and only one of them answers a question the reader has.

If an entry has no reader-visible effect, it does not go in release notes at all. The commit log already exists and is one click away.

## Step 1: Know Which Document You Are Writing

Three different artifacts get called "release notes". Mixing them serves nobody.

| Document | Audience | Shape |
|---|---|---|
| **CHANGELOG** | Anyone auditing history | Terse, cumulative, one line per change, grouped by type, newest version first |
| **Release notes** | People deciding whether to upgrade now | Highlights first, then the full list. Prose for the top items |
| **Upgrade guide** | People who already decided | Only breaking changes, each with before/after and steps |

A small library needs only a CHANGELOG. A release with breaking changes needs all three, and the release notes link to the upgrade guide rather than inlining it.

## Step 2: Gather, Then Translate

```bash
git log --oneline v1.4.0..HEAD
git log v1.4.0..HEAD --format='%s%n%b' | grep -iE 'BREAKING|deprecat'
git diff v1.4.0..HEAD --stat -- '*.proto' 'migrations/' 'openapi.yaml'
```

That last command is the one that matters most: it finds the interface changes that the commit subjects usually fail to mention.

Then translate every candidate through one question: **what can the reader do now that they could not do before, or what will now behave differently?** If there is no answer, drop it.

## Step 3: Categorize

Use these six, in this order, and omit any that are empty. Breaking changes lead — always, regardless of how minor they seem relative to the rest.

| Category | Contains |
|---|---|
| **Breaking** | Anything requiring the reader to change code, config, or data |
| **Added** | New capability |
| **Changed** | Existing behavior that is different but compatible |
| **Deprecated** | Still works, will be removed — with the version it goes away in |
| **Removed** | Gone, previously deprecated |
| **Fixed** | Bugs, described by the symptom the reader saw |
| **Security** | Always its own section, always near the top, never buried in Fixed |

**Deprecations need a date or a version, not "soon".** A deprecation notice without a removal target gets ignored, and then removal is a surprise.

**Security entries state severity and whether action is required.** If a CVE is assigned, include it. If exploitation requires a specific configuration, say which — readers need to know if they were affected, not only that they should upgrade.

## Step 4: Write the Entries

Each entry: what changed, for whom, and the link to detail. One line in a CHANGELOG; two or three sentences for a headline feature.

| Instead of | Write |
|---|---|
| `Fix null pointer in handler` | Fixed a crash when uploading a file with no extension |
| `Bump deps` | Updated to OpenSSL 3.2.1, resolving CVE-2024-XXXX (no action required) |
| `Add caching layer` | Dashboard queries now return in under 200ms for workspaces with 10k+ documents |
| `Refactor config parsing` | *(omit — no reader-visible effect)* |
| `Change API response` | **Breaking:** `GET /documents` now returns `items` instead of `results`. Update clients before upgrading; see the upgrade guide |
| `Improve performance` | Import of a 100MB CSV is roughly 4× faster (was ~90s, now ~22s on the reference dataset) |

**Rules that carry most of the quality:**

- **Lead with the effect, not the mechanism.** The reader cares about the restart, not the token store.
- **Quantify.** "Faster" is unverifiable; "90s → 22s on a 100MB import" is a claim someone can check, and it is far more persuasive.
- **Name the symptom for bug fixes.** Readers search release notes for the problem they hit, using the words they would use for it.
- **Say when action is required.** Most entries need nothing; the ones that do must be unmissable.
- **Link, don't inline.** Migration steps, benchmarks, and API details belong in linked docs.
- **Past tense, active voice, no marketing.** "Sessions now survive a restart." Not "We're thrilled to announce a revolutionary new session experience."

## Step 5: Breaking Changes Get Migration Steps

An entry that says something broke without saying what to do is an incomplete entry.

````markdown
### Breaking

**`GET /documents` renames `results` to `items`**

The list envelope now matches every other collection endpoint.

Before:
```json
{ "results": [...], "total": 42 }
```

After:
```json
{ "items": [...], "total": 42 }
```

**Migration:** update clients to read `items`. The old field is still present
in 2.x and will be removed in 3.0. Clients reading `results` continue to work
until then, with a `Deprecation` header on every response.
````

Best case, the migration is a command — `npx my-tool codemod v3` — and you say so. Second best, it is a diff. Worst acceptable case, it is prose. "Users should update their integrations" is not any of these.

## Format

```markdown
## [2.3.0] — 2026-03-14

### Security
- Fixed a path traversal in the archive importer that allowed writing outside
  the workspace directory (CVE-2026-XXXXX, high). Affects 2.0–2.2 with imports
  enabled. **Upgrade recommended.**

### Breaking
- `GET /documents` returns `items` instead of `results` ([upgrade guide](./UPGRADE.md#23))

### Added
- Full-text search across document bodies, with `search:` filters
- `--dry-run` on `import`, printing what would change without writing

### Changed
- Dashboard queries return in under 200ms for workspaces above 10k documents
- Default session lifetime is now 30 days (was 7); override with `SESSION_TTL`

### Deprecated
- `results` in list responses — removed in 3.0
- `POST /documents/bulk` — use `POST /documents` with an array; removed in 3.0

### Fixed
- Uploading a file with no extension no longer crashes the worker
- Timestamps in exports use the workspace timezone rather than UTC

**Full diff:** [v2.2.1...v2.3.0](https://github.com/org/repo/compare/v2.2.1...v2.3.0)
```

Keep dates in ISO form and versions in brackets — that combination is what makes a CHANGELOG mechanically parseable, which downstream tooling relies on.

## Version Signaling

The number is part of the message. Under semver, a breaking change means a major bump — shipping one in a minor release costs more trust than the delay of doing it properly. If the project is pre-1.0 or uses a different scheme, say so at the top of the CHANGELOG so readers can calibrate.

## Common Mistakes

**Pasting the commit log.** Complete, chronological, unreadable, and it leaks internal naming to people who have no idea what `ToolGateway` is.

**Burying the breaking change** in the middle of a list because it was a small diff. Diff size is unrelated to reader impact.

**Omitting the fix nobody reported.** Someone hit it and never filed. Release notes are how they find out it is fixed.

**"Various bug fixes and improvements."** Says nothing, and reads as a release nobody bothered to document.

**Internal vocabulary.** Module names, ticket numbers, and service names that mean nothing outside the team.

**Listing dependency bumps individually.** Group them, unless one carries a security fix or a behavior change — then it is its own entry.

**No date.** Readers use dates to reason about what they are running.

**Writing it at tag time from memory.** Add the entry with the change, while the reader-visible effect is still obvious.
