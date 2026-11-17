---
name: designing-frontend-interfaces
description: Use when building or restyling any web interface — landing pages, dashboards, marketing sites, web apps, React/Vue components, HTML/CSS layouts, artifacts, posters — or when asked to make a UI look better, more polished, more distinctive, less generic, or less "AI-generated". Also use when a design brief, art direction, visual identity, type scale, or color system is needed before implementation.
license: Complete terms in LICENSE.txt
---

# Designing Frontend Interfaces

## Overview

Distinctive interfaces come from **committing to one aesthetic direction and executing it with a locked system of values**. Generic interfaces come from picking each value ad hoc at the moment it is needed.

**Core principle:** Decide the system before you write the components. Every number in the finished CSS should trace back to a scale you chose deliberately.

**First decision: what kind of interface is this?**

- **Marketing surfaces** — landing pages, docs, brand sites, portfolios. Here you art-direct: named aesthetic direction, memorable moment, expressive type.
- **App surfaces** — dashboards, admin panels, settings, data tools. Here the user's expectations are set by every professional tool they already use (Jakob's Law). The design *is* the conventions: canvas/surface layering, fixed density scales, a 14px data grid. Art-directing a data tool the way you would a landing page is how "amateur" happens.

The token block, hierarchy rules, and component-state rules apply to both. The aesthetic-direction machinery applies to marketing; `references/app-styles.md` replaces it for apps.

This skill covers **visual craft**. Two companion skills cover the rest of interface quality:

- **REQUIRED SUB-SKILL** for anything with flows, forms, or non-trivial state: use `designing-user-experience`
- **REQUIRED SUB-SKILL** before shipping: use `building-accessible-interfaces`
- To critique a finished UI, use `reviewing-interface-quality`

## The Iron Law

```
NO COMPONENT CODE BEFORE THE DESIGN BRIEF AND TOKEN BLOCK EXIST
```

The brief is 8 lines. The token block is one CSS block. Together they cost about ninety seconds and they are what separates a designed interface from a decorated one.

Wrote components first? The values are already arbitrary. Extract them into a real scale before continuing — do not rationalize the numbers you happened to type.

## Checklist

Create a task for each item and complete them in order:

1. **Name the mode** — marketing surface or app surface; app decides the recipe set
2. **Write the design brief** — 8 lines, in your response, before any file is created
3. **Choose the visual system** — marketing: a named direction from `references/aesthetic-directions.md`. App: the conventions from `references/app-styles.md`, parameterized
4. **Critique the plan** — compare it to the tell lists; revise anything that reads as the generic default
5. **Lock the token block** — type scale, color ramp, space scale, radius, shadow, motion. One CSS block.
6. **Build the layout skeleton** — structure and spacing, no decoration yet
7. **Build components** — every interactive element gets all five states
8. **Add the memorable moment** — marketing: the one thing someone will describe to a friend. App: polish the table, empty states, and the header row instead
9. **Self-review against the rubric** — see Self-Review below; fix what fails
10. **Verify visually** — render it and actually look at it

## Step 1: Name the Mode

State it in one line before anything else: **"This is a marketing surface"** or **"This is an app surface."**

- **Marketing** → the aesthetic-direction machinery below is the design. You are allowed to be expressive.
- **App** → `references/app-styles.md` is the design. The direction is *fixed* (professional conventions); your craft shows up in density, legibility, state coverage, and restraint — not in inventing a look.

Getting this wrong is the single most common cause of "amateur" output: a data dashboard given a magazine treatment, or a landing page given a table-styling treatment.

## Step 2: The Design Brief

Write this out before creating any file. It is 8 lines of plain text in your response — not a document, not a file.

```
Purpose:    What job does this interface do?
Audience:   Who uses it, in what context, on what device?
Tone:       Marketing: one named direction (references/aesthetic-directions.md). App: "app conventions" + parameters
Reference:  A real-world visual analogue — a magazine, an era, a discipline (apps: Grafana, Ant Design Pro)
Palette:    Base / surface / ink / one accent — as hue intentions, not hex yet
Type:       Display face + text face, and why this pairing (apps: platform default + mono for values)
Memorable:  Marketing: the one thing someone will describe to a friend. App: the one thing that makes data legible at a glance
Restraint:  What this design deliberately does NOT do
```

The `Restraint` line matters most. A design with no stated restraint becomes a design with every effect applied at once.

**Worked example (marketing):**

