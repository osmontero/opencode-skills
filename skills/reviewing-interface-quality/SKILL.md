---
name: reviewing-interface-quality
description: Use when asked to review, critique, audit, or improve an existing user interface — "review this UI", "why does this look generic", "make this more polished", "design feedback", "does this look AI-generated", "audit this page". Also use as the final gate before shipping any frontend work, and when a UI renders correctly but feels unfinished, cheap, or inconsistent without an obvious cause.
---

# Reviewing Interface Quality

## Overview

"Make it look better" is not actionable. Interface quality problems have specific causes — an unenforced spacing scale, hierarchy varying on four dimensions at once, a state that was never designed — and a review is only useful if it names the cause and the fix.

**Core principle:** Every finding names a location, a cause, and a concrete replacement value. "The spacing feels off" is not a finding. "`.card` uses `padding: 14px` while everything else uses the 8px scale — change to `var(--space-s)`" is.

**Companion skills:** `designing-frontend-interfaces` (visual), `designing-user-experience` (behavior), `building-accessible-interfaces` (access). This skill audits against all three.

## The Iron Law

```
NO FINDING WITHOUT EVIDENCE YOU ACTUALLY GATHERED
```

Reviewing an interface means looking at it. Reading the source and inferring how it renders is not a review — it misses exactly the class of defect a review exists to catch: overflow, collapsed layouts, invisible text, layout shift, broken states.

**Minimum evidence before writing a single finding:** the first-view and full-page shots at 1440px, the full-page shot at 390px, a focus shot, and the computed values for anything you are about to call inconsistent. Dark, empty, loading, and error shots are required for any UI that claims to support them — a state you did not capture is a state you did not review.

## Checklist

1. **Gather evidence** — the full shot list (first-view, full, mobile, dark, empty, loading, error, focus), plus DOM and computed styles
2. **First impression** — 5 seconds, before analysis
3. **System consistency** — the highest-yield pass
4. **AI-generated tells** — the accumulation count
5. **App-mode pass** — only if the mode is app
6. **Typography**
7. **Layout and responsive**
8. **States and behavior**
9. **Accessibility**
10. **Motion and performance**
11. **Report** — severity-graded, each with location, cause, fix

## Step 1: Gather Evidence

### The shot list

Capture these — the two happy-path shots are the minimum, the rest are what make the review real:

| # | Shot | Size / state | Purpose |
|---|---|---|---|
| 1 | **First-view** | 1440×900, viewport only, not full-page | The 5-second pass (Step 2) — what a user actually sees before scrolling |
| 2 | **Full page** | 1440, `full_page=True` | Structure, rhythm, section spacing, orphaned words |
| 3 | **Mobile** | 390×844, full page | Collapse, overlap, legibility without pinch |
| 4 | **Dark mode** | 1440, `prefers-color-scheme: dark` emulated | Contrast in both schemes, elevation by lightness |
| 5 | **Empty** | 1440, first-use state (cleared data) | Was the empty state designed? |
| 6 | **Loading** | 1440, during a real delayed fetch | Skeleton shape, no blank screen, no layout shift |
| 7 | **Error** | 1440, a failed request (route aborted / network offline) | Recovery affordance, copy quality |
| 8 | **Focus** | 1440, keyboard: `Tab` 3-5 times | Ring visible at every stop, order matches visual |

Minimum viable review: shots 1, 2, 3, 8. A review that never captured 4-7 is asserting the states exist without having seen them — mark any state finding from those `UNVERIFIED`, not `CONFIRMED`.

### Capture hygiene

```python
from playwright.sync_api import sync_playwright

URL = "http://localhost:5173"   # or file:///abs/path/index.html
S = {}  # shots go here, named per the list

with sync_playwright() as p:
    b = p.chromium.launch()
    # device_scale_factor=2 — 1x text is unreadable in review; 2x is the floor
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))

    def shot(name, full_page=False, **kwargs):
        # Fonts first — a screenshot before fonts load reviews the fallback, not the design
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(250)   # let any reveal animations settle
        pg.screenshot(path=f"/tmp/rev-{name}.png", full_page=full_page, **kwargs)
        S[name] = True

    pg.goto(URL); pg.wait_for_load_state("networkidle")
    shot("firstview")                      # 1 — viewport only
    shot("fullpage", full_page=True)       # 2

    # 3 — mobile
    pg.set_viewport_size({"width": 390, "height": 844})
    shot("mobile", full_page=True)
    pg.set_viewport_size({"width": 1440, "height": 900})

    # 4 — dark (emulate; for a manual-toggle app, click the toggle instead)
    pg.emulate_media(color_scheme="dark"); shot("dark")
    pg.emulate_media(color_scheme=None)

    # 5 — empty: clear the store / use a clean profile so the first-use state renders
    # 6 — loading: start a slow fetch (or throttle 2500ms in devtools) and shoot mid-load
    # 7 — error: abort the route, or context.set_offline(True) before the fetch
    # 8 — focus: pg.keyboard.press("Tab") ×4, then shot("focus")

    # Horizontal overflow — always a bug
    print("OVERFLOW:", pg.evaluate("""() => [...document.querySelectorAll('*')]
        .filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
        .slice(0, 10).map(e => e.tagName + '.' + e.className)"""))

    # Every distinct value actually used — the consistency audit
    for prop in ["font-size", "font-family", "border-radius", "box-shadow", "padding", "color"]:
        vals = pg.evaluate("""(p) => [...new Set([...document.querySelectorAll('*')]
            .map(e => getComputedStyle(e)[p]))].filter(v => v && v!=='none' && v!=='0px')""", prop)
        print(f"{prop}: {len(vals)} distinct →", vals[:14])

    print("CONSOLE ERRORS:", errors)
    b.close()
```

