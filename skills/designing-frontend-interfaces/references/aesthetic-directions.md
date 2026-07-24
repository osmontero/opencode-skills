# Aesthetic Directions

A catalog of concrete directions, each parameterized enough to build from and different enough from the others that picking a new one produces genuinely different output.

**How to use:** pick one at Step 1. Name it in the brief. Then let its parameters drive the token block. Do not blend three directions — that produces mush. Blending exactly two, deliberately, with one dominant, is how new directions get made.

**Anti-convergence rule:** track what you used last time. If the last three interfaces were dark backgrounds with a neon accent, the next one is light. Rotate across the axes: light/dark, serif/sans/mono, dense/airy, geometric/organic, flat/dimensional.

---

## 1. Technical Broadsheet

Newspaper density meets terminal precision. Information-dense, authoritative, no ornament.

| | |
|---|---|
| **Type** | High-contrast serif display (Instrument Serif, Playfair, Young Serif) + mono text (IBM Plex Mono, JetBrains Mono) |
| **Scale** | 1.333 — big jumps between levels |
| **Color** | Warm newsprint `#f4f1ea`, near-black ink, one signal color for alerts |
| **Layout** | Multi-column, hairline rules, hanging marginalia, tight leading |
| **Radius** | 0 |
| **Shadow** | None. Rules and space only. |
| **Motion** | Almost none. Instant state changes. |
| **Good for** | Changelogs, docs, data tools, research, developer products |

## 2. Swiss Rationalist

Grid-absolute, typographic, unemotional. Every element on a module.

| | |
|---|---|
| **Type** | One neutral grotesque at 3 weights (Helvetica Now, Neue Haas, Work Sans) |
| **Scale** | 1.250 |
| **Color** | White, black, exactly one saturated primary (red or blue) |
| **Layout** | Visible 12-column module, flush-left ragged-right, generous top margins |
| **Radius** | 0 |
| **Shadow** | None |
| **Motion** | Linear, brief, functional |
| **Good for** | Portfolios, agencies, museums, editorial systems |

## 3. Warm Editorial

Magazine feature spread. Photography-led, generous, humane.

| | |
|---|---|
| **Type** | Old-style serif text (Crimson Pro, Lora, Libre Baskerville) + a light sans for furniture |
| **Scale** | 1.500 — dramatic display, comfortable body |
| **Color** | Cream/bone base, deep brown-black ink, muted earth accent |
| **Layout** | 65-75ch measure, drop caps, pull quotes, asymmetric image bleeds |
| **Radius** | 0 or 2px |
| **Shadow** | None; depth from image layering |
| **Motion** | Slow fades on scroll, 500-700ms |
| **Good for** | Long-form, essays, brand stories, journals |

## 4. Brutalist Raw

Structure exposed. Deliberately unpolished, high-impact, honest about being a web page.

| | |
|---|---|
| **Type** | Heavy grotesque or condensed (Big Shoulders, Archivo Black) + default mono |
| **Scale** | 1.500+ — extreme contrast between huge and tiny |
| **Color** | Stark: pure white/pure black + one aggressive accent (safety orange, acid green) |
| **Layout** | Visible borders everywhere, overlapping blocks, intentional misalignment, no max-width |
| **Radius** | 0 |
| **Shadow** | Hard offset shadows (`4px 4px 0 black`), never blurred |
| **Motion** | Snappy, 80-120ms, no easing |
| **Good for** | Music, events, experimental tools, anything counter-corporate |

## 5. Soft Utility

Calm, rounded, quietly friendly. Restraint with warmth — the hardest to do without sliding into generic.

| | |
|---|---|
| **Type** | Humanist sans (Instrument Sans, Outfit, National Park) at 2 weights |
| **Scale** | 1.200 — dense, many close levels |
| **Color** | Low-saturation base (warm gray, pale sage), soft ink, one desaturated accent |
| **Layout** | Airy, single generous column, no hard borders — separation by tint |
| **Radius** | One value, 8-12px, everywhere |
| **Shadow** | Two: `0 1px 2px rgb(0 0 0/.04)` and `0 8px 24px rgb(0 0 0/.06)` |
| **Motion** | 200ms ease-out, subtle scale on press |
| **Good for** | Productivity apps, settings, dashboards, health |
| **Danger** | This is closest to the AI default. Earn it: the palette must be specific and the type must not be Inter. |

## 6. Art Deco Geometric

Symmetry, metallics, stepped forms, luxury restraint.

| | |
|---|---|
| **Type** | Geometric display with high waist (Poiret One, Italiana, Gloock) + clean sans |
| **Scale** | 1.333 |
| **Color** | Deep ink (navy, oxblood, forest) + warm metallic (`#c8a862`) + cream |
| **Layout** | Centered symmetry, stepped/chevron dividers, thin double rules, framed blocks |
| **Radius** | 0, with chamfered corners via `clip-path` |
| **Shadow** | None; depth from layered rules |
| **Motion** | Slow symmetric reveals, 400-600ms |
| **Good for** | Hospitality, spirits, events, premium goods |

## 7. Terminal Phosphor

Monospace everything, CRT nostalgia, systems aesthetic. Not the same as Technical Broadsheet — this one is dark and glowing.

