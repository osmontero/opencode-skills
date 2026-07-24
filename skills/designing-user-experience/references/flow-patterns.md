# Flow Patterns

Worked designs for the flows that appear in most products. Each lists the states that are routinely forgotten.

---

## Onboarding / First Run

**Goal:** get to first value, not through a tour.

```
Entry → minimum viable account → seed or import data → first meaningful action → done
```

| Rule | Detail |
|---|---|
| Defer everything deferrable | Ask for a workspace name later; ask for a team later. Email + password is enough to start. |
| Seed the empty state | Sample data, a template, or an import path. A new account landing on twelve empty tables is abandonment. |
| Progress must be visible | "Step 2 of 3", and the count must not change midway. |
| Every step skippable, or none are | A "Skip" that appears on step 4 but not steps 1-3 reads as a trick. |
| Never block on optional data | Avatar, bio, and preferences belong in settings. |

**Forgotten states:** returning mid-onboarding (resume where they left off), invited user joining an existing workspace (skip creation entirely), email verification pending (what can they do meanwhile?).

---

## Authentication

```
Entry (may be a deep link) → sign in → return to originally requested resource
```

| Rule | Detail |
|---|---|
| Preserve the destination | Deep link → login → the deep link. Never the dashboard. |
| One field per step is fine | Email first, then password, enables SSO routing by domain. |
| `autocomplete` correctly | `current-password` on sign-in, `new-password` on register/reset. Wrong values break password managers. |
| Never block paste | Breaks password managers and 2FA codes. |
| Generic failure message | "Email or password is incorrect" — naming which one is an account-enumeration leak. |
| Rate-limit messaging | "Too many attempts. Try again in 5 minutes." with a real countdown. |

**Forgotten states:** session expired mid-action (preserve the in-flight work), already signed in but hitting `/login` (redirect, do not show the form), 2FA device lost (a recovery path must exist), account locked, password reset link expired.

---

## Search and Filter

```
Entry → query → results → refine → act on a result
```

| Rule | Detail |
|---|---|
| State lives in the URL | Query, filters, sort, and page. Sharing and refreshing must work. |
| Debounce 200-300ms | Not per keystroke, not on submit only. |
| Never blank results while typing | Keep prior results dimmed with a subtle busy indicator. |
| Show the query in the empty state | "No results for 'q3 travel'" — plus a clear-filters control. |
| Show the active filter count | Especially when filters are behind a collapsed panel. |
| Result count always | "1-20 of 347". Users need to know if refining is worthwhile. |

**Forgotten states:** query too short, query too broad (offer to narrow), a filter combination that can never match (say so rather than showing empty), a slow search that resolves after the user has typed more (discard stale responses).

---

## Multi-Step Forms and Wizards

| Rule | Detail |
|---|---|
| Show total steps upfront, never change it | A "Step 3 of 4" that becomes "Step 3 of 7" destroys trust. |
| Back must not lose data | Every step's data persists in both directions. |
| Validate per step, not only at the end | Discovering a step-1 error on step 5 is a rewrite. |
| Review before submit | For anything consequential, a final summary with edit links per section. |
| Save drafts | Long forms must survive a closed tab. |

**Forgotten states:** browser back button (must map to the previous step, not out of the flow), refresh mid-flow, a step that becomes irrelevant based on an earlier answer (renumber consistently or use non-numeric labels).

---

## Data Tables

The single richest state surface in most applications.

| Rule | Detail |
|---|---|
| Sort and filter state in the URL | Same as search. |
| Sticky header past ~15 rows | Column meaning is lost without it. |
| Right-align numerals, `tabular-nums` | Non-tabular figures jitter when values update. |
| Row actions always visible on touch | Hover-revealed actions do not exist on touch devices. |
| Bulk selection shows a count and a clear control | "12 selected · Clear" |
| Virtualize past ~200 rows | Or paginate. Rendering 10,000 DOM rows freezes the tab. |

**Forgotten states:** zero rows vs. zero *matching* rows, one row (does the layout still make sense?), a cell with a 400-character value, a column of all-null values, sort applied to a column with ties, a row deleted by another user while selected.

---

## Checkout / Payment

| Rule | Detail |
|---|---|
| Total visible at every step | Including tax and shipping as soon as they are known. |
| No surprise costs at the last step | The top reason for cart abandonment. |
| Guest checkout available | Forced account creation loses sales. |
| Card fields accept spaces | Strip them yourself. Rejecting `4242 4242 4242 4242` is hostile. |
| One submit, idempotent | Disable on submit *and* guard server-side against double-charge. |
| Failure preserves the cart | Never make the user rebuild an order after a declined card. |

**Forgotten states:** payment declined (which is recoverable — say why if known), payment pending/processing (do not let them retry into a double charge), an item going out of stock between cart and checkout, an expired promo code, a session timing out mid-payment.

---

## Notifications and Toasts

| Type | Duration | Dismissal |
|---|---|---|
| Success | 4-6s | Auto |
| Info | 6-8s | Auto |
| Warning | Persist | Manual |
| Error | Persist | Manual |
| Undo affordance | 8-10s | Auto, with a visible timer |

| Rule | Detail |
|---|---|
| Never stack more than 3 | Collapse the rest into "and 4 more". |
| Never cover the element that triggered them | Especially on mobile, where a bottom toast covers the button. |
| Pair with a live region | A visual-only toast does not exist for screen-reader users. |
| Errors are never toasts alone | If the user must act, put it inline where the action is. |

---

## Real-Time and Collaborative

**Forgotten states:** connection lost and reconnecting (say which), another user editing the same field, a record deleted while you are viewing it, your local change rejected by the server after an optimistic update, clock skew making timestamps read as the future, a tab left open overnight with stale data.

Every one of these needs a designed response. "It just breaks" is the default without one.

---

## Universal Forgotten States

Check these against any flow:

- The user has **no permission** for part of it
- The user's **session expires** mid-flow
- The network **drops** mid-request
- The response is **slow** (5s+), not failed
- The data volume is **10,000×** the demo
- A field contains an **emoji, RTL text, or a 500-character** value
- The user has the tab open in **two windows**
- The user hits **browser back** at every step
- The user arrives via a **deep link** without prior context
- The feature is used on a **390px** viewport with the keyboard open
