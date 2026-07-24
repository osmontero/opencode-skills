# Forest Canopy

Grounded and unhurried. Earth tones that feel cultivated rather than rustic.

**Direction:** Light bone base, deep green inks, one saturated forest accent.
**Best for:** Sustainability reports, outdoor and craft brands, long-form editorial, environmental data.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#f7f6f0` | page background |
| `surface` | `#fffffb` | raised panels, cards, table headers |
| `line` | `#dcded1` | borders, rules, dividers |
| `ink` | `#1a271a` | primary text |
| `ink-2` | `#4a5a46` | secondary text |
| `ink-3` | `#79876f` | meta, captions — never body text |
| `accent` | `#2f6b3c` | one accent, under 10% of surface |
| `accent-ink` | `#f4fbf5` | text and icons on `accent` |

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
| **Text** | "Work Sans", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.333 (perfect fourth)

## CSS

```css
:root {
  --base: #f7f6f0; --surface: #fffffb; --line: #dcded1;
  --ink: #1a271a; --ink-2: #4a5a46; --ink-3: #79876f;
  --accent: #2f6b3c; --accent-ink: #f4fbf5;
  --font-display: "Young Serif", Georgia, serif;
  --font-text: "Work Sans", system-ui, sans-serif;
}
```

## Notes

Works best with generous measure (68ch) and large vertical rhythm. The green accent is dark enough for body links; use it on text as well as fills.