| | |
|---|---|
| **Type** | Mono only (Geist Mono, Red Hat Mono, DM Mono) at 2 weights |
| **Scale** | 1.200 — mono needs small jumps |
| **Color** | Near-black `#0a0c0a`, phosphor foreground (amber `#ffb000` or green `#33ff66`), dim gray secondary |
| **Layout** | Fixed character grid, ASCII rules (`───`), bracket labels, no images |
| **Radius** | 0 |
| **Shadow** | `text-shadow` glow on the accent only |
| **Motion** | Typewriter reveals, block cursor blink, step easing |
| **Good for** | CLIs, infra, logs, security, status pages |

## 8. Botanical Organic

Curves, natural palettes, illustrative texture. Warm without being soft-utility bland.

| | |
|---|---|
| **Type** | Softened serif (Young Serif, Bricolage Grotesque) + rounded sans |
| **Scale** | 1.333 |
| **Color** | Deep green base or bone base, terracotta/ochre/moss secondaries |
| **Layout** | Blob shapes via `border-radius: 60% 40% 55% 45%`, overlapping organic forms, off-grid placement |
| **Radius** | Irregular by design |
| **Shadow** | Soft, large, low-opacity, tinted with the base hue — never gray |
| **Motion** | Slow drift, 600ms+, gentle ease-in-out |
| **Good for** | Food, wellness, sustainability, craft |

## 9. Chromatic Maximalist

Saturated, layered, loud, deliberate. Needs *more* system discipline than minimalism, not less.

| | |
|---|---|
| **Type** | Display face with personality (Erica One, Tektur, Boldonse) + neutral sans for readability |
| **Scale** | 1.500 |
| **Color** | 4-6 saturated hues from one harmonic family, plus black and white as rest |
| **Layout** | Layered z-planes, rotated elements, sticker/collage overlaps, full-bleed color blocks |
| **Radius** | Committed extreme — 0 or full pill, nothing between |
| **Shadow** | Hard offsets in a palette color, not black |
| **Motion** | Staggered entrance, 60ms increments, `back-out` easing |
| **Good for** | Consumer, gaming, youth brands, launches |
| **Danger** | Loud ≠ arbitrary. One type scale, one space scale, one harmonic family. |

## 10. Ledger Minimal

Financial precision. Tabular, tight, trustworthy, near-monochrome.

| | |
|---|---|
| **Type** | Sans with true tabular figures (IBM Plex Sans, Inter *for numerals only*) + mono for values |
| **Scale** | 1.200 |
| **Color** | White, three grays, one green and one red used **only** for signed values |
| **Layout** | Dense tables, right-aligned numerals, hairline row rules, sticky headers |
| **Radius** | 0 or 2px |
| **Shadow** | Only on sticky/overlay surfaces |
| **Motion** | Number transitions only |
| **Good for** | Fintech, analytics, admin, reporting |
| **Required** | `font-variant-numeric: tabular-nums` on every numeric column |

## 11. Kinetic Gradient

Motion and color-field as the primary material. Dark, atmospheric, depth from light not shadow.

| | |
|---|---|
| **Type** | Wide geometric sans (Jura, Tektur) + neutral text face |
| **Scale** | 1.333 |
| **Color** | Very dark base, 2-3 hue mesh gradient, near-white text |
| **Layout** | Full-bleed gradient fields, glass surfaces (`backdrop-filter: blur(20px)`), centered focal content |
| **Radius** | 16-24px, consistent |
| **Shadow** | Glow rather than shadow — colored, large, low opacity |
| **Motion** | Continuous slow gradient drift, parallax, 800ms+ |
| **Good for** | AI/ML products, developer platforms, launches |
| **Danger** | The purple-blue mesh is the canonical AI-slop gradient. Use unexpected pairs: rust/teal, amber/indigo, moss/plum. |

## 12. Paper Craft

Physical materials simulated honestly: layered stock, torn edges, print registration, visible grain.

| | |
|---|---|
| **Type** | Letterpress-flavored serif (Libre Baskerville, Lora) + condensed sans labels |
| **Scale** | 1.333 |
| **Color** | Off-white stock, ink colors that look mixed not digital, one spot color |
| **Layout** | Layered "sheets" at slight rotations, `clip-path` torn edges, visible grain overlay |
| **Radius** | 0, with irregular clip-paths |
| **Shadow** | Tight contact shadow directly under each sheet, 2-4px blur |
| **Motion** | Page-turn and slide, 350ms |
| **Good for** | Portfolios, zines, invitations, archives |

## Grain Overlay Recipe

Used by Warm Editorial, Paper Craft, and Botanical Organic. Self-contained, no image file:

```css
.grain::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  opacity: .035; mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
@media (prefers-reduced-transparency: reduce) { .grain::after { display: none } }
```

## Inventing a Direction

When none of the above fits, build one from a real-world reference rather than from adjectives.

1. **Name a physical artifact** — a 1970s Japanese camera manual, a Le Corbusier floor plan, a seed catalog, an airline safety card, a botanical plate.
2. **List what makes it recognizable** — 5 concrete traits: its palette, its type, how it uses rules, how it handles density, its one signature move.
3. **Map each trait to a token** — this becomes the token block.
4. **Name the direction in two words** and put it in the brief.

Adjectives ("modern", "clean", "sleek") produce defaults. Artifacts produce directions.
