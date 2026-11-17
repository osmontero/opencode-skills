# App UI Numbers (research-verified)

Concrete values from Nielsen Norman Group research (fetched and verified 2026-11) and official platform specs (Material 3, Apple HIG). When a number here and an instinct disagree, the research wins — these are the values behind "why professional software feels right."

## Latency limits (NN/g, the three limits, reaffirmed 2024)

| Limit | Meaning |
|---|---|
| 100ms | Direct-manipulation response: keystrokes, toggles, menus must feel instant |
| 1s | Control: the user still feels in charge; **sorting a table must complete here** or the app feels sluggish |
| 10s | Attention: beyond this the user stops watching; a real progress indicator with an explicit estimate is required |

Variable response times (queries, dashboards) make feedback during the wait *more* important, not less.

## Loading treatment by wait (NN/g skeleton research, reviewed 2026-09)

| Wait / scope | Treatment |
|---|---|
| Under 1s | Nothing. A flashing skeleton or spinner is worse than none. |
| 1-10s, whole screen | Skeleton matching the real layout. **Frame-only skeletons (header + blank body) are the worst option** — on long waits they read as a broken page. |
| 1-10s, one module | Spinner / wait animation in that module only. |
| Over 10s | Determinate progress bar with a time estimate. |
| Any non-load work (upload, export, transform) | Progress bar, never a skeleton. |

## Confirmation dialogs (NN/g, reviewed 2026-08) — the eight rules

1. Confirm only actions with serious consequences — irreversible, costly, or affecting other people.
2. Never for routine actions. A dialog that always gets "yes" has lost all protective power.
3. Be specific: restate the exact effect ("Delete the 47 records in *Q3 Archive*"), never "these items".
4. Label buttons with consequences, not Yes/No ("Delete 47 records" / "Keep them").
5. Progressive disclosure for details; the first screen is the decision.
6. No default "Yes" — best, no default at all.
7. Type-the-name only for the rarest, catastrophic actions; overusing it trains users to type past it.
8. Offer "Don't ask again" for semi-routine ones.

**Calibrate with consequence × frequency:** a frequent reversible action gets undo; an occasional costly one (a payment ~2× the user's normal range) gets a specific confirmation.

## Undo (NN/g user-control research)

- Undo beats confirmation as the primary defense — some errors survive even the best dialogs.
- A transient contextual undo (toast, 8-10s) needs a persistent Undo entry alongside it for desktop power users; the contextual one disappears.
- Rapid successive actions (data tools) need multi-level undo.

## Dashboards and charts (NN/g preattentive research)

- A dashboard is a single-page, at-a-glance **monitoring** view — not an exploration tool. If the user has to dig, it is a table with decoration.
- Encode quantity with **length and position** (bars, lines, scatter) — the only two attributes humans judge accurately. Area and angle are detected fast but judged wrong: **no pie/donut/treemap/radial gauge for quantitative comparison**. 3D distorts length — never.
- Color is categorical, never ordinal — it has no perceptual order. Pair color with shape or a direct label (~8% of men have color-vision deficiency).
- Salience by **removal**: a bare large number beats a number with a decorative icon; every superfluous element on a tile slows visual search.

## Empty states (NN/g complex-apps research)

1. Communicate status — a blank panel makes users wonder whether it is loading, an error, or a filter.
2. **Never a misleading interim state.** "No records" that gets replaced by data when the slow query resolves destroys trust: users who learned it will refresh on the *real* empty and miss results.
3. Use the space to teach what belongs there, and give the direct path — a button or link, not just an instruction.

## Data tables (NN/g four-task research)

A table exists to do exactly four things — **find, compare, view/edit, act** — and must support each explicitly.

- **Find:** first column is a human-readable identifier, never a generated one; default column order = importance, related columns adjacent; filters discoverable with a visible "active" indication.
- **Compare:** freeze the header row (and first column) once the table exceeds the screen; hover row highlight; hidden/reordered columns must be cheap to restore and visibly indicated ("15 columns hidden").
- **View/edit:** in-place editing only in narrow tables; deep edit in a **non-modal side panel** — a modal covers the reference rows.
- **Act:** 1-2 actions inline; more in a per-row menu; never hover-revealed only. Bulk: per-row checkbox + action bar + select-all with indeterminate state.
- **Wide tables:** a column chooser is the professional default, better than horizontal scroll.
- **Pagination:** one default page size (10 or 20) plus "View all" for power users; filters + a result count are what make any listing pattern work.
- **Mobile:** two columns is the portrait floor; required horizontal scroll must be *apparent* (cut-off content), not hinted with dots.

## Platform sizing (Material 3 / Apple HIG)

| Value | M3 | Apple |
|---|---|---|
| Touch target | 48dp | 44pt (28pt minimum, dense controls only) |
| List row height | 56dp one line / 72dp two lines | — |
| Button height | 40dp | — |
| App bar | 64dp (small) | 44pt |
| Shape scale | 4 / 8 / 12 / 16 / 28dp | continuous corners |
| Spacing grid | 8dp, 4dp half-step | system spacing |
| Elevation | tonal steps first; shadow 0/1/3/6/8/12dp | — |