```
Purpose:    Changelog for a developer infrastructure tool
Audience:   Engineers skimming on a wide monitor, 30 seconds per visit
Tone:       Ledger Minimal — financial precision, near-monochrome (see references/aesthetic-directions.md)
Reference:  1990s man pages, Bloomberg terminal screens
Palette:    White, three tints of one gray family, one green and one red for signed values only
Type:       IBM Plex Sans + IBM Plex Mono — one family, tabular figures everywhere
Memorable:  Version numbers set enormous in the left margin, hanging outside the text column
Restraint:  No cards. No shadows. No rounded corners. Rules and space only.
```

Note the direction names a *discipline*, not an adjective. Also note the palette is **not** cream+serif+terracotta — that combination is now an AI cliché in its own right (see Anti-Slop).

**App-mode brief — same 8 lines, different content:**

```
Purpose:    Operations dashboard for a managed-cloud fleet
Audience:   SREs monitoring 200+ servers, dense data, mostly desktop
Tone:       App conventions — no art direction; craft in density, legibility, state coverage
Reference:  Grafana, Ant Design Pro, shadcn admin
Palette:    Tinted gray canvas, white surfaces, one blue accent, fixed semantic set
Type:       Inter or the platform default for UI; mono for values; 14px data grid
Memorable:  A table you can read across without losing your row
Restraint:  No shadows except overlays. No decorative icons. No animation beyond state changes.
```

For apps, `Tone` is the conventions and the brief's job is *parameters* (accent hue, density, light/dark). `references/app-styles.md` supplies the defaults.

## Step 3: Critique the Plan

Before any code, hold the plan up against the two tell lists (Step 6) and answer, honestly:

1. If I described this design to a stranger, would they say it sounds like the thing *every* generated site sounds like?
2. Is the accent color, the typeface, or the layout the one choice I'd pick for *any* similar brief — i.e., the statistical center?
3. For an app: did I invent a "look" where I should have been executing conventions? For marketing: did I skip the memorable moment to be safe?

Rewrite whichever part is the default. The whole point of planning is to catch the generic choice *now*, when it is one line of text, instead of after it has become forty components.

**Why this works:** a model with no plan samples the center of the distribution and calls it done. A model that has *named* its direction and then attacked its own plan for being generic is forced to make at least one off-center, defensible choice. That single act is what separates "designed" from "decorated."

## Step 4: Lock the Token Block

Every value the interface uses comes from here. If a number is not in this block, it does not belong in a component.

```css
:root {
  /* TYPE — one ratio, applied consistently. 1.200 minor third (dense UI),
     1.250 major third (general), 1.333 perfect fourth (marketing),
     1.500 perfect fifth (editorial/poster). Pick ONE. */
  --font-display: "IBM Plex Sans", system-ui, sans-serif;
  --font-text:    "IBM Plex Mono", ui-monospace, monospace;
  --step--1: 0.8rem;    --step-0: 1rem;     --step-1: 1.25rem;
  --step-2:  1.563rem;  --step-3: 1.953rem; --step-4: 2.441rem;
  --step-5:  3.052rem;  --step-6: 3.815rem;

  /* SPACE — one base unit and its multiples. Never a value in between. */
  --space-3xs: 0.25rem; --space-2xs: 0.5rem; --space-xs: 0.75rem;
  --space-s:   1rem;    --space-m:   1.5rem; --space-l:  2rem;
  --space-xl:  3rem;    --space-2xl: 4.5rem; --space-3xl: 7rem;

  /* COLOR — a ramp, not a set of one-offs. One accent, used sparingly.
     For APPS this block is different: tinted canvas + white surface,
     one blue accent, a fixed semantic set. See references/app-styles.md. */
  --base:    #0f1115;   /* page */
  --surface: #171a21;   /* raised */
  --ink:     #e8eaed;   /* primary text */
  --ink-2:   #9aa1ad;   /* secondary text */
  --ink-3:   #6b7280;   /* tertiary / meta */
  --line:    #262b34;   /* borders, rules */
  --accent:  #4f8cff;   /* <10% of visible surface */

  /* FORM */
  --radius: 6px;        /* commit: one value for containers, smaller for controls. Not "some of each". */
  --border: 1px solid var(--line);
  --shadow: none;       /* apps: shadows only on overlays. If used, define 2 — near and far. Never 5. */

  /* MOTION */
  --dur-fast: 120ms; --dur: 220ms; --dur-slow: 420ms;
  --ease:     cubic-bezier(0.2, 0, 0, 1);
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
}
```

**Rules for the block:**

