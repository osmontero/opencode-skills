# Sunset Boulevard

Golden-hour warmth with real heat in it. Energetic without tipping into novelty.

**Direction:** Warm off-white base, cocoa inks, a burnt-orange accent that carries the whole identity.
**Best for:** Creative portfolios, launch announcements, culture and hospitality decks, event pages.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#fdf6ee` | page background |
| `surface` | `#fffcf7` | raised panels, cards, table headers |
| `line` | `#ead7c2` | borders, rules, dividers |
| `ink` | `#2b1a12` | primary text |
| `ink-2` | `#6b4a35` | secondary text |
| `ink-3` | `#8f6f57` | meta, captions — never body text |
| `accent` | `#c2410c` | one accent, under 10% of surface |
| `accent-ink` | `#fff7ed` | text and icons on `accent` |

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
| **Text** | "Instrument Sans", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.333 (perfect fourth)

## CSS

```css
:root {
  --base: #fdf6ee; --surface: #fffcf7; --line: #ead7c2;
  --ink: #2b1a12; --ink-2: #6b4a35; --ink-3: #8f6f57;
  --accent: #c2410c; --accent-ink: #fff7ed;
  --font-display: "Bricolage Grotesque", "Trebuchet MS", sans-serif;
  --font-text: "Instrument Sans", system-ui, sans-serif;
}
```

## Notes

Resist adding a second warm accent — coral and sand read as decoration next to the burnt orange and dilute it. If a secondary is genuinely needed, use `ink-3` as a warm gray.
