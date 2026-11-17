# App Styles: Shells, Tables, and Density

Visual conventions for dashboards, admin panels, settings, and data tools. The numbers below converge across Tabler, shadcn/ui, Ant Design, MUI X, Mantine, and Untitled UI, cross-checked against Material 3 and Apple HIG.

In app mode these conventions **are** the design. Jakob's Law: your users' expectations are set by every other professional tool they have used. Inventing a personality here is a defect, not a feature — reserve art direction for marketing surfaces.

## App Shell

| Part | Value | Note |
|---|---|---|
| Sidebar width | 200-256px | 256px (16rem) is the shadcn standard; 200px Ant Design |
| Collapsed rail | 64px (4rem) | Icon-only; submenus become flyouts |
| Top bar height | 64px | M3 small app bar |
| Canvas (page background) | Tinted gray, e.g. `#f5f5f5` | **The canvas/surface split is the pro-vs-amateur divider**: white cards and tables on a 2-4% tinted page |
| Surface (cards, tables, inputs) | White in light mode | Dark mode: one lightness step above the canvas |
| Separation | 1px hairline borders, not shadows | Shadows in apps are for overlays (menus, dialogs, toasts) only |
| Content width | Unconstrained for data views; ~1140-1200px for settings prose | Tables want the width; forms do not |
| Page skeleton | Header row (title left, primary action right) → content | The header row is the skeleton of every app page |

Sidebar anatomy: sticky brand/workspace header + independently scrolling nav groups + sticky account footer (avatar, name, role). Section labels are muted small caps. The active item is a **tinted background block + primary-colored icon and text** (a 2px left "matchstick" on light themes). The parent of the active item gets a weaker highlight. Badges: count pills, right-aligned in the item.

Dark-mode layering (re-tune, never invert): canvas ~`oklch(0.145)`, surface ~`oklch(0.205)`, borders ~10% white instead of solid gray, accent brightened one ramp step, shadows dropped in favor of borders. Persist the choice and apply it pre-paint to avoid a flash.

## KPI / Stat Cards

- **4-up** on desktop, 2-up tablet, 1-up mobile — the canonical dashboard rhythm.
- Structure: small muted label → large value → delta line (muted, colored indicator **only on the delta**).
- Icon, if any: a large **faded** icon in the corner that never covers text and is not interactive.
- Padding 16px (12px compact). The value comes from the type scale's largest step; the label from the smallest.
- **The number is the card.** A card that is mostly icon and decoration should not exist — that is a marketing element in an app.

## Data Tables

The most-convergent component across professional templates. Deviating is what makes an app look amateur.

| Part | Value |
|---|---|
| Font size | **14px at every density** — density is padding, never font |
| Row height | ~52px standard (16px cell padding) · ~40px compact (8px) · ~64px comfortable (22px) |
| Header | Tinted background (2-3% black), 1px bottom rule, ghost sort buttons: neutral double-chevron → single arrow when sorted, `aria-sort` set |
| Separators | Horizontal rules only; zebra stripes only if hover + rules still lose the user's row |
| Row hover | 2-4% tint |
| Selection | 32px checkbox column; selected row ~10% primary tint; select-all with indeterminate state |
| Row actions | Last column: 32×32 ghost icon button → right-aligned dropdown; destructive item last; never hover-revealed only |
| Status values | A **pill** (tinted background + ink), never color alone |
| Long values | Truncate in-cell; full value in a tooltip or the detail panel |
| Footer bar | Left: "0 of 5 selected" (only when selectable) · right: rows-per-page select (10/20/25/50) + "Page X of Y" + 32px icon paging buttons |
| Empty state | 96px-tall centered row: what is missing + the action that fills it |
| Sticky header | Once the table scrolls past it |

Behavior rules (the four user tasks, non-modal edit panel, column chooser, mobile stacking) live in `designing-user-experience/references/app-ui-numbers.md`.

## Forms (app)

- Stack: **label (12-14px, above) → input (36-40px tall) → helper (muted) → error (danger)**. 8px label-to-input, 16px between field groups.
- Genuinely paired fields (name/email, expiry/CVC): two-column grid, collapsing to one below 768px. Everything else: one column.
- Settings pages: section header + muted description → fields → divider → next section → one action row (sticky if the page is long).
- Focus: a 3px ring via box-shadow, not a border-color change.

## Color in Apps

- Neutrals are ~80% of the surface. One accent, derived into tints (hover ~20%, selected ~10%, focus solid).
- Solid accent only for: primary buttons, the active nav item, focus rings.
- The semantic set (success, warning, danger, info) is fixed and used identically everywhere — tint + ink pairs, always paired with text or an icon.
- "Recessed" areas (table headers, card footers, disabled zones) are 2-3% tints of the canvas, not new colors.

## Component Sizes (M3 / Apple)

| Part | Value |
|---|---|
| Touch target | 44-48px (Apple 44pt / M3 48dp); dense floor 28pt Apple, 24px WCAG 2.5.8 |
| Button height | 40px (M3); 36px shadcn; 32px sm |
| Icon button | 32×32 |
| Shape scale | Container 12-16px · control 8px · small 4px · pill for badges and status only |
| Elevation | Tonal steps first (surface lightness); shadow levels 0/1/3/6/8/12dp if used |
| Spacing | 4px base grid; 16px is the workhorse (card padding, gaps, field groups) |
