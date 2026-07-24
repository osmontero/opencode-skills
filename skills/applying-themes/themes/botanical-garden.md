# Botanical Garden

Cultivated and alive. Garden colors handled with restraint — a seed catalog, not a flower shop.

**Direction:** Warm paper base, deep leaf inks, one terracotta accent.
**Best for:** Food and agriculture, craft and maker brands, community programs, seasonal reports.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#f6f5ef` | page background |
| `surface` | `#fffefa` | raised panels, cards, table headers |
| `line` | `#dddcc9` | borders, rules, dividers |
| `ink` | `#1f2a1c` | primary text |
| `ink-2` | `#4d5a44` | secondary text |
| `ink-3` | `#7b886e` | meta, captions — never body text |
| `accent` | `#a83a1f` | one accent, under 10% of surface |
| `accent-ink` | `#fff6f3` | text and icons on `accent` |

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
| **Display** | "Bricolage Grotesque", "Trebuchet MS", sans-serif | DejaVu Sans Bold |
| **Text** | "Lora", Georgia, serif | DejaVu Serif |

**Scale ratio:** 1.333 (perfect fourth)

## CSS

```css
:root {
  --base: #f6f5ef; --surface: #fffefa; --line: #dddcc9;
  --ink: #1f2a1c; --ink-2: #4d5a44; --ink-3: #7b886e;
  --accent: #a83a1f; --accent-ink: #fff6f3;
  --font-display: "Bricolage Grotesque", "Trebuchet MS", sans-serif;
  --font-text: "Lora", Georgia, serif;
}
```

## Notes

Terracotta and leaf green are close in luminance — do not place them adjacent at large sizes or the edge vibrates. Separate them with `base` or `line`.