**States must be real, not faked.** The empty, loading, and error shots must come from the app actually being in that state (cleared data, a throttled or aborted request, `set_offline`). Rendering the error state by injecting CSS or hardcoding a class is not evidence — it proves the markup exists, not that the state is reachable or correct.

### What to look for, per shot

| Shot | Checks |
|---|---|
| **First-view** | Can you say what the page is and the primary action in 5 seconds? Is the first thing your eye lands on the most important element? Any element touching the viewport edge? |
| **Full page** | Section spacing vary with importance (uniform padding = a finding)? Orphaned single words on heading last lines? Left/right edges of a consistent alignment? Any element wider than its container? |
| **Mobile** | Horizontal scroll (cross-check the OVERFLOW printout)? Text under ~12px? Two-column content that did not collapse? Fixed elements covering content? Primary actions in the bottom half (thumb reach)? |
| **Dark** | Ink-2/ink-3 still readable (re-check contrast, do not assume)? Any pure `#000` page or `#fff` text? Depth from lightness steps, not shadows? Accent brightened enough? |
| **Empty** | A designed message + the action that fills it — or nothing? (Nothing is an Important finding.) First-use vs no-results vs cleared, distinct? |
| **Loading** | Skeleton matches the loaded layout's shape? No blank/white flash? No layout shift between skeleton and content (compare with the first-view shot)? Spinner for under 100ms? |
| **Error** | A visible error with a recovery control? No raw status code / stack trace in user copy? Is it inline at the source or a banner where one belongs? |
| **Focus** | Focus ring visible on every stop, including on dark and colored surfaces? Tab order matches visual order? Any trap or skipped element? |

Then **read every screenshot you captured**. The distinct-value counts tell you where the system broke; the screenshots tell you what it looks like. You need both.

For a server-backed app, wrap this with `testing-webapps/scripts/with_server.py`.

If the UI genuinely cannot be rendered (no runtime, a fragment, a component in isolation), say so explicitly in the report and mark every visual finding `PLAUSIBLE` rather than `CONFIRMED`.

## Step 2: First Impression

Look at the **first-view** shot (viewport-only, before scrolling) for five seconds and answer before analyzing anything:

1. **What is this?** If unclear in 5s, the hierarchy has failed.
2. **What should I do?** The primary action should be unmistakable.
3. **Where does my eye land first?** Is it the most important thing?
4. **What mode is it in, and is that mode executed?** For marketing surfaces: could I name the aesthetic direction? "Clean" and "modern" mean there is no direction. For app surfaces: does it execute the professional conventions (canvas/surface split, table discipline, density)? A dashboard that tries to be a landing page, or one that ignores the conventions, both fail this test.
5. **Would I guess this was generated?** If yes, name the specific tells.

Write these answers down before proceeding. Once you start auditing details you cannot recover the naive read, and it is the read every real user has.

## Step 3: System Consistency

Highest yield. Most "looks unpolished" comes from here, and every finding is objective.

| Check | Threshold | Common cause |
|---|---|---|
| Distinct `font-size` values | > 8 | Sizes chosen ad hoc, no ratio scale |
| Distinct `font-family` values | > 3 | Third face crept in, or a fallback resolving differently |
| Distinct `border-radius` values | > 2 | Mixed radii — the loudest amateur signal |
| Distinct `box-shadow` values | > 3 | A new shadow invented per component |
| Padding values off the space scale | any | Raw px instead of tokens |
| Distinct grays in `color` | > 5 | No ink ramp; each component picked its own |
| Accent color surface area | > 10% | Accent used as decoration rather than emphasis |

