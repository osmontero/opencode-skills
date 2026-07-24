# Color and Theming

## Build a Ramp, Not a Set of Colors

Picking colors one at a time as components need them produces a palette that never resolves. Build the full ramp first, then only use what is in it.

**A complete interface palette:**

```
base      page background
surface   raised panels, cards, inputs
surface-2 nested / hover surfaces
line      borders, rules, dividers
ink       primary text                — 4.5:1 min on base
ink-2     secondary text              — 4.5:1 min on base
ink-3     tertiary / meta / disabled  — 3:1 min, never body text
accent    one, under 10% of surface
accent-ink readable text on accent    — 4.5:1 against accent
```

Plus, only if the interface actually needs them: `positive`, `negative`, `warning`, `info` — each with a `-bg` and `-ink` partner.

**Three ink levels is enough.** A fourth means the hierarchy is unclear and should be solved with space or weight instead.

## Choose a Hue Strategy

| Strategy | Construction | Reads as |
|---|---|---|
| **Monochromatic** | One hue, vary lightness and chroma only | Disciplined, calm, hardest to get wrong |
| **Analogous** | Base hue ± 30° | Cohesive, natural, warm or cool as a whole |
| **Complementary** | Base + 180°, one dominant one accent | High tension, strong focal points |
| **Split-complement** | Base + 150° and + 210° | Complementary energy, less crude |
| **Triadic** | Three hues 120° apart | Vibrant, needs one clear dominant |
| **Neutral + spot** | Grays/tints + one saturated hue | Editorial, most versatile |

Commit to one. Two saturated accents from unrelated hue families is the fastest way to make an interface look assembled rather than designed.

## Neutrals Are Never Neutral

Pure grays (`#888`) look dead against any colored content. Tint every neutral toward the accent or its complement.

```css
/* Warm-tinted neutrals for a warm accent */
--base: #faf8f5; --surface: #ffffff; --line: #e8e2d9;
--ink: #1a1613;  --ink-2: #57504a;  --ink-3: #8d857b;

/* Cool-tinted neutrals for a cool accent */
--base: #f7f8fa; --surface: #ffffff; --line: #dfe3ea;
--ink: #10131a;  --ink-2: #4c5462;  --ink-3: #838c9c;
```

Build the tint by mixing the accent into the neutral at 3-8%:

```css
--line: color-mix(in oklch, var(--accent) 6%, #e5e5e5);
```

## Use OKLCH

`oklch(L C H)` is perceptually uniform: equal lightness steps look equally different, which HSL does not deliver. `oklch(0.6 0.2 250)` and `oklch(0.6 0.2 140)` genuinely match in brightness; `hsl(250 70% 50%)` and `hsl(140 70% 50%)` do not.

```css
--accent-h: 25; --accent-c: 0.16;
--accent-100: oklch(0.96 calc(var(--accent-c) * 0.2) var(--accent-h));
--accent-300: oklch(0.84 calc(var(--accent-c) * 0.6) var(--accent-h));
--accent-500: oklch(0.62 var(--accent-c) var(--accent-h));
--accent-700: oklch(0.45 calc(var(--accent-c) * 0.9) var(--accent-h));
--accent-900: oklch(0.28 calc(var(--accent-c) * 0.7) var(--accent-h));
```

Changing `--accent-h` alone re-themes the whole ramp coherently. Note that chroma must drop at the light and dark ends — holding it constant produces muddy, unattainable colors that get clipped to sRGB.

## Contrast Requirements

WCAG 2.2 AA, non-negotiable:

| Content | Minimum |
|---|---|
| Body text | 4.5:1 |
| Text ≥ 24px, or ≥ 18.66px bold | 3:1 |
| Icons and UI component boundaries carrying meaning | 3:1 |
| Focus indicator against adjacent colors | 3:1 |
| Disabled elements | exempt — but if users must read it, it is not decoration |

Verify, do not estimate. Contrast is not eyeballable, especially for mid-tone accents on mid-tone surfaces.

```python
def relative_luminance(hexstr):
    r, g, b = (int(hexstr.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(fg, bg):
    a, b = relative_luminance(fg), relative_luminance(bg)
    lo, hi = sorted((a, b))
    return round((hi + 0.05) / (lo + 0.05), 2)

print(contrast('#55504a', '#f4f1ea'))   # 7.15 — passes AA for body
```

The `applying-themes` skill bundles `scripts/check_contrast.py`, which validates a whole theme file at once.

