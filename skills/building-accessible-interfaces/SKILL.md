---
name: building-accessible-interfaces
description: Use when building or auditing any web UI for accessibility — keyboard navigation, screen readers, focus management, ARIA, color contrast, form labels and error announcements, reduced motion, or touch target size. Triggers include "is this accessible", "WCAG", "a11y", "screen reader", "keyboard navigation", "focus trap", "contrast ratio", "aria-label", or building modals, menus, tabs, comboboxes, toasts, and custom controls that must work without a mouse.
---

# Building Accessible Interfaces

## Overview

Accessibility is not a pass applied at the end. Almost every accessibility defect is a structural decision — a `div` that should have been a `button`, a state communicated only in color, a modal that never moved focus — and structural decisions are expensive to reverse.

**Core principle:** Native semantic HTML is accessible by default. Every layer you add on top of it is a layer you now own the accessibility of.

Target: **WCAG 2.2 Level AA**.

## The Iron Law

```
NO CUSTOM CONTROL WHERE A NATIVE ELEMENT EXISTS
```

A `<div onclick>` needs a role, a tabindex, key handlers for Enter and Space, a focus style, and a disabled state. A `<button>` needs none of that — it arrives with all of it, correct on every platform and assistive technology, for free.

Wrote `<div onclick>`? Replace it with `<button>`. Do not add ARIA to make the div behave like a button — ARIA changes what assistive tech announces, never what the browser does.

## Checklist

1. **Semantics first** — correct elements, landmarks, heading order
2. **Keyboard** — everything operable, visible focus, logical order, no traps
3. **Names** — every control and image has an accessible name
4. **Contrast** — text 4.5:1, large text and UI boundaries 3:1
5. **Forms** — labels, error association, announcement
6. **Dynamic content** — live regions for anything that changes without navigation
7. **Motion and targets** — reduced-motion respected, targets ≥ 24px (44px recommended)
8. **Verify** — automated scan, then a keyboard walk, then a screen reader

## 1. Semantics

### Use the Right Element

| Need | Element | Never |
|---|---|---|
| Navigates to a URL | `<a href>` | `<button onclick=location…>` |
| Performs an action | `<button>` | `<div onclick>`, `<a href="#">` |
| Group of options, one choice | `<input type="radio">` | styled divs |
| Show/hide content | `<details><summary>` | div + JS toggle |
| Modal dialog | `<dialog>` | div with `position: fixed` |
| Selection from a list | `<select>` | custom listbox, unless genuinely required |
| Tabular data | `<table>` with `<th scope>` | grid of divs |
| Progress | `<progress>` | animated div |

The `<a>` vs `<button>` distinction is not cosmetic: links support open-in-new-tab, copy-link, and activate on Enter only; buttons activate on Enter *and* Space. Screen-reader users navigate by element type, so a "button" in the links list is genuinely misleading.

### Landmarks

Exactly one `<main>`. Wrap navigation in `<nav>`. Use `<header>`, `<footer>`, `<aside>`. Screen-reader users jump between landmarks constantly; a page of nested divs offers nothing to jump to.

```html
<a href="#main" class="skip-link">Skip to content</a>
<header>…</header>
<nav aria-label="Primary">…</nav>
<main id="main" tabindex="-1">…</main>
<footer>…</footer>
```

Multiple `<nav>` elements each need a distinguishing `aria-label` ("Primary", "Breadcrumb", "Pagination").

```css
.skip-link { position: absolute; left: -9999px; }
.skip-link:focus { left: var(--space-s); top: var(--space-s); z-index: 9999; }
```

### Headings

One `<h1>` per page. Never skip levels (`h2` → `h4` is a defect). Heading level communicates document structure — pick it for structure and set the size with CSS.

## 2. Keyboard

**Every interactive element must be reachable and operable by keyboard alone.** This is the highest-yield check in this document and it takes ninety seconds: unplug the mouse and Tab through the page.

| Key | Expected |
|---|---|
| `Tab` / `Shift+Tab` | Move between focusable elements in DOM order |
| `Enter` | Activate link or button |
| `Space` | Activate button, toggle checkbox, scroll page |
| `Esc` | Close modal, popover, menu; cancel the current interaction |
| `Arrows` | Move within a composite widget — radio group, tabs, menu, listbox |
| `Home` / `End` | First / last item in a composite widget |

**Roving tabindex** — a composite widget is *one* tab stop, with arrows moving inside it:

```js
// Only the active item is tabbable; arrows move the active item.
items.forEach((el, i) => el.tabIndex = i === active ? 0 : -1);
```

Tabs, menus, toolbars, and listboxes all use this. A tab list where every tab is a separate tab stop is incorrect.

### Focus Visibility

```css
:focus-visible {
  outline: 2px solid var(--focus, currentColor);
  outline-offset: 2px;
  border-radius: 2px;
}
:focus:not(:focus-visible) { outline: none; }  /* no ring on mouse click */
```

**Never `outline: none` without a replacement.** The focus indicator must have 3:1 contrast against adjacent colors and be at least 2px thick (WCAG 2.2 SC 2.4.11/2.4.13).

