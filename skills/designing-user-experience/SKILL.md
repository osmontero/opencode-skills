---
name: designing-user-experience
description: Use when designing how an interface behaves rather than how it looks — user flows, navigation and information architecture, forms and validation, loading/empty/error states, confirmation and undo for destructive actions, button and error message wording, feedback for slow operations, or mobile and touch behavior. Also use when a UI looks finished but breaks on bad input, slow networks, no data, or first use.
---

# Designing User Experience

## Overview

Visual design decides what an interface looks like when everything goes right. UX decides what happens the rest of the time — and the rest of the time is most of the time.

**Core principle:** Design the states, not the screens. A "screen" is one state of a component; shipping only that one is why generated UI looks finished and breaks on contact with real data.

**Companion skills:** `designing-frontend-interfaces` for visual craft, `building-accessible-interfaces` for access, `reviewing-interface-quality` to audit a finished UI.

## The Iron Law

```
NO COMPONENT IS DONE UNTIL ITS EMPTY, LOADING, ERROR, AND PARTIAL STATES EXIST
```

A list that only renders when it has items is not a list component — it is a demo. If the design has no answer for "what does a new user with no data see", the design is incomplete.

## Checklist

Create a task for each item:

1. **Map the flow** — entry point → steps → success, and every branch off it
2. **Fill the state matrix** — for every component that touches data
3. **Design the failure paths** — what breaks, what the user sees, how they recover
4. **Write the copy** — buttons, errors, empty states, confirmations
5. **Set the feedback budget** — what happens at 100ms, 1s, 10s
6. **Handle the destructive and irreversible** — confirm, undo, or both
7. **Check touch and small viewport** — targets, reach, keyboard-open behavior
8. **Walk the flow as a first-time user** — with no data, no permissions, on a slow connection

## Step 1: Map the Flow

Before designing screens, write the flow as text. It takes two minutes and exposes gaps no mockup will.

```
GOAL: Reviewer approves a pending expense

Entry:    Email link → deep link into the item (may not be authenticated)
Step 1:   Authenticate                → already logged in? skip
Step 2:   View item + receipt
Step 3:   Approve | Reject | Request info
Success:  Confirmation + next pending item queued
Exit:     No items left → done state, not an empty table

Branches:
  Not authorized for this item     → explain who is, offer to forward
  Item already actioned by someone → show who and when, no error framing
  Receipt fails to load            → approve still possible, receipt shows retry
  Offline mid-approve              → queue and retry, tell them it is queued
```

**The branches are the design work.** Any flow whose branch list is empty has not been thought about yet.

**Reduce steps before styling them.** Each step is a chance to abandon. Ask of every one: can this be defaulted, inferred, deferred to later, or removed? A form field that can be derived should not be asked.

## Step 2: The State Matrix

Every component that displays data or accepts input has these states. Enumerate them explicitly; do not discover them in production.

| State | Trigger | Requirement |
|---|---|---|
| **Empty — first use** | New user, nothing created yet | Explain the feature and give the primary action. Never "No data." |
| **Empty — no results** | Filter or search matched nothing | Echo the query, offer to clear filters. Different from first-use empty. |
| **Empty — cleared** | User completed everything | Acknowledge it. This is a success state, not an absence. |
| **Loading — first** | No cached data | Skeleton matching real layout, delayed ~200ms |
| **Loading — refresh** | Data exists, updating | Keep old data visible, subtle indicator. Never blank the screen. |
| **Partial** | Some sources failed | Show what loaded, mark what did not, offer retry for that part |
| **Error — recoverable** | Timeout, 5xx, network | What happened, what to do, a retry control |
| **Error — permanent** | 404, deleted, revoked | Say it plainly, offer the nearest useful destination |
| **Error — permission** | 403 | Who does have access, how to request it |
| **Offline** | Connection lost | What still works, what is queued |
| **Too much** | 10,000 rows | Pagination or virtualization, plus a count |
| **Stale** | Cache older than threshold | Timestamp and a refresh control |
| **Success** | Action completed | Confirm it, and say what changed |

**The four empty states are genuinely different.** Collapsing them into one "No items found" is the most common UX shortcut in generated interfaces.

```
First use:   "No expenses yet — add your first to start tracking."     [Add expense]
No results:  "No expenses match 'q3 travel'."                          [Clear filters]
Cleared:     "All caught up. Nothing needs review."
Error:       "Couldn't load expenses. Check your connection."          [Retry]
```