| Token | Rule |
|---|---|
| Type scale | One ratio for the whole page. Deriving sizes by eye produces muddy hierarchy. |
| Space scale | Every margin/padding/gap is a `--space-*` token. No `13px`. No `0.85rem`. |
| Color ramp | Three ink levels is enough. A fourth means the hierarchy is unclear. |
| Accent | Exactly one, unless the direction is explicitly maximalist. Under 10% of surface. |
| Radius | Marketing: one value. App: by role (container / control / badge) — consistent within each role, never "some of each." Mixed radii with no logic is the loudest amateur signal. |
| Shadow | Zero or two. Two shadows = one tight contact shadow + one wide ambient. |
| Motion | Three durations, two easings. That covers every transition an interface needs. |

## Step 5: Hierarchy

**Vary one dimension at a time.** Amateur hierarchy changes size *and* weight *and* color *and* spacing simultaneously; everything shouts and nothing leads.

| Need | Change | Keep fixed |
|---|---|---|
| Section heading vs. body | Size (2+ steps) | Weight, color |
| Emphasis inside a paragraph | Weight | Size, color |
| Metadata / captions | Color (to `--ink-3`) | Size, weight |
| Grouping | Space (a full step) | Everything else |

**Space groups more reliably than lines or boxes.** Before adding a border or a card, try doubling the gap between groups and halving it within them. Most "needs a card" instincts are actually "needs correct spacing."

## Step 6: Anti-Slop

Generic AI interface output has a specific, enumerable signature. **The signature rotates.** A ban list from 2024 (Inter, purple gradients, three cards) is now itself a tell — the model that obeys it drifts to the *next* most common defaults. So treat the lists below as **dated appendices**, and treat the *process* — plan, critique the plan (Step 3), screenshot and count — as the permanent defense.

**The mechanism (why bans alone fail):** nobody detects "one AI-ism." They detect *accumulation* — 50 micro-defaults, each defensible alone, that together read as "generated." A slightly off dot, an arbitrary middle dot, an unnecessary eyebrow label, a card that shouldn't be a card. Each is fixable; the total is not. The audit that matters is a **count**, not a checklist of sins:

> **The accumulation audit:** look at the rendered screenshot and count the "safe choices" — generic labels, unnecessary ornaments, mid-dot separators, `→` appended to links, all-caps eyebrows, numbered non-sequences, hover-lifts on non-clickable cards, redundant status badges. Near zero is the goal. Ten-plus means the page is sampled from the center of the distribution and no real decisions were made.

### Wave 1 (2024-era tells — still identifiable in 2026)

| Never | Instead |
|---|---|
| Inter / Roboto / Open Sans / `system-ui` as the **display** face | A face with an opinion — see `references/typography.md`. (In **app** UI, Inter or the platform default *is* correct — the tell is only for marketing display.) |
| Indigo/purple → blue gradient on hero, headline, or button | One committed palette from a real reference |
| `rounded-xl`/`rounded-2xl` (12-16px) on every surface | Radius by role: 0-4px layout, small controls, pill only for badges |
| `shadow-md` / `rgba(0,0,0,.1)` on every card | Shadow only where something floats; borders for grouping |
| Centered hero → 3 identical feature cards → CTA | Let the content decide the structure |
| `text-gray-500` body on white | Real ink colors; body at full contrast |
| Emoji as feature icons | A real icon set, or nothing |
| Every section the same vertical padding | Vary section spacing to express importance |

### Wave 2 (2025-26 tells — what the Wave-1 bans produced)

| Never | Instead |
|---|---|
| **Cream/beige base (~`#f4f1ea`) + serif display + terracotta/clay accent (~`#d97757`)** — the dominant 2025 AI cliché | A palette from a *named* reference, checked against the direction catalog; rotate light/dark and warm/cool across designs |
| Near-black background + single acid-green or vermilion accent | If dark, a tinted dark (slate, warm charcoal) with a full ramp, not one neon |
| **Uniform "SaaS card kit"** — identical rounded cards, one radius on everything, same soft gray shadow each | Vary the radius by role; separate with hairlines and canvas tints, not cards |
| **Fingernail card** — rounded panel with a colored left-edge stripe/curve | Group by canvas tint and spacing; a side stripe turns every card into an alert |
| **Neobrutalism as a default** — 2px borders + hard offset shadows ≥4px + 0 radius, on everything | If the direction is brutalist, commit fully; it is one of the named directions, not the fallback |
| ALL-CAPS tracked eyebrow labels above every heading | The heading alone, or a single small label where it adds information |
| Middle-dot meta lines (`A · B · C`) and `//` separators | Plain punctuation; one separator style, used only in real lists |
| `→` appended to every link/button label | Arrows on at most the primary action |
| `01 / 02 / 03` numbering on content that is not a sequence | No numbering, or number only real steps |
| One accent word (italic/colored) inside an otherwise uniform headline | Weight or size for emphasis, not color |
| Tinted-near-black (`#0b0b0b`, `#111`) as "designer black" everywhere | A chosen surface ramp with lightness steps |
| Pulsing/animated status dots, "Active"/"Verified" badges that restate what the app enforces | One static status treatment; badges only for information the user cannot see elsewhere |
| Fade-in-on-scroll applied to *every* section, hover-lift on *every* card | One orchestrated motion moment; hover only where there is a real action |
| Glassmorphism / "liquid glass" panels over blurred color blobs | Solid surfaces; `backdrop-filter` only where a real layering exists |
| Bento grids, four-point-star logos, gradient logos, golden/yellow washes (2026 trend defaults) | The named direction's own vocabulary |
| Grain texture + hand-drawn wobble + zine collage on *functional* UI (the 2026 "imperfect by design" backlash) | Roughness in the brand layer only; app surfaces stay precise |
| Walls of header + subheader + bullets in every section; second-person labels ("Needs You") | One line of intent per section; labels as nouns |
| Implementation detail leaking into copy ("Built with X. Runs locally. Your data never leaves your browser.") | Copy that serves the reader's task |