**The most common failure:** a mid-saturation accent used as a text color on a light background. `#4a90d9` on white is 2.9:1 — it fails. Darken the accent for text use and keep the bright value for fills only. This is exactly why the ramp needs a `-700` step.

## Semantic Token Layers

Three layers. Components only ever reference layer 3.

```css
:root {
  /* 1. Primitives — raw values, no meaning */
  --blue-500: oklch(0.62 0.16 250);
  --gray-50:  oklch(0.98 0.004 250);
  --gray-900: oklch(0.19 0.012 250);

  /* 2. Semantic — meaning, no component */
  --color-bg: var(--gray-50);
  --color-fg: var(--gray-900);
  --color-accent: var(--blue-500);

  /* 3. Component — what the CSS actually uses */
  --btn-bg: var(--color-accent);
  --btn-fg: white;
  --card-bg: var(--color-bg);
}
```

Dark mode then only overrides layer 2. Component CSS never changes.

## Dark Mode

Dark mode is not an inversion. Naive inversion produces glare and destroys depth.

| Rule | Why |
|---|---|
| Never pure black `#000` for the page | Causes halation against light text; use `oklch(0.16 0.01 h)` |
| Never pure white `#fff` for text | Too much contrast is fatiguing; use `oklch(0.94 0.01 h)` |
| Elevation goes **lighter**, not darker | Shadows are invisible on dark. Raised surfaces get a lighter tint. |
| Reduce accent chroma ~15-25% | Saturated colors vibrate against dark backgrounds |
| Increase accent lightness | A `-500` accent that worked on white needs `-400` on dark |
| Soften large images | `filter: brightness(0.85)` prevents a photo from becoming the page's light source |

```css
:root {
  --color-bg: oklch(0.98 0.004 250); --color-surface: oklch(1 0 0);
  --color-fg: oklch(0.19 0.012 250); --color-accent: oklch(0.55 0.17 250);
  --shadow: 0 1px 2px oklch(0 0 0 / 0.06), 0 8px 24px oklch(0 0 0 / 0.08);
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: oklch(0.16 0.012 250); --color-surface: oklch(0.21 0.014 250);
    --color-fg: oklch(0.94 0.008 250); --color-accent: oklch(0.72 0.14 250);
    --shadow: 0 1px 2px oklch(0 0 0 / 0.4), 0 8px 24px oklch(0 0 0 / 0.5);
  }
}
:root[data-theme="dark"]  { /* repeat the dark block — manual toggle must win */ }
:root[data-theme="light"] { /* repeat the light block */ }
```

Support both the media query *and* an explicit `data-theme` attribute. A toggle that cannot override the OS preference in both directions is broken.

## Color Is Never the Only Signal

About 8% of men have some form of color vision deficiency. Any state communicated by color alone is invisible to them.

| Wrong | Right |
|---|---|
| Red text = error | Red text + icon + the word "Error" |
| Green dot = online | Green filled dot vs. gray hollow dot + label |
| Colored line = series | Color + distinct dash pattern or direct label |
| Red/green diff | Color + `+`/`−` prefix |

## Gradients and Texture

Gradients earn their place when they create atmosphere, not when they decorate a button.

```css
/* Mesh — layered radial gradients, unexpected hue pair */
background:
  radial-gradient(60% 50% at 15% 20%, oklch(0.55 0.18 40 / .35), transparent 60%),
  radial-gradient(50% 45% at 85% 75%, oklch(0.5 0.15 195 / .30), transparent 60%),
  oklch(0.15 0.02 250);
```

**Rules:** interpolate in `oklab` or `oklch` (`linear-gradient(in oklch, ...)`) to avoid the gray dead zone that sRGB interpolation produces between complementary hues. Keep gradients behind content, never on text. And avoid purple→blue on white — it is the single most recognizable AI-generated palette.

## Common Mistakes

**Accent used as a background *and* as body text.** The value that works as a fill is almost never dark enough for text. Two steps of the ramp, not one value.

**Untinted grays with a saturated accent.** The grays look dirty. Mix 4-8% of the accent into every neutral.

**Semantic colors invented per component.** `--card-border: #ddd` in one file and `#e0e0e0` in another. All borders come from `--line`.

**Dark mode contrast never checked.** Light-mode contrast passing tells you nothing about dark mode. Check both.

**Opacity used to make text secondary.** `opacity: 0.6` on text over a patterned or image background produces unpredictable contrast. Use a real `--ink-2` color.