## Step 3: Forms

Forms are where most UX failures live because they are where users actually type.

### Structure

- **One column.** Multi-column forms cause skipped fields and are ambiguous with keyboard order. Exceptions: genuinely paired fields (city/state, expiry/CVC).
- **Labels above inputs**, always visible. Placeholder-as-label disappears on focus, fails at low contrast, and breaks autofill and screen readers.
- **Group related fields** with real spacing (see the proximity rule in `designing-frontend-interfaces`).
- **Mark whichever is rarer** — if most fields are required, mark the optional ones instead. Never mark nothing.
- **Show requirements before typing**, not as an error afterwards. "8+ characters, one number" belongs under the field from the start.

### Validation Timing

| When | Do |
|---|---|
| While typing, field never blurred | Nothing. Validating on keystroke 3 of an email is hostile. |
| On blur, field non-empty | Validate this field |
| While typing, **after** an error was shown | Re-validate live so the error clears as they fix it |
| On submit | Validate all, focus the first invalid field, summarize at top if more than 2 |
| Server rejects | Map errors back to specific fields; never only a banner |

Errors appear **next to the field**, not only in a summary. A summary at the top is an addition for long forms, never a replacement.

### Input Types

Getting these right is most of mobile form UX — the correct keyboard appears automatically.

```html
<input type="email"    inputmode="email"    autocomplete="email">
<input type="tel"      inputmode="tel"      autocomplete="tel">
<input type="text"     inputmode="numeric"  autocomplete="one-time-code" pattern="[0-9]*">
<input type="password" autocomplete="current-password">
<input type="password" autocomplete="new-password">
<input type="text"     autocomplete="street-address">
```

Use `inputmode="numeric"` rather than `type="number"` for codes, PINs, and card numbers — `type="number"` adds spinners, allows `e` and `-`, and silently drops leading zeros.

**Never block paste.** Blocking paste on password or confirmation fields breaks password managers and helps no one.

### Data Handling

- **Never clear the form on error.** Losing typed data is the single most infuriating form behavior.
- **Preserve input across navigation** where the form is long — sessionStorage or server draft.
- **Be liberal in what you accept.** Strip spaces from card numbers and phone numbers rather than rejecting them. Accept `+1 (555) 123-4567` and normalize it yourself.
- **Disable submit only while submitting**, never as a validation gate. A permanently disabled button with no explanation gives the user nothing to act on.

## Step 4: Copy

Interface copy is UX, not decoration. It is often the entire difference between a usable and an unusable state.

### Buttons

Name the action, not the abstraction.

| Weak | Strong |
|---|---|
| Submit | Send invitation |
| OK | Delete 3 files |
| Yes / No | Discard changes / Keep editing |
| Continue | Review order |

A confirmation dialog's buttons must be readable **without** the dialog text. "OK" and "Cancel" on a delete confirmation force the user to re-read the prompt to know which is destructive.

### Errors

Three parts: what happened, why, what to do. Never expose a stack trace or a raw status code to a user.

| Bad | Good |
|---|---|
| "Error: invalid input" | "Enter a date after today — this event has already passed." |
| "Something went wrong" | "Couldn't save. Your connection dropped — we kept your changes. [Retry]" |
| "Error 403" | "You don't have access to this project. Ask its owner, Dana Reyes, for access." |
| "Invalid email" | "Emails need an @ — did you mean dana@example.com?" |

Never blame the user. "You entered an invalid date" → "That date has already passed."

### Voice

- Second person, active voice, present tense.
- Short. Cut every sentence that does not change what the user does.
- No exclamation marks in error states.
- No jargon the user did not introduce — "authentication token expired" → "you've been signed out."
- Sentence case for buttons and headings; Title Case reads as shouting in UI.

## Step 5: Feedback and Latency

Every user action needs acknowledgment within 100ms, even if the result takes longer.

| Elapsed | Requirement |
|---|---|
| 0-100ms | Feels instant. Show nothing extra. A flashing spinner is worse than none. |
| 100ms-1s | Immediate local feedback — button enters a pressed/busy state |
| 1-10s | Skeleton or determinate progress. Keep the layout stable. |
| 10s+ | Real progress, an estimate, and a cancel control |

**Optimistic updates** for actions that nearly always succeed (like, star, reorder): apply the change immediately, reconcile on response, and revert with a clear message on failure. Do not use them for anything with financial or destructive consequences.