**Why both waves exist:** the field keeps converging on the center of the distribution, and the center *moves*. The durable countermeasures are not the items above — they are: name a direction from a real reference (not adjectives), make at least one off-center deliberate choice, and run the accumulation audit on the actual render.

**The convergence trap:** do not keep reaching for the same "safe distinctive" choices. Space Grotesk + dark slate + lime accent became a cliché; cream + serif + terracotta replaced it. Vary light/dark, serif/sans/mono, dense/airy, warm/cool across your work. Check `references/aesthetic-directions.md` and pick one you did not pick last time.

**In app mode, the anti-slop rule inverts:** the defense is *conformance to conventions*, not distinctiveness. A dashboard that looks like every other well-built dashboard is doing its job — see `references/app-styles.md`. Do not spend art direction there; spend it on the marketing surfaces, and on the states and density that make the app feel finished.

**Rationalization table:**

| Thought | Reality |
|---|---|
| "The user didn't specify a style, so neutral is safest" | Unspecified means you choose. Neutral is a choice, and it is the worst one. |
| "It's just a quick demo" | Demos are what people look at. The brief takes ninety seconds. |
| "This is a standard pattern, everyone does it" | Everyone does it is the tell. Name the variant you picked and why. |
| "I'll add the distinctive touches at the end" | Distinctiveness is structural. Bolted on at the end it reads as decoration. |
| "Tailwind/shadcn defaults are a design system" | They are a *palette* of defaults. Configure them, or you ship the defaults everyone ships. |
| "A card grid is the clearest way to show features" | It is the most *common* way. Try a table, a list with rules, a stepped layout, an editorial spread. |
| "The tell lists are outdated anyway" | The lists rotate; the *audit* doesn't. If you cannot count five safe choices in the render, you are done. |

## Step 7: Component States

Every interactive element gets all five. Missing states are the most common gap in generated UI.

```css
.btn              { /* rest */ }
.btn:hover        { /* pointer only — must not be the sole affordance */ }
.btn:active       { /* pressed — a real transform, not just a color shift */ }
.btn:focus-visible{ outline: 2px solid var(--accent); outline-offset: 2px; }
.btn:disabled     { /* visibly inert, and still readable */ }
.btn[aria-busy]   { /* loading — reserve the space, don't collapse the layout */ }
```

Never remove focus outlines. If the default outline is ugly, restyle it — do not set `outline: none`. See `building-accessible-interfaces`.

## Step 8: Verify Visually

Rendering code and reading it back is not verification. Look at the actual pixels — and look at the *states*, not just the default load, because the states are where generated UI is unfinished.

Capture discipline (all shots): wait for `document.fonts.ready` — a screenshot taken before fonts load reviews the fallback, not the design — and shoot at `device_scale_factor=2`, because 1x text is unreadable.

```bash
# Static HTML — minimum: first-view, full, mobile, dark, plus one state shot
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width':1440,'height':900}, device_scale_factor=2)
    pg.goto('file:///abs/path/index.html')
    pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
    pg.screenshot(path='/tmp/firstview.png')              # viewport only — what a user sees first
    pg.screenshot(path='/tmp/fullpage.png', full_page=True)
    pg.set_viewport_size({'width':390,'height':844})
    pg.screenshot(path='/tmp/mobile.png', full_page=True)
    pg.set_viewport_size({'width':1440,'height':900})
    pg.emulate_media(color_scheme='dark')
    pg.screenshot(path='/tmp/dark.png')
    b.close()"
```

