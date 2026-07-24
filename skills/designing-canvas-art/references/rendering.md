# Rendering the Canvas

The philosophy decides what to make. This decides how to actually produce the file.

## Choosing the Renderer

| Renderer | Best for | Weakness |
|---|---|---|
| **SVG → `cairosvg`** | Anything geometric, typographic, or pattern-based. **The default.** | Raster effects need a second pass |
| **`reportlab`** | Multi-page PDFs, precise print units, embedded fonts | Verbose; awkward for organic shapes |
| **PIL / Pillow** | Grain, noise, blur, blend modes, photographic texture | No vector output; type is mediocre |
| **`matplotlib`** | Data-derived marks, scientific-diagram languages | Fights you on anything non-chart |
| **HTML + Playwright** | Reusing CSS layout skills, web fonts, gradients | Needs a browser; PDF sizing is fiddly |

**Compose them.** The strongest results usually come from SVG for structure and geometry, rasterized once, then PIL for grain and tonal finishing.

```bash
source ~/.local/opencode-venv/bin/activate
python3 -c "import cairosvg, PIL, reportlab; print('ok')"
```

## Canvas Geometry

Work in points (1pt = 1/72in) for print, or pixels at a declared DPI.

| Format | Points (w × h) | Pixels @ 300 DPI |
|---|---|---|
| A4 portrait | 595 × 842 | 2480 × 3508 |
| A3 portrait | 842 × 1191 | 3508 × 4961 |
| US Letter | 612 × 792 | 2550 × 3300 |
| Square | 800 × 800 | 3333 × 3333 |
| ISO A-series poster (A2) | 1191 × 1684 | 4961 × 7016 |

**Export PNG at 300 DPI minimum** for anything that could be printed. 150 DPI is acceptable for screen-only. Below that, hairlines and small type break down.

## The Margin Contract

Nothing may fall outside the safe area, and nothing may overlap. This is the most common failure in generated canvas work and it is entirely preventable.

```python
W, H = 595, 842
MARGIN = round(min(W, H) * 0.085)      # ~50pt on A4 — never below 6%
SAFE = (MARGIN, MARGIN, W - MARGIN, H - MARGIN)

def contains(box, safe=SAFE):
    """box = (x0, y0, x1, y1) — assert before drawing."""
    return safe[0] <= box[0] and safe[1] <= box[1] and box[2] <= safe[2] and box[3] <= safe[3]
```

Full-bleed elements are a deliberate exception — but *text* is never one. Compute every text block's bounding box and assert it before committing the draw.

**Baseline grid:** pick a unit (typically the body leading, 12-16pt) and place every element on a multiple of it. This is what makes composition read as considered rather than arranged.

```python
UNIT = 14
def snap(v): return round(v / UNIT) * UNIT
```

## Type

Load real faces from `canvas-fonts/` — the skill bundles ~40 open-licensed TTFs. Never rely on a system default; it will differ across machines and silently change the layout.

```python
from PIL import ImageFont
FONTS = "skills/designing-canvas-art/canvas-fonts"
display = ImageFont.truetype(f"{FONTS}/Gloock-Regular.ttf", 96)
label   = ImageFont.truetype(f"{FONTS}/GeistMono-Regular.ttf", 9)
```

For SVG, embed the face as base64 so the file renders identically anywhere:

```python
import base64, pathlib
b64 = base64.b64encode(pathlib.Path(f"{FONTS}/Gloock-Regular.ttf").read_bytes()).decode()
style = f"""<style>@font-face{{font-family:'Display';
  src:url(data:font/ttf;base64,{b64}) format('truetype');}}</style>"""
```

Measuring text before placing it — the only reliable way to honor the margin contract:

```python
box = draw.textbbox((x, y), text, font=display)   # (x0, y0, x1, y1)
assert contains(box), f"text escapes safe area: {box}"
```

**Typographic rules for canvas work:**

- One display face, one label face. A third is almost always a mistake.
- Labels are tiny (7-10pt) and widely tracked (`0.12em`+). They are texture, not reading matter.
- Display type may be enormous. Set it tight — negative tracking, leading below 1.0.
- Rotated text (`writing-mode` / `rotate`) in the margin is a reliable way to add structure without adding content.
- Total word count on the canvas: usually under 40. If it is over 100, this became a document.

## Systematic Mark-Making

The philosophy asks for "dense accumulation of marks... patient repetition." That means generated fields, not hand-placed shapes.