```bash
# Fast static pass over source
grep -rEo '(padding|margin|gap|font-size):[^;]+' src/ | grep -E '[0-9]+px' | sort | uniq -c | sort -rn
grep -rEo 'border-radius:[^;]+' src/ | sort | uniq -c
```

**Also check:** are design tokens declared but not used? A `:root` block with a beautiful scale and components full of raw px is a very common and very fixable finding.

## Step 4: AI-Generated Tells

This is the pass that answers "would I guess this was generated." The tells **rotate with the era** — a 2024 checklist (Inter, purple gradients) now also flags 2026 output. Work from the full lists in `designing-frontend-interfaces` Step 6 (Anti-Slop, both waves).

**Do the accumulation count, not a sin checklist.** Look at the render and tally the "safe choices": generic eyebrow labels, middle-dot meta lines, `→` appended to links, `01/02/03` numbering on non-sequences, hover-lift on non-clickable cards, redundant status badges, a colored left-edge stripe on a card, uniform section padding. Each is defensible alone; ten-plus means the page was sampled from the center of the distribution. Report the count as evidence.

**Era-aware:** if the output is cream/beige + serif + terracotta, or dark-slate + a single neon accent, or a uniform rounded "SaaS card kit" with the same soft gray shadow everywhere, name it as the current generative default. Conversely, do not flag a *conformant* admin UI as generic — in app mode, looking like a well-built dashboard is the point, not a defect.

## Step 5: App-Mode Pass (run only when Step 2 names the mode as app)

Audit against `designing-frontend-interfaces/references/app-styles.md`:

- [ ] Canvas/surface split: tinted page background, white (or one-step-lighter) content panels — not everything on a flat single background
- [ ] Tables: 14px at every density (padding varies, font does not); rules-only; 32px checkbox and action columns; footer bar with row-count and page controls; 96px empty state
- [ ] Numeric columns right-aligned, `tabular-nums`
- [ ] Status values are pills, never color alone
- [ ] KPI cards: the number leads; no decorative icon stealing focus
- [ ] Accent confined to primary buttons, active nav, focus, and semantic states
- [ ] Shadows only on overlays
- [ ] No marketing art direction (hero, scroll moment, named aesthetic movement) imposed on a data tool

## Step 6: Typography

- [ ] Sizes follow one ratio — not eyeballed
- [ ] Display face is not Inter / Roboto / system-ui
- [ ] Three weights maximum
- [ ] Body measure 60-75ch — not full page width, not 30ch
- [ ] Line-height varies inversely with size (body ~1.6, display ~1.0)
- [ ] Large display type has negative tracking
- [ ] Body text has no added letter-spacing
- [ ] No centered paragraphs; no all-caps sentences
- [ ] Numeric columns use `tabular-nums`
- [ ] Headings use `text-wrap: balance`
- [ ] No orphaned single words on heading final lines

## Step 7: Layout and Responsive

- [ ] No horizontal page scroll at any width (check the overflow query output)
- [ ] Nothing touches the viewport edge without intended padding
- [ ] Related items are visibly closer than unrelated ones (4:1 inner/outer ratio)
- [ ] Section spacing varies with importance — not uniform down the page
- [ ] Alignment is consistent — no near-misses (12px vs. 16px left edges)
- [ ] At 390px: nothing overlaps, no text clipped, no fixed element covering content
- [ ] Tables and code blocks scroll inside their own container, not the page
- [ ] Images have `width`/`height` or `aspect-ratio` — no layout shift
- [ ] `100dvh`/`100svh` rather than `100vh`
- [ ] The grid is broken at least once, deliberately — or the design is a uniform centered column

## Step 8: States and Behavior

Check each against `designing-user-experience`. These are usually **missing**, not wrong — so audit the code, not just the render.

- [ ] Empty (first use) distinct from empty (no results) distinct from empty (cleared)
- [ ] Loading does not blank already-visible content
- [ ] Skeletons match the real content's shape and are delayed ~200ms
- [ ] Errors state what to do and provide the control to do it
- [ ] No raw status codes or stack traces surfaced to the user
- [ ] Forms preserve input on error
- [ ] Validation on blur, not on keystroke
- [ ] Inputs have correct `type`, `inputmode`, `autocomplete`
- [ ] Button labels name their action, readable out of context
- [ ] Destructive actions have undo or a specific confirmation
- [ ] All five interactive states exist: rest, hover, active, focus-visible, disabled
- [ ] Filter/tab/modal state is in the URL
- [ ] Touch targets ≥ 44px, nothing hover-only

## Step 9: Accessibility

Run the automated scan, then the keyboard walk. Full detail in `building-accessible-interfaces`.

```bash
npx @axe-core/cli http://localhost:5173 --exit
```