**Never move content under a pointer.** Content that shifts after load causes mis-clicks. Reserve space for anything that will arrive: images with `width`/`height`, ad slots, async badges.

## Step 6: Destructive and Irreversible Actions

**Prefer undo over confirm.** A confirmation dialog interrupts every user to protect against a rare mistake; undo protects against the mistake without interrupting anyone.

```
Do:      [Delete]  →  item removed  →  toast: "Message deleted. [Undo]"  (8-10s)
Instead of:  [Delete]  →  "Are you sure?"  →  [Yes] [No]
```

**Confirm when undo is genuinely impossible** — sending an email, charging a card, permanently destroying data, anything affecting other people.

A real confirmation dialog:
- States the **specific** consequence with the count and name: "Delete 47 records from *Q3 Archive*? This cannot be undone."
- Labels the buttons with the actions, never Yes/No.
- Puts the destructive action in a destructive color **and** distinct wording.
- Requires typing the resource name only when the action is catastrophic and irreversible. Reserve that friction; overusing it trains users to type past it.
- Focuses the **safe** option by default.

Never use `window.confirm()` in production UI — it is unstyleable, blocks the main thread, and reads poorly to screen readers.

## Step 7: Navigation and Information Architecture

- **The user must always know where they are.** Current section indicated in nav; page title matching the destination they clicked.
- **Breadcrumbs for hierarchies deeper than two levels.**
- **Back must work.** Modals, filters, tabs, and steps should be URL-addressable so back and refresh behave. A filtered view that resets on refresh is broken.
- **Deep links must survive auth.** Land on a login, then return to the originally requested resource — not the dashboard.
- **Flat beats deep.** Seven items at one level are easier than three levels of three. Add a level only when a category genuinely has its own landing content.
- **Search is a feature, not a fallback.** If the answer to "how do users find X" is "search", the IA needs work — but ship search anyway.

## Step 8: Touch and Small Viewports

| Rule | Value |
|---|---|
| Minimum touch target | 44×44 CSS px (WCAG 2.2 SC 2.5.8) |
| Spacing between targets | 8px minimum |
| Primary actions | Bottom half of the screen — thumb reach |
| Destructive actions | Away from primary actions, never adjacent |
| Hover-only affordances | Forbidden. Touch has no hover. |
| Fixed bottom bars | Account for the on-screen keyboard and safe areas |

```css
.bottom-bar { padding-bottom: max(var(--space-s), env(safe-area-inset-bottom)); }
body { min-height: 100dvh; }  /* not 100vh — browser chrome makes it overflow */
```

Every gesture needs a visible equivalent. Swipe-to-delete is fine as an accelerator; it cannot be the only way to delete.

## Self-Review

- [ ] Every data component has all four empty states distinguished
- [ ] Loading never blanks already-visible content
- [ ] Every error says what to do next, and has a control to do it
- [ ] No error text exposes a status code or stack trace
- [ ] Forms never clear on error
- [ ] Validation fires on blur, not on keystroke
- [ ] Every input has the right `type`, `inputmode`, and `autocomplete`
- [ ] Button labels name their action and are readable out of context
- [ ] Destructive actions have undo, or a confirmation naming the specific consequence
- [ ] Filters, tabs, and modals are reflected in the URL
- [ ] Touch targets ≥ 44px, primary actions in thumb reach
- [ ] Nothing is reachable by hover alone
- [ ] Walked the whole flow with no data, no permission, and a throttled connection

## Common Mistakes

**The happy path is the only path.** Everything renders beautifully with three seeded items and collapses with zero or ten thousand.

**"No data" as an empty state.** It tells the user nothing and offers no action. Empty states are the highest-leverage onboarding surface in the product.

**Spinner replacing the whole page on refresh.** The user had content; now they have nothing. Keep it and indicate the update.

**Disabled submit with no explanation.** The user cannot tell what is missing. Enable it and validate on click, or state what is incomplete.

**Confirmation dialogs everywhere.** Confirming everything trains users to dismiss without reading, which is worse than no confirmation. Undo where possible.

**Error toasts that auto-dismiss.** A 4-second toast carrying the only description of a failure is a message the user will miss. Errors persist until dismissed; only successes auto-dismiss.

**Modal-in-modal.** Almost always a sign the flow needs a page, not a layer.

**Icon-only buttons without labels.** Recognizable icons are a short list: close, search, menu, plus. Everything else needs a visible label or, at minimum, a tooltip plus an accessible name.
