---
name: writing-internal-comms
description: Use when writing communication aimed at colleagues rather than users or customers — 3P updates (Progress/Plans/Problems), status reports, leadership and exec updates, company newsletters, FAQ answers, project updates, incident reports, launch announcements, or policy and reorganization notes. Triggers include "write an update for leadership", "draft the weekly status", "announce this to the company", "write the incident writeup".
license: Complete terms in LICENSE.txt
---

# Writing Internal Communications

## Overview

Internal comms fail in one of two directions: too long to be read, or too vague to be useful. Both come from the same cause — writing what the author knows instead of what the reader needs in order to decide.

**Core principle:** Lead with the conclusion. The reader should get the point from the first sentence and read on only for supporting detail.

## The Iron Law

```
NO INTERNAL COMMS WITHOUT GATHERING THE FACTS FIRST
```

An update assembled from memory is an update full of hedges. Pull the actual state — commits, tickets, threads, metrics, docs — before writing a line. Vague comms are almost always under-researched, not badly written.

If the facts are genuinely unavailable, ask the user for them. Do not paper over the gap with "significant progress was made."

## Checklist

1. **Identify the type** — route to the guideline file below
2. **Identify the audience and their decision** — who reads this, and what do they do differently afterwards?
3. **Gather the facts** — from real sources, with dates and numbers
4. **Draft to the format** — follow the guideline file's structure exactly
5. **Run the compression pass** — see below
6. **Check the tone** — especially for anything about problems, incidents, or people

## Routing

| Request | File |
|---|---|
| Weekly/biweekly team or company update | `examples/3p-updates.md` |
| Company-wide newsletter | `examples/company-newsletter.md` |
| Answering recurring questions | `examples/faq-answers.md` |
| Anything else — announcements, incidents, policy, launches | `examples/general-comms.md` |

**Read the routed file and follow its structure.** These formats exist so readers can skim them the same way every time; improvising a new structure destroys that value.

## Audience and Decision

Answer both before writing. If you cannot, ask.

**Who reads this?** Their context level determines everything.

**What changes because they read it?** Every internal comm should produce a decision, an action, or a corrected mental model. If none of the three, it does not need to be sent.

| Audience | Wants | Does not want |
|---|---|---|
| Executives | Outcome, risk, what you need from them | How it was built, which tickets closed |
| Peer teams | What changed that affects them, when, migration path | Internal reasoning, team process |
| Own team | Specifics, ownership, next steps | Context they already have restated |
| Whole company | Why it matters to them, what to do | Team jargon, org detail |

## Gathering Facts

Available integrations vary by environment — check what is actually connected before assuming.

| Source | Look for |
|---|---|
| Git / issue tracker | What shipped in the window, with dates |
| Slack / Teams | High-engagement threads; decisions made in channel |
| Docs / Drive | Recently-edited specs and decision records |
| Dashboards | The numbers, so claims carry magnitude |
| Calendar | Non-recurring meetings — reviews, incidents, launches |

**Every claim gets a number, a name, or a date.** "Improved performance" is noise. "p95 latency down from 840ms to 210ms" is information. If no number exists, say what specifically happened instead.

## The Compression Pass

Run this on every draft. It is where most of the quality comes from.

1. **Delete the warm-up.** "As you may know…", "I wanted to reach out to share…", "The team has been hard at work…" — the real first sentence is usually the third one.
2. **Move the conclusion to the top.** If the outcome is in the last paragraph, it is in the wrong place.
3. **Cut adverbs of degree.** "Very", "really", "quite", "significantly", "substantially" add length and subtract precision.
4. **Replace hedges with a fact or a stated unknown.** "Should be ready soon" → "Ready Thursday" or "No date yet — blocked on the vendor's reply."
5. **One idea per paragraph**, three sentences maximum.
6. **Convert prose lists to bullets** and prose comparisons to tables.
7. **Read the first sentence alone.** Does it carry the point? If not, rewrite it.

**Length targets:** 3P update ≤ 250 words. Exec update ≤ 200. Announcement ≤ 300. Incident report as long as needed, with a ≤ 100-word summary on top.

## Writing About Problems

The section people get wrong, and the one that decides whether the comm builds or costs trust.

- **State the problem in the first sentence.** Burying it reads as concealment, and readers who find it late trust the rest less.
- **Own it without theatre.** "We shipped a regression that took checkout down for 40 minutes" — not "an issue was experienced by some users."
- **No passive voice for failures.** "Mistakes were made" is the canonical example of what not to write.
- **Blame systems, not people.** Name what allowed the failure — a missing check, an unclear owner, an untested path. Never name an individual as the cause.
- **Include the ask.** A problem with no ask is a complaint. "Blocked on X; need a decision from Y by Thursday."
- **Separate impact from cause.** Readers need impact immediately; cause can follow.

## Tone

- Plain declarative sentences, active voice.
- Write for someone skimming on a phone between meetings.
- No corporate euphemism: "rightsizing", "synergies", "learnings", "circle back", "leverage" as a verb.
- No manufactured enthusiasm. Exclamation marks are for genuine celebration, once.
- Do not thank people for reading. Do not apologize for length — shorten it instead.
- Match the organization's existing register; read a previous update if one exists.

## Self-Review

- [ ] The first sentence carries the point
- [ ] Every claim has a number, a name, or a date
- [ ] No hedges without a stated reason for the uncertainty
- [ ] Problems stated plainly, in active voice, with an ask
- [ ] Under the length target for the type
- [ ] A reader with no context understands what changed and why it matters
- [ ] Every name, date, number, and link verified rather than recalled
- [ ] Nothing confidential is exposed to a wider audience than intended

## Common Mistakes

**Activity reported as achievement.** "Held 6 planning meetings" is not progress. What shipped, what was decided, what changed?

**The point buried at the end.** Readers stop early. Conclusion first, always.

**Uniform detail across items.** A major launch and a dependency bump get the same three lines. Weight by importance.

**Problems omitted because they look bad.** The omission is what looks bad — especially when the problem surfaces later.

**Copy-pasted ticket titles.** Written for the team that owns them. Translate into outcomes for this audience.

**One update reused for every audience.** An exec summary and a team update are different documents, not the same document at two lengths.

## Keywords

3P updates, company newsletter, company comms, weekly update, status report, exec update, leadership update, FAQs, incident report, postmortem, announcement, internal comms

## Related Skills

- **coauthoring-docs** — for substantial documents (specs, proposals, RFCs) rather than updates
- **verifying-before-completion** — before stating in writing that something shipped or passed, verify that it did
