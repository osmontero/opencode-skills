# Golden Hour

Late-afternoon amber. Rich and inviting without becoming sepia nostalgia.

**Direction:** Warm cream base, cocoa inks, a deep amber accent.
**Best for:** Annual reviews, food and hospitality, retrospectives, warm brand storytelling.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#fbf5ea` | page background |
| `surface` | `#fffdf8` | raised panels, cards, table headers |
| `line` | `#e8dcc4` | borders, rules, dividers |
| `ink` | `#2a2018` | primary text |
| `ink-2` | `#5c4a37` | secondary text |
| `ink-3` | `#8a7357` | meta, captions — never body text |
| `accent` | `#b45309` | one accent, under 10% of surface |
| `accent-ink` | `#fffbeb` | text and icons on `accent` |

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
| **Display** | "Gloock", Georgia, serif | DejaVu Serif Bold |
| **Text** | "Outfit", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.333 (perfect fourth)

## CSS

```css
:root {
  --base: #fbf5ea; --surface: #fffdf8; --line: #e8dcc4;
  --ink: #2a2018; --ink-2: #5c4a37; --ink-3: #8a7357;
  --accent: #b45309; --accent-ink: #fffbeb;
  --font-display: "Gloock", Georgia, serif;
  --font-text: "Outfit", system-ui, sans-serif;
}
```

## Notes

The amber accent fails contrast as small text on the cream base at lighter values — the `#b45309` given here passes, but do not lighten it toward mustard for text use. Keep bright yellow for fills only.