```python
import math, random
rng = random.Random(7)            # ALWAYS seed — the piece must be reproducible

# Field of marks whose density follows a function
for i in range(2400):
    x = rng.uniform(*(SAFE[0], SAFE[2]))
    y = rng.uniform(*(SAFE[1], SAFE[3]))
    t = (y - SAFE[1]) / (SAFE[3] - SAFE[1])          # 0..1 down the page
    if rng.random() > t ** 1.7:                       # density gradient
        continue
    r = 0.4 + 1.6 * t
    draw.ellipse((x - r, y - r, x + r, y + r), fill=INK)
```

Other systematic languages that reward sustained viewing:

- **Registration marks and rules** — crosshairs at corners, tick scales along an edge
- **Indexed grid** — every cell carrying a coordinate label in 7pt mono
- **Contour accumulation** — nested offset paths from a noise field
- **Moiré** — two rotated line grids at 2-4° producing emergent interference
- **Halftone** — dot radius modulated by an underlying gradient or image

Seed the RNG and record the seed in the philosophy `.md`. An unreproducible piece cannot be refined, and refinement is the entire second pass.

## Grain and Finishing

The single highest-value finishing pass. Applied at ~3-5% it makes digital output read as material.

```python
import numpy as np
from PIL import Image, ImageFilter

def add_grain(img: Image.Image, amount=0.035, blur=0.4) -> Image.Image:
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    noise = np.random.default_rng(7).normal(0, 255 * amount, a.shape[:2])[..., None]
    out = Image.fromarray(np.clip(a + noise, 0, 255).astype(np.uint8))
    return out.filter(ImageFilter.GaussianBlur(blur)) if blur else out
```

Other finishing moves, in order of value: a very slight vignette; a 1-2px chromatic offset on one channel at the edges; a paper-tone base (`#f6f2e9`) instead of pure white; overprint simulation via `ImageChops.multiply` on layered color fields.

## SVG → PNG/PDF

```python
import cairosvg
cairosvg.svg2png(bytestring=svg.encode(), write_to="piece.png",
                 output_width=2480, output_height=3508)   # A4 @ 300 DPI
cairosvg.svg2pdf(bytestring=svg.encode(), write_to="piece.pdf")
```

## Multi-Page PDF

```python
from PIL import Image
pages = [Image.open(p).convert("RGB") for p in ["p1.png", "p2.png", "p3.png"]]
pages[0].save("book.pdf", save_all=True, append_images=pages[1:],
              resolution=300.0)
```

## Verification — Mandatory

Generating the file is not finishing it. **Read the rendered PNG back and look at it.** Every defect the philosophy warns about — overlap, overflow, crowding — is visible in the render and invisible in the code.

```python
from PIL import Image
img = Image.open("piece.png")
print(img.size, img.mode)

# Coverage: how much of the canvas carries marks
import numpy as np
a = np.asarray(img.convert("L"))
print(f"ink coverage: {(a < 200).mean():.1%}")     # 8-35% is usually right

# Edge safety: no marks in the outer 5%
m = int(min(img.size) * 0.05)
edges = np.concatenate([a[:m].ravel(), a[-m:].ravel(), a[:, :m].ravel(), a[:, -m:].ravel()])
print("edge is clean:", (edges < 200).mean() < 0.001)
```

Then actually view the PNG. Check:

- [ ] No text touches or crosses the safe area
- [ ] No two elements overlap unintentionally
- [ ] Ink coverage in the 8-35% band — below reads empty, above reads muddy
- [ ] Type is legible at 100% and the composition holds as a thumbnail
- [ ] The palette is genuinely limited — count the distinct colors
- [ ] Marks vary; nothing repeats mechanically without modulation
- [ ] Grain is present but not visible as noise
- [ ] The output opens in a normal viewer without warnings

**Thumbnail test:** downscale to 200px wide and look again. A strong composition still reads. If it becomes an even gray field, the value structure has no hierarchy.

## Common Mistakes

**Text placed without measuring.** Overflow and overlap are guaranteed. Measure the bbox and assert against the safe area.

**Unseeded randomness.** The second refinement pass cannot reproduce the first result, so refinement becomes regeneration.

**Pure white or pure black grounds.** Both read as digital default. Use a paper tone or a near-black with a hue.

**Effects stacked instead of composition refined.** The final step says explicitly: refine what is there, do not add. If the instinct is to call a new drawing function, that is the signal to stop.

**Too many colors.** Count them. Three to five, plus the ground, is the working range.

**Never viewing the output.** The most common failure. The code ran, so it must be right — it is not.
