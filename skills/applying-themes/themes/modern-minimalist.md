# Modern Minimalist

Grayscale discipline. Nothing decorative survives — hierarchy comes entirely from size, weight, and space.

**Direction:** Neutral grays with a faint cool tint, near-black as the only accent.
**Best for:** Technical documentation, portfolios, systems and process docs, anything that must not date.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#ffffff` | page background |
| `surface` | `#fafafa` | raised panels, cards, table headers |
| `line` | `#e4e4e7` | borders, rules, dividers |
| `ink` | `#18181b` | primary text |
| `ink-2` | `#52525b` | secondary text |
| `ink-3` | `#71717a` | meta, captions — never body text |
| `accent` | `#09090b` | one accent, under 10% of surface |
| `accent-ink` | `#fafafa` | text and icons on `accent` |

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
| **Display** | "Instrument Sans", system-ui, sans-serif | DejaVu Sans Bold |
| **Text** | "Instrument Sans", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.200 (minor third)

## CSS

```css
:root {
  --base: #ffffff; --surface: #fafafa; --line: #e4e4e7;
  --ink: #18181b; --ink-2: #52525b; --ink-3: #71717a;
  --accent: #09090b; --accent-ink: #fafafa;
  --font-display: "Instrument Sans", system-ui, sans-serif;
  --font-text: "Instrument Sans", system-ui, sans-serif;
}
```

## Notes

With no color to lean on, spacing does all the grouping — the 4:1 inner/outer gap ratio matters more here than in any other theme. If a status color is unavoidable, add exactly one and treat it as data, not decoration.
