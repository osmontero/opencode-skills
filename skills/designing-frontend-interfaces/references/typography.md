# Typography

Type is the largest surface in almost every interface. It carries more of the aesthetic signal than color does.

## Choosing Faces

**Two faces maximum.** A display face with character, and a text face that disappears. A third face is almost always a mistake; the exception is adding a mono for code or numerals.

**The pairing rule:** contrast the *skeleton*, share the *mood*. A high-contrast serif with a geometric sans works because the skeletons differ sharply. Two humanist sans-serifs conflict because they are nearly the same idea executed slightly differently.

| Pairing strategy | Display | Text | Reads as |
|---|---|---|---|
| Serif + Mono | Instrument Serif, Gloock, Young Serif | IBM Plex Mono, Geist Mono | Technical authority |
| Serif + Sans | Playfair, Lora, Crimson Pro | Instrument Sans, Work Sans | Editorial |
| Sans + Serif | Big Shoulders, Archivo | Crimson Pro, Libre Baskerville | Modern with warmth |
| Grotesque solo | Work Sans / Neue Haas at 3 weights | same face | Swiss rationalist |
| Mono solo | Geist Mono, DM Mono, Red Hat Mono | same face | Systems / terminal |
| Display + Grotesque | Erica One, Tektur, Boldonse | Instrument Sans | Loud consumer |

**Never use as a display face:** Inter, Roboto, Open Sans, Lato, Montserrat, Poppins, Arial, `system-ui`. These are the generic-AI signature. Inter is acceptable for body text and genuinely excellent for tabular numerals — but the moment it sets a headline, the design reads as untouched default.

## Sourcing Faces

Self-hosted, no external requests (required for artifacts under CSP):

```css
@font-face {
  font-family: "Instrument Serif";
  src: url("data:font/woff2;base64,...") format("woff2");
  font-display: swap;
}
```

The `designing-canvas-art` skill bundles ~40 open-licensed TTFs under `canvas-fonts/` — Instrument Serif, Big Shoulders, Bricolage Grotesque, Crimson Pro, Geist Mono, Gloock, IBM Plex Serif/Mono, Italiana, JetBrains Mono, Lora, National Park, Outfit, Poiret One, Tektur, Work Sans, Young Serif and more. Convert to woff2 and inline for artifacts.

Google Fonts is fine when external requests are allowed. Subset aggressively:

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=IBM+Plex+Mono:wght@400;600&display=swap">
```

Always name a real fallback in the same metric class. `serif` and `sans-serif` alone cause visible reflow.

## Building the Scale

Pick one ratio and generate every size from it. Never choose a size by eye.

| Ratio | Value | Use for |
|---|---|---|
| Minor third | 1.200 | Dense UI, dashboards, tables, settings |
| Major third | 1.250 | General product UI — the safe default |
| Perfect fourth | 1.333 | Marketing, docs, content sites |
| Perfect fifth | 1.500 | Editorial, posters, high-drama landing pages |

```
step_n = base × ratio^n     base = 1rem = 16px
```

At 1.250: `0.64 · 0.8 · 1 · 1.25 · 1.563 · 1.953 · 2.441 · 3.052 · 3.815`

**Fluid type** — one clamp per step, so it scales between breakpoints without media queries:

```css
--step-0: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
--step-3: clamp(1.75rem, 1.4rem + 1.75vw, 2.5rem);
--step-6: clamp(3rem, 1.8rem + 6vw, 6rem);
```

Cap the top. Unbounded `vw` sizing produces absurd headlines on ultrawide monitors.

## Setting Text

| Property | Rule |
|---|---|
| **Measure** | 60-75 characters for body. `max-width: 68ch`. Under 45ch feels choppy, over 85ch loses the line. |
| **Leading** | Inverse to size. Body `1.5-1.65`. Headings `1.05-1.2`. Display over 3rem often `0.95`. |
| **Tracking** | Large text needs negative tracking (`-0.02em` to `-0.04em`). Small caps and tiny labels need positive (`0.05em` to `0.12em`). Body text needs none. |
| **Weight** | Three maximum. Typically 400 / 500-600 / 700. Six weights of one face is a slop signal. |
| **Alignment** | Flush left. Justified text without hyphenation creates rivers; if justifying, add `hyphens: auto`. Never center more than two lines. |
| **Paragraph spacing** | Space between paragraphs *or* an indent. Never both. |

```css
h1 { font-size: var(--step-6); line-height: 0.95; letter-spacing: -0.03em; text-wrap: balance; }
p  { font-size: var(--step-0); line-height: 1.6;  max-width: 68ch; text-wrap: pretty; }
.label { font-size: var(--step--1); letter-spacing: 0.1em; text-transform: uppercase; }
```

`text-wrap: balance` on headings prevents orphaned last words. `text-wrap: pretty` on body prevents single-word final lines. Both are cheap and visibly improve craft.

## Numerals

Data-heavy interfaces live or die here.

```css
.numeric { font-variant-numeric: tabular-nums lining-nums; }
.prose   { font-variant-numeric: oldstyle-nums proportional-nums; }
```

Tabular figures are **required** for any column of numbers that updates or aligns. Without them, digits jitter as values change. Old-style figures (which have ascenders and descenders) belong in running prose set in a serif — they look wrong in tables.

## Optical Corrections

Mathematically centered is not visually centered.

- **Text in buttons** sits optically high because descenders create phantom space below. Subtract 1-2px from bottom padding.
- **Uppercase-only text** has no descenders and looks bottom-heavy when vertically centered. Nudge it up.
- **Punctuation hangs.** A quotation mark starting a pull quote should hang left of the text edge (`text-indent: -0.4em`).
- **Icons beside text** align to the cap height or the x-height, not the line box.
- **Large display type** needs tighter tracking than the same face at body size. Optical sizing (`font-optical-sizing: auto`) handles this automatically on variable fonts that support it.

## Loading Performance

```css
@font-face { font-display: swap; }  /* text visible immediately in fallback */
```

Preload only the faces used above the fold:

```html
<link rel="preload" href="/fonts/display.woff2" as="font" type="font/woff2" crossorigin>
```

Match fallback metrics to avoid layout shift:

```css
@font-face {
  font-family: "Display Fallback"; src: local("Georgia");
  size-adjust: 105%; ascent-override: 92%; descent-override: 22%;
}
```

## Common Mistakes

**Scale abandoned mid-build.** Headings use the scale; a caption somewhere uses `13px`. Grep for `px` in font-size declarations.

**Line-height as a single global value.** `line-height: 1.5` on an `h1` at 4rem is a wall of text. Leading must vary inversely with size.

**Centered body copy.** Centering is for one to two lines of display text. Centered paragraphs are painful to read because every line starts at a different x-position.

**All-caps long strings.** Uppercase is legible for 1-3 words. A full uppercase sentence loses word-shape recognition and reads ~15% slower.

**Letter-spacing applied to body text.** Body faces are already spaced correctly by their designer. Tracking belongs on display sizes and tiny labels only.
