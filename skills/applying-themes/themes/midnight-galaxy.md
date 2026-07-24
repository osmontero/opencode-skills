# Midnight Galaxy

Deep-space drama. Dark and atmospheric, with depth built from light rather than shadow.

**Direction:** Very dark violet base, violet-tinted neutrals, one luminous lavender accent.
**Best for:** Launch pages, entertainment and gaming, keynote decks, anything that should feel like an event.

## Palette

| token | hex | role |
|---|---|---|
| `base` | `#14101f` | page background |
| `surface` | `#1e1830` | raised panels, cards, table headers |
| `line` | `#372e4d` | borders, rules, dividers |
| `ink` | `#ece8f7` | primary text |
| `ink-2` | `#b5abcf` | secondary text |
| `ink-3` | `#948aae` | meta, captions — never body text |
| `accent` | `#a78bfa` | one accent, under 10% of surface |
| `accent-ink` | `#150c26` | text and icons on `accent` |

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
| **Display** | "Boldonse", "Trebuchet MS", sans-serif | DejaVu Sans Bold |
| **Text** | "Instrument Sans", system-ui, sans-serif | DejaVu Sans |

**Scale ratio:** 1.500 (perfect fifth)

## CSS

```css
:root {
  --base: #14101f; --surface: #1e1830; --line: #372e4d;
  --ink: #ece8f7; --ink-2: #b5abcf; --ink-3: #948aae;
  --accent: #a78bfa; --accent-ink: #150c26;
  --font-display: "Boldonse", "Trebuchet MS", sans-serif;
  --font-text: "Instrument Sans", system-ui, sans-serif;
}
```

## Notes

Violet-on-dark is close to the canonical AI-generated gradient. Keep it away from blue: the accent should stay in the lavender range and the base should stay violet, never drifting toward indigo. Depth comes from lighter raised surfaces, not from shadows — shadows are invisible here.