- [ ] Zero axe violations, or each remaining one is justified in writing
- [ ] Body text 4.5:1, large text 3:1 — **in both light and dark**
- [ ] Focus visible everywhere; `outline: none` never appears without a replacement
- [ ] Tab order matches visual order
- [ ] Modals move focus in and return it on close
- [ ] Every image has `alt` (empty for decorative)
- [ ] Every icon-only button has an accessible name
- [ ] One `<h1>`; no skipped heading levels
- [ ] `<main>`, `<nav>`, `<header>` landmarks present
- [ ] No state communicated by color alone
- [ ] Live regions exist for async updates and pre-date their content

## Step 10: Motion and Performance

- [ ] `prefers-reduced-motion` block exists
- [ ] Only `transform`/`opacity`/`filter` animated — no `width`/`height`/`top`/`left`
- [ ] No `transition: all`
- [ ] Durations 80-450ms for user-triggered motion
- [ ] Entrances ease out; exits ease in and are faster
- [ ] No spinner for sub-100ms operations
- [ ] Zero console errors
- [ ] Fonts have `font-display: swap` and a metric-matched fallback
- [ ] No layout shift on load (watch the screenshot sequence, or check CLS)

## Report Format

Order findings by severity. Every finding carries a location, a cause, and a fix.

```markdown
## First Impression
[The 5 answers from Step 2 — the naive read, verbatim]

## Evidence
Shots captured: first-view, full-page, mobile, dark, empty, loading, error,
focus (list the ones actually taken; name any the review skipped and why).
2x-scale screenshots, fonts settled. 34 distinct font-sizes, 6 border-radii,
9 box-shadows. 2 console errors. 1 horizontal overflow.
Accumulation audit: N safe-choice tells counted on the render (target: low).

## Critical — breaks the interface for some users
**Focus indicator removed globally**
`src/styles/base.css:12` — `*:focus { outline: none }` with no replacement.
Keyboard users cannot tell where they are; WCAG 2.4.7 failure.
Fix: delete it, add `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }`.
[Seen in: focus shot — CONFIRMED. Findings that come from a captured shot carry
the shot name; findings inferred from code without a shot are marked PLAUSIBLE.]

## Important — visibly degrades quality
**Spacing scale not enforced**
17 distinct padding values including `14px`, `18px`, `22px` (`Card.tsx:8`,
`Panel.tsx:22`, `Modal.tsx:41`). Tokens exist in `:root` but are unused, so
nothing aligns to a common rhythm.
Fix: replace every raw px with the nearest `--space-*` token.

**Empty state is an absent state**
[If the empty shot shows nothing — no message, no action. The empty shot is
precisely the evidence for this; do not mark it PLAUSIBLE when you captured it.]
Fix: first-use message + the primary action that fills it.

## Minor — polish
**Headings orphan their last word**
`h2` in `Hero.tsx:14` wraps "started" alone onto line 2 at 1440px.
Fix: add `text-wrap: balance`.

## Strengths
[Specific, not flattery. "The type pairing carries the direction" — not "looks good".]

## Verdict
Ship / Ship with the Critical items fixed / Needs rework — plus one sentence of reasoning.
```

## Severity

| Severity | Definition |
|---|---|
| **Critical** | Unusable for some users, or data loss. Keyboard traps, removed focus, failing contrast on body text, form clearing on error, horizontal overflow on mobile. |
| **Important** | Visibly degrades quality or blocks a real task. Inconsistent system values, missing states, unreadable measure, missing error recovery. |
| **Minor** | Polish. Orphaned words, a slightly-off duration, a shadow that could be tighter. |

Do not pad the report. Five real findings beat twenty that mix a keyboard trap with a 2px alignment nit — the padding buries the trap.

## Common Mistakes

**Reviewing the code instead of the interface.** The defects a review exists to catch are the ones only visible when rendered.

**"Feels off" findings.** If you cannot name the cause, keep looking. Every quality problem has a mechanical cause.

**One width, one state.** Most defects appear at 390px *or* in a state the default load never shows (empty, dark, error, focus). Both widths, and every state the UI claims to support, always. A review of the happy path at one width is not a review.

**Redesigning instead of reviewing.** "Rebuild this as a dashboard" is not a finding. Fix what exists unless the direction itself is the problem — and if it is, say so once, as a single top-level finding.

**Severity inflation.** Calling everything Critical means nothing is. Reserve it for genuinely broken.

**Listing violations without fixes.** "Contrast fails" is half a finding. "`--ink-3` `#8b857c` on `--base` `#f4f1ea` is 2.9:1; darken to `#6b6459` for 4.5:1" is a whole one.

**Skipping the first impression.** Once you are three passes deep you cannot recover the naive read, and it is the only read most users get.
