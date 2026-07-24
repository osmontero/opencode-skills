# Motion

## The Principle

**One orchestrated moment beats twenty scattered micro-interactions.** A page load where elements arrive in a considered sequence reads as designed. The same page with a hover transition on every element and a fade on every section reads as noisy.

Budget: one signature moment per view, plus functional feedback on interactive elements. That is the whole allowance.

## Duration and Easing

| Interaction | Duration | Easing |
|---|---|---|
| Hover, focus, color change | 80-140ms | `ease-out` |
| Button press | 60-100ms | `ease-out` |
| Toggle, checkbox, small state | 140-200ms | `ease-out` |
| Dropdown, tooltip, popover | 160-220ms | `ease-out` |
| Modal, drawer, sheet | 240-320ms | custom ease-out |
| Page/route transition | 300-450ms | custom ease-out |
| Ambient / decorative loop | 2000ms+ | `ease-in-out`, infinite |

Under 80ms reads as instant — the animation is wasted work. Over 500ms for anything the user triggered feels broken; they are waiting on your animation.

```css
--ease-out:  cubic-bezier(0.16, 1, 0.3, 1);    /* decisive arrival — the default */
--ease-in:   cubic-bezier(0.7, 0, 0.84, 0);    /* exits only */
--ease-both: cubic-bezier(0.87, 0, 0.13, 1);   /* symmetric moves */
--ease-back: cubic-bezier(0.34, 1.56, 0.64, 1); /* playful overshoot — use sparingly */
```

**Entrances ease out, exits ease in.** Things arriving should decelerate into place; things leaving should accelerate away. `ease-in-out` on an entrance makes it feel sluggish at the start.

**Exits are faster than entrances** — roughly 70% of the entrance duration. Users have already decided; do not make them wait for the dismissal.

## Animate Only Compositor Properties

```
✅ transform   opacity   filter   clip-path(sometimes)
❌ width  height  top  left  margin  padding  font-size  box-shadow
```

Layout properties trigger reflow on every frame and drop the animation below 60fps on mid-range hardware. Almost every layout animation has a transform equivalent:

| Instead of | Use |
|---|---|
| `left: 0 → 100px` | `transform: translateX(100px)` |
| `width: 0 → 100%` | `transform: scaleX(0 → 1)` with `transform-origin: left` |
| `height: auto` reveal | `grid-template-rows: 0fr → 1fr` (animatable, no JS measurement) |
| `box-shadow` on hover | Animate `opacity` of a pseudo-element carrying the shadow |

**Animating to `height: auto`:**

```css
.disclosure { display: grid; grid-template-rows: 0fr; transition: grid-template-rows var(--dur) var(--ease-out); }
.disclosure[open] { grid-template-rows: 1fr; }
.disclosure > div { overflow: hidden; }
```

## Orchestration

Staggered arrival is what makes a page load feel authored. Increments of 40-80ms; total sequence under 600ms.

```css
@keyframes rise { from { opacity: 0; transform: translateY(12px) } }

.reveal > * {
  animation: rise 500ms var(--ease-out) backwards;
  animation-delay: calc(var(--i, 0) * 60ms);
}
```

```html
<div class="reveal">
  <h1 style="--i:0">…</h1>
  <p  style="--i:1">…</p>
  <a  style="--i:2">…</a>
</div>
```

`backwards` fill mode is required — without it, elements flash at full opacity before their delay elapses.

**Scroll-triggered, no JavaScript:**

```css
@media (prefers-reduced-motion: no-preference) {
  .on-scroll {
    animation: rise linear both;
    animation-timeline: view();
    animation-range: entry 10% cover 35%;
  }
}
```

Where `animation-timeline` is unsupported, this degrades to the element simply being visible — acceptable. If a JS fallback is needed, use `IntersectionObserver` and add a class; never animate on `scroll` events.

## Reduced Motion

**Mandatory.** Vestibular disorders make large-scale motion genuinely nauseating.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

The blanket reset is the safe floor. Better, where you have the budget: keep opacity fades (which do not trigger vestibular response) and remove only movement, parallax, scale, and rotation.

```css
@media (prefers-reduced-motion: reduce) {
  .reveal > * { animation: fade-only 200ms both; }  /* opacity only, no translate */
  .parallax   { transform: none !important; }
}
```

Never gate essential information behind an animation that reduced-motion users will not see.

## View Transitions

For route and state changes, the View Transition API replaces a great deal of custom animation code:

```js
document.startViewTransition(() => updateTheDOM());
```

```css
::view-transition-old(root) { animation: fade-out 180ms var(--ease-in);  }
::view-transition-new(root) { animation: fade-in  280ms var(--ease-out); }

/* Element morphs between states when it carries the same name */
.hero-image { view-transition-name: hero; }
```

Feature-detect: `if (!document.startViewTransition) { updateTheDOM(); return; }`

## Motion in React

When Motion (formerly Framer Motion) is available:

```jsx
<motion.div
  initial={{ opacity: 0, y: 12 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -8 }}
  transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
/>
```

Springs for anything the user drags or that should feel physical:

```jsx
transition={{ type: "spring", stiffness: 320, damping: 30, mass: 0.9 }}
```

Higher `stiffness` = faster. Higher `damping` = less bounce. `damping` below ~20 oscillates visibly, which is rarely what an interface wants.

Respect the preference:

```jsx
const reduce = useReducedMotion();
<motion.div animate={reduce ? { opacity: 1 } : { opacity: 1, y: 0 }} />
```

**Do not reach for a library** for hover states, color transitions, or simple reveals. CSS handles those with zero bundle cost.

## Loading and Latency

Motion's most valuable job is making waiting tolerable.

| Wait | Treatment |
|---|---|
| Under 100ms | Nothing. A spinner that flashes is worse than no spinner. |
| 100ms - 1s | Inline indicator on the triggering control; keep layout stable |
| 1s - 10s | Skeleton matching the real content's shape, or a determinate bar |
| Over 10s | Progress with a real estimate, plus a cancel affordance |

**Skeletons must match the real layout.** A skeleton whose shape differs from the loaded content causes a jarring snap — worse than a spinner. And delay the skeleton by ~200ms so fast responses never flash it.

```css
@keyframes shimmer { to { background-position-x: -200% } }
.skeleton {
  background: linear-gradient(90deg, var(--surface-2) 25%, var(--surface) 37%, var(--surface-2) 63%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
@media (prefers-reduced-motion: reduce) { .skeleton { animation: none } }
```

## Common Mistakes

**Everything animates.** Transitions on every hover, fades on every section. The signal disappears into the noise.

**`transition: all`.** Animates properties you never intended, including layout ones, and silently costs performance. Name the properties.

**Animating layout properties.** `width`, `height`, `top`, `left` reflow every frame. Use transforms.

**No `prefers-reduced-motion` block.** An accessibility failure, not a polish item.

**Entrance easing on exits.** `ease-out` on a dismissal makes it linger.

**Spinner for a 60ms request.** It flashes. Show nothing under 100ms.

**Animation as the only feedback.** If a spinner is the sole indication that a submit succeeded, screen-reader users get nothing. Pair it with a live region — see `building-accessible-interfaces`.