For any UI with data, also capture the **empty state** (cleared data) and, if it loads asynchronously, the **loading state** mid-fetch — these are the states you are most likely to have not designed. The full 8-shot protocol with per-shot checklists lives in `reviewing-interface-quality` Step 1. For dev servers, use the `testing-webapps` skill's `with_server.py` helper.

Then read every PNG and check them against the rubric. What to look for that only shows in the render: text overflowing containers, collapsed layouts at 390px, invisible low-contrast text, elements touching viewport edges, a heading that wraps to one orphaned word, images without dimensions causing layout shift, and in the state shots — an empty state that is genuinely empty of *design*, a skeleton that does not match the loaded layout.

## Self-Review

Score each line honestly. Any `no` means fix it, not explain it.

**All interfaces:**
- [ ] Every spacing value in the CSS is a token from the block
- [ ] All five states exist on every interactive element
- [ ] Focus is visible and never suppressed
- [ ] Verified at 1440px and 390px by looking at screenshots
- [ ] Body text passes 4.5:1; large text passes 3:1
- [ ] **Accumulation audit:** counting safe defaults (generic labels, mid-dots, `→`, eyebrows, hover-lift on non-clicks, redundant badges) on the render gives a low number — near zero for marketing

**Marketing surfaces:**
- [ ] The type scale is one ratio; no size was chosen by eye
- [ ] Exactly one accent color, under 10% of visible surface
- [ ] One radius value (or a deliberate, named exception); mixed radii is the loudest amateur signal
- [ ] A stranger could name the aesthetic direction from a screenshot
- [ ] The `Memorable` line from the brief is actually present in the build
- [ ] The `Restraint` line was actually respected
- [ ] Nothing from either Anti-Slop wave appears

**App surfaces:**
- [ ] Canvas/surface split: tinted page, white (or lighter) content panels
- [ ] Tables follow the convention: 14px, rules-only, 32px checkbox/action columns, footer bar, 96px empty state
- [ ] Density comes from padding, never from shrinking the font
- [ ] The accent is used only for: primary buttons, active nav, focus, and semantic states
- [ ] Shadows only on overlays (menus, dialogs, toasts)
- [ ] No art direction invented — the conventions are the design

## Reference Files

Load these when you reach the relevant decision — not upfront.

| File | Load when |
|---|---|
| `references/aesthetic-directions.md` | Step 2 (marketing) — choosing and parameterizing a direction |
| `references/app-styles.md` | Step 1 names the mode **app** — shells, tables, KPI cards, density, sizes |
| `references/typography.md` | Choosing faces, building the scale, setting text |
| `references/color-and-theme.md` | Building the ramp, dark mode, contrast math |
| `references/layout-and-composition.md` | Grids, breakpoints, breaking the grid, z-index |
| `references/motion.md` | Any animation beyond a hover color change |

## Common Mistakes

**Tokens declared, then ignored.** The `:root` block exists but components use `padding: 14px`. Grep your CSS for raw px values before finishing.

**Distinctive typeface, default everything else.** Swapping Inter for a display face while keeping the card grid, the uniform radius, and the gray body text produces generic output in a costume.

**Maximalism as an excuse for incoherence.** Maximalist directions still need one type scale, one space scale, one palette. More elements, same system.

**The brief describes a design the build does not deliver.** Re-read the brief at the self-review. If `Restraint: no shadows` and the build has shadows, the build is wrong.

**Complexity mismatched to the vision.** A refined-minimal direction implemented with elaborate scroll animations reads as confused. Match implementation effort to the stated tone.

**Marketing art direction applied to an app.** A dashboard given a hero, a named aesthetic movement, and a memorable scroll moment is a costume. App craft is density, legibility, state coverage, and convention — see `references/app-styles.md`. If the mode is app, spend the effort on the table and the empty state, not on the look.

**Banning the old tells and shipping the new ones.** Removing Inter, purple gradients, and card grids without a positive plan lands the model in the *next* statistical center — for 2025-26 that is cream/beige + serif + terracotta, or dark slate + a single neon accent. The fix is never a longer ban list; it is a named direction from a real reference plus the accumulation audit on the render. The tell lists rotate; the plan-and-count process does not.

**The plan was never critiqued.** The brief and token block exist, so the model jumps to code and the generic choice hardens into forty components. Step 3 exists to kill the center-of-distribution plan while it is still one line of text. If you cannot say *one specific thing* you changed when you critiqued the plan, the critique did not happen.
