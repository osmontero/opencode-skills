# Layout and Composition

## Space Is the Design

Before adding a border, a card, or a background tint to group things — try changing the space. Most "this needs a container" instincts are actually "this spacing is wrong."

**The proximity rule:** space *within* a group must be visibly smaller than space *around* it. If a label sits 12px from its input and 16px from the next field, the form reads as an undifferentiated list. Make it 6px and 32px.

```css
.field       { display: grid; gap: var(--space-3xs); }  /* within: 4px  */
.field-group { display: grid; gap: var(--space-l); }    /* between: 32px */
```

A 4:1 ratio between outer and inner spacing is a reliable starting point.

## The Space Scale

One base unit, geometric-ish progression. Every gap, margin, and padding is a token.

```css
--space-3xs: 0.25rem;  /*  4px */  --space-2xs: 0.5rem;  /*  8px */
--space-xs:  0.75rem;  /* 12px */  --space-s:   1rem;    /* 16px */
--space-m:   1.5rem;   /* 24px */  --space-l:   2rem;    /* 32px */
--space-xl:  3rem;     /* 48px */  --space-2xl: 4.5rem;  /* 72px */
--space-3xl: 7rem;     /* 112px */
```

Fluid section spacing, so vertical rhythm scales with viewport:

```css
--space-section: clamp(3rem, 2rem + 5vw, 7rem);
```

**No value in between.** `padding: 14px` means the scale was abandoned. If 12 is too tight and 16 is too loose, the problem is usually the font-size or line-height, not the padding.

## Grids

```css
.grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--space-m);
}
```

`minmax(0, 1fr)` rather than `1fr` — without it, grid items with long unbreakable content (URLs, code) blow out the track.

**Intrinsic grids** handle responsive layout without a single media query:

```css
/* Cards wrap automatically at their own minimum width */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
  gap: var(--space-m);
}
```

The `min(18rem, 100%)` guard prevents overflow on viewports narrower than the stated minimum.

**Content-width layout** — full-bleed elements without wrapper divs:

```css
.layout {
  display: grid;
  grid-template-columns:
    [full-start] minmax(var(--space-s), 1fr)
    [content-start] min(68ch, 100%) [content-end]
    minmax(var(--space-s), 1fr) [full-end];
}
.layout > *          { grid-column: content; }
.layout > .full-bleed{ grid-column: full; }
```

## Breaking the Grid

An interface where every element sits inside the same centered column is legible and forgettable. Break it deliberately — once or twice per page, not everywhere.

| Technique | Implementation |
|---|---|
| **Hanging marginalia** | Metadata in the gutter: `margin-left: calc(-1 * var(--space-2xl))` |
| **Asymmetric split** | `grid-template-columns: 5fr 7fr` — never 50/50, never for the whole page |
| **Overlap** | Negative margin plus `z-index`; a heading crossing an image edge |
| **Full bleed** | One element escaping to `100vw` while the rest stays in measure |
| **Off-axis** | `transform: rotate(-1.5deg)` on a single element |
| **Vertical text** | `writing-mode: vertical-rl` for a section label in the margin |

Break it once with confidence rather than five times timidly.

## Responsive

**Mobile-first, min-width queries.** Base styles are the small-screen styles; each breakpoint adds.

```css
.stack { display: grid; gap: var(--space-m); }
@media (min-width: 48em) { .stack { grid-template-columns: 1fr 2fr } }
```

Breakpoints in `em` respond to user font-size settings; `px` breakpoints ignore them.

**Container queries** for components that appear in several contexts. A card in a sidebar and the same card in a main column should respond to *their own* width, not the viewport's:

```css
.card-area { container-type: inline-size; }
@container (min-width: 30rem) {
  .card { grid-template-columns: 8rem 1fr; }
}
```

**Test widths that matter:** 390 (iPhone), 768 (tablet portrait), 1024 (tablet landscape / small laptop), 1440 (desktop), 1920. The 390 and 1440 checks are mandatory; the rest as the design warrants.

**Touch targets:** minimum 44×44 CSS px for anything tappable, with at least 8px between adjacent targets. This is WCAG 2.2 SC 2.5.8.

## Vertical Rhythm

Section spacing should express importance, not be uniform.

```css
.section        { padding-block: var(--space-section); }
.section--hero  { padding-block: calc(var(--space-section) * 1.6); }
.section--dense { padding-block: calc(var(--space-section) * 0.5); }
```

Uniform section padding down the whole page is a slop signal — it says no editorial decision was made about what matters.

**Flow spacing** — one rule instead of per-element margins:

```css
.flow > * + * { margin-block-start: var(--flow-space, var(--space-m)); }
.flow > h2    { --flow-space: var(--space-xl); }   /* more room above headings */
.flow > h2 + * { --flow-space: var(--space-2xs); } /* less below them */
```

## Z-Index

A named scale, defined once. Ad-hoc `z-index: 9999` is how stacking bugs are born.

```css
--z-base: 0; --z-raised: 10; --z-sticky: 100;
--z-overlay: 1000; --z-modal: 1100; --z-toast: 1200;
```

Remember that `transform`, `filter`, `opacity < 1`, `backdrop-filter`, and `will-change` all create new stacking contexts. A child cannot escape its parent's context regardless of its `z-index`.

## Overflow Discipline

Horizontal page scroll is always a bug. Wide content scrolls inside its own container.

```css
.table-wrap { overflow-x: auto; overscroll-behavior-x: contain; }
pre          { overflow-x: auto; }
img, video, svg { max-width: 100%; height: auto; }
```

Find the culprit:

```js
[...document.querySelectorAll('*')].filter(el =>
  el.getBoundingClientRect().right > document.documentElement.clientWidth)
```

**Reserve space for media** to prevent layout shift:

```html
<img src="hero.jpg" width="1600" height="900" alt="" style="aspect-ratio:16/9">
```

## Layout Recipes

**Sidebar that collapses without a media query:**

```css
.with-sidebar { display: flex; flex-wrap: wrap; gap: var(--space-l); }
.with-sidebar > .sidebar { flex: 1 1 16rem; }
.with-sidebar > .main    { flex: 999 1 60%; min-width: 50%; }
```

**Sticky footer:**

```css
body { min-height: 100svh; display: grid; grid-template-rows: auto 1fr auto; }
```

Use `svh`/`dvh` rather than `vh` — mobile browser chrome makes `100vh` overflow.

**Center anything:**

```css
.center { display: grid; place-items: center; }
```

**Equal-height cards with bottom-pinned actions:**

```css
.card { display: grid; grid-template-rows: auto 1fr auto; }
```

## Common Mistakes

**Everything in one centered column.** Legible, forgettable. Vary the measure by content type — a data table does not want 68ch.

**Uniform section padding.** Every section equally important means none of them are.

**Cards used as the default grouping tool.** A card implies "this is a discrete, actionable object." Applied to everything it means nothing. Rules, space, and tint are lighter-weight alternatives.

**Fixed heights on text containers.** Text length varies with content and translation. Constrain width, let height be intrinsic.

**`gap` forgotten in favor of child margins.** Margins on children collapse unpredictably and break when items reorder. Use `gap` on the container.

**`100vh` on mobile.** Address bar behavior makes it overflow. Use `100dvh` or `100svh`.
