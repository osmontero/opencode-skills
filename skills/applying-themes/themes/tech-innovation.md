# Tech Innovation

Terminal-adjacent and high contrast. Reads as a product surface, not a marketing page.

**Direction:** Near-black base, cool neutrals, one luminous sky accent.
**Best for:** Developer tools, AI and infrastructure products, changelogs, status pages, API docs.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#0b0e14` | page background |
| `surface` | `#131924` | raised panels, cards, table headers |
| `line` | `#26314a` | borders, rules, dividers |
| `ink` | `#e8eef7` | primary text |
| `ink-2` | `#a7b6ca` | secondary text |
| `ink-3` | `#8496ad` | meta, captions — never body text |
| `accent` | `#38bdf8` | one accent, under 10% of surface |
| `accent-ink` | `#031824` | text and icons on `accent` |

```contrast
ink        on base    AA
ink-2      on base    AA
ink-3      on base    AA-large
ink        on surface AA
accent     on base    UI
accent-ink on accent  AA
```

## Typography

| | Web | PDF / slides (metric-safe) |
|---|---|---|
| **Display** | "Tektur", "Trebuchet MS", sans-serif | DejaVu Sans Bold |
| **Text** | "Geist Mono", ui-monospace, monospace | DejaVu Sans Mono |

**Scale ratio:** 1.200 (minor third)

## CSS

```css
:root {
  --base: #0b0e14; --surface: #131924; --line: #26314a;
  --ink: #e8eef7; --ink-2: #a7b6ca; --ink-3: #8496ad;
  --accent: #38bdf8; --accent-ink: #031824;
  --font-display: "Tektur", "Trebuchet MS", sans-serif;
  --font-text: "Geist Mono", ui-monospace, monospace;
}
```

## Notes

Mono body text needs a smaller scale ratio than proportional text — 1.200 keeps the levels distinguishable without the jumps becoming absurd. Never use the cyan accent as a text color on `surface`; it is a fill and border color.
