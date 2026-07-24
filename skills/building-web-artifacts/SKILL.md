---
name: building-web-artifacts
description: Use when building elaborate, multi-component HTML artifacts using modern frontend technologies (React, Tailwind CSS, shadcn/ui). Triggers include requests for complex web artifacts requiring state management, routing, or shadcn/ui components. Not for simple single-file HTML/JSX artifacts — use direct generation for those.
license: Complete terms in LICENSE.txt
---
------

# Building Web Artifacts

To build powerful frontend opencode artifacts, follow these steps:
1. Initialize the frontend repo using `scripts/init-artifact.sh`
2. Develop your artifact by editing the generated code
3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
4. Save the artifact file and inform the user of its location
5. (Optional) Test the artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

**REQUIRED SUB-SKILL:** Use `designing-frontend-interfaces` before writing components. Write the design brief and lock the token block first — shadcn's defaults are a starting point, not a design, and shipping them unmodified produces exactly the generic output this section warns about.

Also required before shipping: `designing-user-experience` for state coverage, `building-accessible-interfaces` for keyboard and screen-reader support.

**The specific slop signature to avoid:** centered `max-w-4xl` for everything, purple/violet→blue gradients on white, uniform `rounded-lg` on every surface, `shadow-md` everywhere, Inter or `system-ui` as the display face, `text-gray-500` body copy, and the hero → three feature cards → CTA skeleton.

### Configure Tailwind, Don't Accept It

Tailwind's defaults are a palette of defaults — using them raw is how artifacts converge on the same look. Override them with the token block from your brief:

```js
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        base: "#f7f6f0", surface: "#fffffb", line: "#dcded1",
        ink: { DEFAULT: "#1a271a", 2: "#4a5a46", 3: "#79876f" },
        accent: { DEFAULT: "#2f6b3c", ink: "#f4fbf5" },
      },
      fontFamily: {
        display: ['"Young Serif"', "Georgia", "serif"],
        text: ['"Work Sans"', "system-ui", "sans-serif"],
      },
      borderRadius: { DEFAULT: "2px" },   // ONE radius
    },
  },
};
```

Now `bg-base`, `text-ink-2`, `border-line`, `font-display` carry the semantics, and the theme is swappable in one file. The `applying-themes` skill provides ten contrast-verified palettes ready to drop in here.

Also disable shadcn's default radius variable if you committed to a different one — `--radius` in `globals.css` silently applies to every component.

## Component and State Requirements

Every data-driven component in the artifact needs its full state set — see `designing-user-experience` for the matrix. In a self-contained artifact these are cheap to get wrong because there is usually no real backend to force them.

```tsx
if (error)          return <ErrorState onRetry={refetch} message={...} />;
if (loading)        return <Skeleton />;              // matching the real layout
if (!items.length)  return query ? <NoResults query={query} onClear={...} />
                                 : <FirstRun onCreate={...} />;
return <List items={items} />;
```

The two empty states are different and both are needed. `No data` for both is the most common shortcut in generated artifacts.

## Accessibility in Artifacts

shadcn/ui is built on Radix, so its primitives are accessible **as long as you use them as intended**. The defects come from what you add around them:

- Icon-only buttons need `aria-label` — Radix cannot infer one
- Custom `<div onClick>` handlers bypass everything Radix gives you; use `<Button>`
- `className` overrides that remove focus rings (`focus:outline-none` without a replacement ring) break keyboard navigation
- Charts and canvases need a text alternative — a caption stating the finding
- Verify contrast after theming; Radix does not check your colors

## Performance

Artifacts are single self-contained files, so bundle size is the whole load time.

- **Inline fonts as base64 woff2**, subset to the characters used. A full TTF can exceed the entire rest of the bundle.
- **No icon library imports.** `import { X } from "lucide-react"` can pull in the whole set depending on tree-shaking. Paste the individual SVGs.
- **Virtualize lists over ~200 rows.** Rendering thousands of DOM nodes freezes the tab.
- **`React.memo` on rows** inside large lists; keep the key stable.
- **No external requests.** Artifacts frequently run under a CSP that blocks CDNs, remote fonts, and `fetch`. Everything must be inlined.

## Verification

Before presenting the artifact, open `bundle.html` and check it:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1440,'height':900})
    errs=[]; pg.on('console', lambda m: m.type=='error' and errs.append(m.text))
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://$PWD/bundle.html'); pg.wait_for_timeout(1200)
    pg.screenshot(path='/tmp/artifact.png', full_page=True)
    pg.set_viewport_size({'width':390,'height':844})
    pg.screenshot(path='/tmp/artifact-mobile.png', full_page=True)
    print('CONSOLE ERRORS:', errs); b.close()"
```

Then read both screenshots. A bundle that builds successfully can still render blank — a missing inlined asset, a CSP violation, or a runtime error in a lazily-rendered branch all produce a clean build and an empty page.

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new React project:
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:
- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for bundling (via .parcelrc)
- ✅ Node 18+ compatibility (auto-detects and pins Vite version)

### Step 2: Develop Your Artifact

To build the artifact, edit the generated files. See **Common Development Tasks** below for guidance.

### Step 3: Bundle to Single HTML File

To bundle the React app into a single HTML artifact:
```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in the agent conversations as an artifact.

**Requirements**: Your project must have an `index.html` in the root directory.

**What the script does**:
- Installs bundling dependencies (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
- Creates `.parcelrc` config with path alias support
- Builds with Parcel (no source maps)
- Inlines all assets into single HTML using html-inline

### Step 4: Share Artifact with User

Finally, share the bundled HTML file in conversation with the user so they can view it as an artifact.

### Step 5: Testing/Visualizing the Artifact (Optional)

Note: This is a completely optional step. Only perform if necessary or requested.

To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components