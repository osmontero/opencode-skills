# Desert Rose

Dusty and composed. Muted warmth with a serious center — sophistication rather than softness.

**Direction:** Blush-neutral base, plum-brown inks, a deep wine accent.
**Best for:** Boutique brands, invitations, wellness and beauty, considered personal portfolios.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#faf1ec` | page background |
| `surface` | `#fffaf7` | raised panels, cards, table headers |
| `line` | `#e8d2c8` | borders, rules, dividers |
| `ink` | `#33191f` | primary text |
| `ink-2` | `#6b4048` | secondary text |
| `ink-3` | `#94696f` | meta, captions — never body text |
| `accent` | `#8c3552` | one accent, under 10% of surface |
| `accent-ink` | `#fff5f7` | text and icons on `accent` |

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
| **Display** | "Italiana", Georgia, serif | DejaVu Serif Bold |
| **Text** | "Crimson Pro", Georgia, serif | DejaVu Serif |

**Scale ratio:** 1.500 (perfect fifth)

## CSS

```css
:root {
  --base: #faf1ec; --surface: #fffaf7; --line: #e8d2c8;
  --ink: #33191f; --ink-2: #6b4048; --ink-3: #94696f;
  --accent: #8c3552; --accent-ink: #fff5f7;
  --font-display: "Italiana", Georgia, serif;
  --font-text: "Crimson Pro", Georgia, serif;
}
```

## Notes

The only theme here that sets body text in a serif. It needs a generous measure and loose leading (1.65) — at tight leading the serif reads as cramped rather than elegant.
