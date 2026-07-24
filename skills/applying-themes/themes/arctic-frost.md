# Arctic Frost

Cold clarity. Precise, clinical, and unmistakably legible — winter light rather than winter mood.

**Direction:** Pale blue-white base, blue-tinted neutrals, one deep steel accent.
**Best for:** Medical and scientific reporting, analytics dashboards, compliance and audit documents.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#f4f8fc` | page background |
| `surface` | `#ffffff` | raised panels, cards, table headers |
| `line` | `#d8e4f0` | borders, rules, dividers |
| `ink` | `#0f1b28` | primary text |
| `ink-2` | `#42576b` | secondary text |
| `ink-3` | `#67809a` | meta, captions — never body text |
| `accent` | `#15588f` | one accent, under 10% of surface |
| `accent-ink` | `#f0f7ff` | text and icons on `accent` |

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
| **Display** | "Jura", "Trebuchet MS", sans-serif | DejaVu Sans Bold |
| **Text** | "IBM Plex Sans", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.200 (minor third)

## CSS

```css
:root {
  --base: #f4f8fc; --surface: #ffffff; --line: #d8e4f0;
  --ink: #0f1b28; --ink-2: #42576b; --ink-3: #67809a;
  --accent: #15588f; --accent-ink: #f0f7ff;
  --font-display: "Jura", "Trebuchet MS", sans-serif;
  --font-text: "IBM Plex Sans", system-ui, sans-serif;
}
```

## Notes

Built for density. Pair with tabular numerals (`font-variant-numeric: tabular-nums`) on every numeric column — this theme is most often used where numbers align.