### Focus Management

Focus must move when context changes, and return when it closes.

```js
// Opening
lastFocused = document.activeElement;
dialog.showModal();                    // <dialog> traps focus natively
dialog.querySelector('h2').focus();    // or the first meaningful control

// Closing
dialog.close();
lastFocused?.focus();                  // MUST return focus
```

**Never trap focus outside a modal.** A trap that Esc cannot escape is WCAG 2.1.2, a Level A failure — it can leave a keyboard user stuck on the page permanently.

**Route changes in SPAs:** move focus to the new page's `<h1>` or `<main tabindex="-1">` and announce the new title. Without this, a screen-reader user has no idea navigation occurred.

**Never move focus unprompted.** Auto-focusing a field mid-typing, or jumping focus on a background update, disorients everyone.

## 3. Accessible Names

Every control needs a name. Check this in devtools' Accessibility pane — the computed name, not the markup you intended.

```html
<!-- Visible label — best -->
<label for="q">Search</label><input id="q">

<!-- Icon-only button -->
<button aria-label="Close dialog"><svg aria-hidden="true">…</svg></button>

<!-- Label a region by an existing heading -->
<section aria-labelledby="h-recent"><h2 id="h-recent">Recent</h2>…</section>
```

**Rules:**
- Decorative images: `alt=""`. Omitting `alt` entirely makes screen readers read the filename.
- Informative images: `alt` describes the information, not the picture. A chart's alt is its finding.
- Icons inside a labelled control: `aria-hidden="true"` so the name is not doubled.
- Link text must make sense out of context. "Read more" ×8 on a page is useless; screen-reader users list links.
- `aria-label` **overrides** visible text. If a button reads "Save" but has `aria-label="Submit"`, voice-control users saying "click Save" fail. Keep them matching.

## 4. Contrast

| Content | Ratio |
|---|---|
| Body text | 4.5:1 |
| Text ≥ 24px, or ≥ 18.66px bold | 3:1 |
| Icons and UI boundaries that carry meaning | 3:1 |
| Focus indicator vs. adjacent colors | 3:1 |

Measure, do not estimate. See `designing-frontend-interfaces/references/color-and-theme.md` for the formula, and `applying-themes/scripts/check_contrast.py` for a runnable checker.

**Color is never the only signal.** Add an icon, a label, a pattern, or a shape wherever color conveys state — see the table in that same reference.

## 5. Forms

```html
<div class="field">
  <label for="email">Email address</label>
  <p id="email-hint" class="hint">We'll only use this to send your receipt.</p>
  <input id="email" type="email" inputmode="email" autocomplete="email"
         aria-describedby="email-hint email-err" aria-invalid="true" required>
  <p id="email-err" class="error">Enter an email address with an @.</p>
</div>
```

| Rule | Why |
|---|---|
| Every input has a `<label for>` | Placeholders are not labels — they vanish on focus and fail contrast |
| Errors linked via `aria-describedby` | Otherwise the error is invisible to screen readers |
| `aria-invalid="true"` on invalid fields | Announces the state, not just the message |
| Hints and errors both in `aria-describedby` | Space-separated ID list; both get announced |
| Never `disabled` on a submit as validation | Disabled elements are skipped by Tab and give no reason |
| Group related inputs in `<fieldset><legend>` | Radio groups and checkbox sets need the group name announced |
| `required` attribute, not just a red asterisk | Announced natively |

On submit failure: move focus to the first invalid field, or to a summary that links to each error.

## 6. Live Regions

Anything that changes without a page navigation must be announced.

```html
<div aria-live="polite" aria-atomic="true" class="sr-only" id="status"></div>
<div role="alert" id="errors"></div>   <!-- implicitly assertive -->
```

| Region | Use for | Interrupts? |
|---|---|---|
| `aria-live="polite"` | Status, results count, save confirmations | No — waits for a pause |
| `role="alert"` / `assertive` | Errors, session expiry, destructive warnings | Yes |

**Critical:** the live region element must exist in the DOM **before** the content changes. Injecting an element that already contains text announces nothing.

```js
// ✅ Region already present; only its text changes
status.textContent = `${n} results`;

// ❌ Injecting a populated live region — silent
container.innerHTML = '<div aria-live="polite">12 results</div>';
```

Use sparingly. Three live regions competing produce unusable chatter.

```css
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0;
  margin: -1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap;
}
```

Note `.sr-only` content is still *focusable* if it contains controls — use `.sr-only:focus-within` styles to reveal skip links.

