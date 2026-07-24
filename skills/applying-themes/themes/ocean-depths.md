# Ocean Depths

Deep maritime calm. Dark, composed, and quietly authoritative — the trust of a research vessel rather than a corporate brochure.

**Direction:** Dark base, cool neutrals tinted blue, a single luminous teal accent.
**Best for:** Financial reporting, consulting decks, infrastructure dashboards, trust-building content.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#0f1c26` | page background |
| `surface` | `#16283a` | raised panels, cards, table headers |
| `line` | `#2d4859` | borders, rules, dividers |
| `ink` | `#eef6f8` | primary text |
| `ink-2` | `#accad4` | secondary text |
| `ink-3` | `#8aa7b3` | meta, captions — never body text |
| `accent` | `#4fd1c5` | one accent, under 10% of surface |
| `accent-ink` | `#04222a` | text and icons on `accent` |

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
| **Display** | "Young Serif", Georgia, serif | DejaVu Serif Bold |
| **Text** | "IBM Plex Sans", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.250 (major third)

## CSS

```css
:root {
  --base: #0f1c26; --surface: #16283a; --line: #2d4859;
  --ink: #eef6f8; --ink-2: #accad4; --ink-3: #8aa7b3;
  --accent: #4fd1c5; --accent-ink: #04222a;
  --font-display: "Young Serif", Georgia, serif;
  --font-text: "IBM Plex Sans", system-ui, sans-serif;
}
```

## Notes

The teal accent is the only saturated color — keep it for emphasis and data highlights, never for large fills. On dark backgrounds, soften photographs with `filter: brightness(.85)` so they do not become the page's light source.
