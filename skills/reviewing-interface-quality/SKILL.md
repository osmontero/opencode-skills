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

**Minimum evidence before writing a single finding:** a screenshot at 1440px, a screenshot at 390px, and the computed values for anything you are about to call inconsistent.

## Checklist

1. **Gather evidence** — render at two widths, capture DOM and computed styles
2. **Pass 1: First impression** — 5 seconds, before analysis
3. **Pass 2: System consistency** — the highest-yield pass
4. **Pass 3: Typography**
5. **Pass 4: Layout and responsive**
6. **Pass 5: States and behavior**
7. **Pass 6: Accessibility**
8. **Pass 7: Motion and performance**
9. **Report** — severity-graded, each with location, cause, fix

## Step 1: Gather Evidence

```python
from playwright.sync_api import sync_playwright
URL = "http://localhost:5173"   # or file:///abs/path/index.html

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
    pg.goto(URL); pg.wait_for_load_state("networkidle")
    pg.screenshot(path="/tmp/rev-desktop.png", full_page=True)

    # Horizontal overflow — always a bug
    print("OVERFLOW:", pg.evaluate("""() => [...document.querySelectorAll('*')]
        .filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
        .slice(0, 10).map(e => e.tagName + '.' + e.className)"""))

    # Every distinct value actually used — the consistency audit
    for prop in ["font-size", "font-family", "border-radius", "box-shadow", "padding", "color"]:
        vals = pg.evaluate("""(p) => [...new Set([...document.querySelectorAll('*')]
            .map(e => getComputedStyle(e)[p]))].filter(v => v && v!=='none' && v!=='0px')""", prop)
        print(f"{prop}: {len(vals)} distinct →", vals[:14])

    pg.set_viewport_size({"width": 390, "height": 844})
    pg.screenshot(path="/tmp/rev-mobile.png", full_page=True)
    print("CONSOLE ERRORS:", errors)
    b.close()
```

Then **read both screenshots**. The distinct-value counts tell you where the system broke; the screenshots tell you what it looks like. You need both.

For a server-backed app, wrap this with `testing-webapps`' `scripts/with_server.py`.

If the UI genuinely cannot be rendered (no runtime, a fragment, a component in isolation), say so explicitly in the report and mark every visual finding `PLAUSIBLE` rather than `CONFIRMED`.

## Step 2: First Impression

Look at the desktop screenshot for five seconds and answer before analyzing anything:

1. **What is this?** If unclear in 5s, the hierarchy has failed.
2. **What should I do?** The primary action should be unmistakable.
3. **Where does my eye land first?** Is it the most important thing?
4. **Could I name the aesthetic direction?** "Clean" and "modern" mean there is no direction.
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

## Step 4: Typography

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

## Step 5: Layout and Responsive

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

## Step 6: States and Behavior

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

## Step 7: Accessibility

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

## Step 8: Motion and Performance

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
Rendered at 1440×900 and 390×844. 34 distinct font-sizes, 6 border-radii,
9 box-shadows. 2 console errors. 1 horizontal overflow.

## Critical — breaks the interface for some users
**Focus indicator removed globally**
`src/styles/base.css:12` — `*:focus { outline: none }` with no replacement.
Keyboard users cannot tell where they are; WCAG 2.4.7 failure.
Fix: delete it, add `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }`.

## Important — visibly degrades quality
**Spacing scale not enforced**
17 distinct padding values including `14px`, `18px`, `22px` (`Card.tsx:8`,
`Panel.tsx:22`, `Modal.tsx:41`). Tokens exist in `:root` but are unused, so
nothing aligns to a common rhythm.
Fix: replace every raw px with the nearest `--space-*` token.

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

**Desktop only.** Most defects appear at 390px. Both widths, always.

**Redesigning instead of reviewing.** "Rebuild this as a dashboard" is not a finding. Fix what exists unless the direction itself is the problem — and if it is, say so once, as a single top-level finding.

**Severity inflation.** Calling everything Critical means nothing is. Reserve it for genuinely broken.

**Listing violations without fixes.** "Contrast fails" is half a finding. "`--ink-3` `#8b857c` on `--base` `#f4f1ea` is 2.9:1; darken to `#6b6459` for 4.5:1" is a whole one.

**Skipping the first impression.** Once you are three passes deep you cannot recover the naive read, and it is the only read most users get.