## 7. Motion and Targets

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important; animation-iteration-count: 1 !important;
    transition-duration: .01ms !important; scroll-behavior: auto !important;
  }
}
```

- Nothing may flash more than **3 times per second** (seizure risk, WCAG 2.3.1).
- Auto-playing motion over 5 seconds needs a pause control (WCAG 2.2.2).
- Carousels need pause, and must not auto-advance while focused.

**Target size (WCAG 2.2 SC 2.5.8, AA):** 24×24 CSS px minimum. **44×44 is the practical recommendation.** Enlarge the hit area without changing the visual size:

```css
.icon-btn { position: relative; }
.icon-btn::after { content:""; position:absolute; inset:-10px; }
```

## 8. The Five Rules of ARIA

1. **Use a native element instead** if one exists with the semantics you need.
2. **Do not change native semantics** — `<button role="heading">` is wrong; wrap instead.
3. **All interactive ARIA must be keyboard-operable** — a `role="button"` div needs `tabindex="0"` and Enter/Space handlers.
4. **Never `role="presentation"` or `aria-hidden="true"` on a focusable element** — it becomes focusable but unannounced, which is the worst possible state.
5. **Every interactive element needs an accessible name.**

**No ARIA is better than bad ARIA.** Incorrect ARIA actively misinforms; missing ARIA merely falls back to the native behavior.

## Component Patterns

### Dialog

```html
<dialog id="confirm" aria-labelledby="confirm-title">
  <h2 id="confirm-title">Delete 47 records?</h2>
  <p>Records in Q3 Archive will be permanently removed.</p>
  <button data-close>Keep records</button>
  <button data-confirm class="danger">Delete 47 records</button>
</dialog>
```

`dialog.showModal()` provides focus trapping, Esc-to-close, inert background, and the `::backdrop` pseudo-element natively. Still required of you: focus something meaningful on open, and restore focus on close.

### Disclosure

```html
<button aria-expanded="false" aria-controls="panel-1">Shipping details</button>
<div id="panel-1" hidden>…</div>
```

Toggle both `aria-expanded` and `hidden`. Or use `<details><summary>` and write no JavaScript at all.

### Tabs

```html
<div role="tablist" aria-label="Account settings">
  <button role="tab" aria-selected="true"  aria-controls="p1" id="t1" tabindex="0">Profile</button>
  <button role="tab" aria-selected="false" aria-controls="p2" id="t2" tabindex="-1">Billing</button>
</div>
<div role="tabpanel" id="p1" aria-labelledby="t1" tabindex="0">…</div>
<div role="tabpanel" id="p2" aria-labelledby="t2" tabindex="0" hidden>…</div>
```

Roving tabindex; arrows move between tabs; Home/End jump to first/last.

### Toast

```html
<div aria-live="polite" id="toasts"></div>   <!-- present at page load -->
```

Errors use `role="alert"`. Never auto-dismiss anything the user must act on — WCAG 2.2.1 requires that time limits be adjustable.

### Combobox

The hardest common pattern. Use a maintained library (React Aria, Radix, Headless UI) rather than hand-rolling it. If hand-rolling: `role="combobox"` with `aria-expanded`, `aria-controls`, and `aria-activedescendant` pointing at the highlighted option's id — focus stays in the input while arrows move the highlight.

## Verification

Automated tools catch roughly 30-40% of issues. All three passes are required.

**1. Automated scan**

```bash
npx @axe-core/cli http://localhost:5173 --exit
npx lighthouse http://localhost:5173 --only-categories=accessibility --view
```

Or in a Playwright test — see the `testing-webapps` skill:

```python
page.add_script_tag(url="https://cdn.jsdelivr.net/npm/axe-core@4/axe.min.js")
violations = page.evaluate("async () => (await axe.run()).violations")
assert not violations, [v["id"] for v in violations]
```

**2. Keyboard walk** — no mouse:

- [ ] Tab reaches every control, in an order matching the visual layout
- [ ] Focus is always visible — never lost, never invisible on any background
- [ ] Enter and Space activate what they should
- [ ] Esc closes every overlay
- [ ] Arrows work inside tabs, menus, and radio groups
- [ ] Opening a modal moves focus in; closing it returns focus to the trigger
- [ ] Nothing is reachable only by hover
- [ ] No focus trap outside a modal

**3. Screen reader** — 5 minutes with the real thing:

| Platform | Reader | Start / stop |
|---|---|---|
| macOS | VoiceOver | `Cmd+F5` |
| Windows | NVDA (free) | `Ctrl+Alt+N` |
| Linux | Orca | `Super+Alt+S` |

Navigate by heading (`H`), by landmark (`D`), and by form control (`F`). Every control should announce its name, its role, and its state.

## Common Mistakes

**`<div onclick>` instead of `<button>`.** The single most common defect. Not keyboard-operable, no role, no focus, no disabled state.

**`outline: none` with no replacement.** Removes the only signal keyboard users have about where they are.

**Placeholder as label.** Disappears on focus, fails contrast, breaks autofill, unreliable for screen readers.

**Focus never returns from a modal.** Focus lands back at `<body>`, forcing a full re-tab through the page.

**Live region injected with its content.** Announces nothing. The element must pre-exist.

**`aria-label` contradicting visible text.** Breaks voice control — the user says the word they can see, and nothing happens.

**Icon-only buttons with no name.** Announced as "button". Every icon button needs `aria-label`.

**Heading levels chosen for size.** `<h4>` picked because it looked right. Set the level for structure and the size in CSS.

**Contrast checked in light mode only.** Dark mode passing is a separate check.

**`aria-hidden="true"` on something focusable.** Reachable by Tab but announced as nothing. Use `inert` on hidden containers instead.
