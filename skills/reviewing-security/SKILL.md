---
name: reviewing-security
description: Use when reviewing code for security before merging or shipping, and when a change touches untrusted input, authentication, authorization, secrets, SQL, subprocess execution, file paths, outbound requests, deserialization, uploads, or third-party dependencies. Triggers include "security review", "is this safe", "can this be exploited", "audit this for vulnerabilities", and adding any new external interface — an endpoint, a webhook, a plugin, or a tool an LLM can call.
---

# Reviewing Security

## Overview

Most security review output is worthless because it names categories instead of paths. "Validate all user input" is true of every program ever written and changes nothing. A useful finding is a *path*: an input an attacker controls, the code that carries it, the operation it reaches, and what the attacker gets.

**Core principle:** Follow the data, not a checklist. Vulnerabilities live in the gap between where a value enters and where it acts.

**Companion skills:** `requesting-code-review` for the general review loop, `systematic-debugging` when confirming an exploit path.

## The Iron Law

```
NO FINDING WITHOUT A PATH FROM ATTACKER-CONTROLLED INPUT TO IMPACT
```

If you cannot name the input, the route it takes, and what it costs the operator, you have a code smell — file it under Observations, not Findings. Padding a report with categorical advice buries the one path that is real.

**The corollary:** trace the path in the actual code before reporting it. A grep hit is a lead, not a finding.

## Checklist

1. **Map the attack surface** — entry points, who reaches them, what privilege they run with
2. **Trace inputs to sinks** — injection in all its forms
3. **Authorization** — the highest-yield pass
4. **Secrets and crypto**
5. **Process and plugin boundaries**
6. **Dependencies**
7. **Data exposure** — logs, errors, responses
8. **Run the scanners** — then verify reachability before reporting
9. **Report** — severity by exploitability, each with a path

## Step 1: Map the Attack Surface

Do this before reading implementation. You are building the list of places a stranger can reach.

| Entry point | Who can reach it | Privilege it runs with |
|---|---|---|
| HTTP route, gRPC method | anon / authed / admin / internal-only | process, DB role, filesystem |
| Queue or event consumer | whoever can publish | usually full process |
| File upload, import | any authed user | parser runs in-process |
| Webhook receiver | the internet, until signature is verified | |
| CLI flags, env, config | local operator | |
| **LLM / tool output** | **anyone who can influence the model's context** | whatever the tool can do |

```bash
# Enumerate handlers and consumers — adapt the pattern to the framework
grep -rnE '\.(Get|Post|Put|Patch|Delete|Handle|HandleFunc)\(' --include='*.go' --include='*.ts'
grep -rnE 'func \(.*\) [A-Z][A-Za-z]*\(ctx context.Context' --include='*.go'   # gRPC impls
```

That last row is not a novelty. **Model output is untrusted input.** If a document, a web page, or a prior tool result can steer the model into calling a tool, then every sink that tool reaches is attacker-reachable. Review tool definitions with the same suspicion as HTTP handlers.

## Step 2: Trace Inputs to Sinks

For each entry point, follow the value. A sink is any operation whose behavior changes if the value is hostile.

| Sink | What makes it dangerous | The safe form |
|---|---|---|
| SQL / query builder | string concatenation or interpolation | parameterized query; allowlist for identifiers, which cannot be parameterized |
| Shell / process spawn | a shell interpreter, or user data in argv[0] | exec with an argv array, no shell, fixed binary path |
| Filesystem path | `..`, absolute paths, symlinks, NUL | join, then `filepath.EvalSymlinks`, then verify the result is still under the root |
| Outbound HTTP | user-supplied URL → SSRF | allowlist hosts; block private, link-local, and metadata ranges; re-check after redirects |
| Template render | autoescape off, or `dangerouslySetInnerHTML` | escaped by default; sanitize HTML with a real sanitizer |
| Deserialization | polymorphic or type-carrying formats | fixed schema, decode into a concrete type, cap size and depth |
| Archive extraction | zip-slip, symlinks, decompression bombs | validate each entry path, cap total bytes and entry count |
| Redirect target | open redirect → phishing, token theft | allowlist paths, or same-origin only |
| Regex over user input | catastrophic backtracking | bound input length, avoid nested quantifiers |
| `eval` / reflection / dynamic import | arbitrary code | there is no safe form — remove it |

**Follow the value across boundaries.** The common miss is a value that is validated at the edge, stored, and then read back and trusted. Storage is not sanitization. If it is rendered or executed later, it is still tainted.

Concrete vulnerable/fixed pairs for each row: see [references/vulnerability-patterns.md](references/vulnerability-patterns.md).

## Step 3: Authorization

**This is where the real bugs are.** Injection is well-defended by modern libraries; broken object-level authorization is not, because it cannot be fixed by a framework — it requires knowing which rows belong to whom.

- [ ] Every handler taking an ID verifies the caller may access *that* object — not merely that they are logged in
- [ ] The check is on the path the data actually takes; a check in the route layer that the service layer can bypass is not a check
- [ ] Tenant/org scoping is in the query (`WHERE tenant_id = ?`), not applied to results after fetching
- [ ] No role, tenant, price, or user ID is trusted from the request body — mass assignment is authorization bypass with extra steps
- [ ] Default deny: a new route without an explicit policy is unreachable, not public
- [ ] State-changing operations are not reachable by `GET`
- [ ] Sequential IDs are not the only thing standing between a user and someone else's record
- [ ] Admin surfaces are gated by more than an unlinked URL
- [ ] Authorization is re-checked on each step of multi-step flows, not only at the start

```bash
# Handlers that take an identifier — each one needs an ownership check
grep -rnE 'Param\("id"\)|params\.id|req\.body\.(userId|tenantId|role)' --include='*.go' --include='*.ts'
```

## Step 4: Secrets and Crypto

- [ ] No secret in source, config committed to git, logs, error messages, URLs, or client-visible bundles
- [ ] No secret in git *history* — rotate anything ever committed; deleting it in a later commit fixes nothing
- [ ] Passwords hashed with argon2id/scrypt/bcrypt — never a bare SHA, never unsalted
- [ ] Tokens and signatures compared with a constant-time function
- [ ] Randomness for tokens, IDs, and salts comes from a CSPRNG (`crypto/rand`, `crypto.randomUUID`) — never `math/rand`
- [ ] JWTs: signature verified, algorithm pinned (reject `none` and algorithm confusion), `exp`/`aud`/`iss` checked
- [ ] TLS verification never disabled — no `InsecureSkipVerify: true`, no `NODE_TLS_REJECT_UNAUTHORIZED=0`
- [ ] Session tokens rotate on privilege change; logout invalidates server-side
- [ ] Cookies: `HttpOnly`, `Secure`, `SameSite` set deliberately
- [ ] No hand-rolled crypto primitives or custom "encryption"

```bash
gitleaks detect --no-banner          # or: trufflehog git file://.
git log -p -S'BEGIN PRIVATE KEY' --oneline | head
```

## Step 5: Process and Plugin Boundaries

For anything that spawns a subprocess, loads a plugin, or executes tools on behalf of a model:

- [ ] The child inherits only the environment it needs — not the full parent env with every credential in it
- [ ] Working directory, open file descriptors, and network access are deliberate, not inherited by default
- [ ] Child output is parsed as data, never re-entered as trusted instructions
- [ ] Resource limits exist: timeout, memory, output size. An unbounded child is a denial-of-service primitive
- [ ] Failure is closed — a crashed or unresponsive plugin denies the operation rather than skipping the check
- [ ] The tool surface itself is the security boundary: a tool that takes a path, a URL, or a command is that sink, exposed to whoever influences the model

## Step 6: Dependencies

- [ ] Lockfile committed and honored in the build (`npm ci`, `go mod verify`)
- [ ] Advisory scan clean, or each exception justified in writing with a reachability argument
- [ ] New direct dependencies: check age, maintenance, download counts, and name against typosquats
- [ ] Install/postinstall scripts reviewed for any new dependency
- [ ] CI actions pinned to a SHA, not a moving tag

```bash
govulncheck ./...          # Go — reports only vulnerabilities you actually reach
npm audit --omit=dev       # Node
pip-audit                  # Python
```

`govulncheck` is worth more than a generic scanner precisely because it does reachability analysis. Prefer tools that tell you whether the vulnerable function is called.

## Step 7: Data Exposure

- [ ] Errors returned to clients carry no stack traces, SQL, file paths, or internal hostnames
- [ ] Logs contain no passwords, tokens, session IDs, full card numbers, or PII beyond what is needed
- [ ] Debug endpoints (`/debug/pprof`, GraphQL introspection, admin consoles) are disabled or gated in production
- [ ] CORS: no `Access-Control-Allow-Origin: *` combined with credentials; the origin allowlist is explicit
- [ ] Authenticated responses are not cacheable by shared caches
- [ ] Object storage buckets and their listings are private by default
- [ ] Timing and error-message differences do not reveal whether an account exists

## Step 8: Run the Scanners, Then Verify

```bash
semgrep --config=auto .
```

Scanner output is a lead list, not a report. **Before reporting any scanner hit, confirm it is reachable in this codebase** — check whether the sink is actually called with a tainted value. Forwarding raw tool output is how a review becomes noise that gets ignored, taking the real findings with it.

## Severity

Grade by exploitability, not by category name.

| Severity | Definition |
|---|---|
| **Critical** | Unauthenticated attacker gains code execution, credentials, or bulk access to other users' data. No unusual preconditions. |
| **High** | Authenticated attacker escalates privilege, reads or writes another tenant's data, or extracts secrets. |
| **Medium** | Requires an unusual precondition (a specific race, a chained bug, a user action) or yields limited data. |
| **Low** | Hardening. Real weakness, no demonstrated path today — a missing defense-in-depth layer that would contain a future bug. |

Do not inflate. A report where everything is Critical is a report nobody acts on.

## Report Format

```markdown
## Scope
[What was reviewed — diff range, paths, or "full repo". What was NOT reviewed.]
[Scanners run and their versions.]

## Critical
**Tenant isolation missing on document fetch**
`internal/api/documents.go:88` — the handler loads by primary key only:
`db.First(&doc, c.Param("id"))`. There is no `tenant_id` predicate and no
post-fetch ownership check.
**Path:** any authenticated user → `GET /api/documents/{id}` → sequential
integer IDs → full document body of any tenant.
**Impact:** cross-tenant read of all documents; IDs are enumerable.
**Fix:** scope the query — `db.Where("tenant_id = ?", claims.TenantID).First(&doc, id)`
— and add the predicate at the repository layer so new callers inherit it.

## High
[same shape]

## Medium / Low
[same shape]

## Observations (not findings)
[Weaknesses with no demonstrated path. Say so plainly rather than promoting them.]

## Verified Clean
[What you checked and found sound. Silence reads as "not checked".]

## Assessment
**Ship?** Yes / No / After the Critical and High items
**Reasoning:** [1-2 sentences]
```

## What NOT to Report

| Do not report | Why |
|---|---|
| "Add input validation" with no sink | Categorical advice, not a finding |
| Missing rate limiting with no abusable endpoint named | Name the endpoint and the cost, or drop it |
| Missing browser security headers on a service with no browser client | Threat does not apply |
| Findings in tests, fixtures, or example code | Not attacker-reachable |
| Scanner output you did not confirm is reachable | Noise that buries real findings |
| Cryptographic preference nits with no threat | "Use AES-256 instead of AES-128" is not a finding |
| Anything you would describe as "theoretically" | If it were exploitable you would have the path |

## Common Mistakes

**Checklist review instead of path review.** Walking OWASP Top 10 top to bottom finds the vulnerabilities that are already handled by the framework and misses the authorization bug that is unique to this domain.

**Stopping at the entry point.** Validation at the edge tells you nothing if the value is stored and later concatenated into a query.

**Trusting the framework blindly.** ORMs have raw-query escape hatches, templates have raw-output escape hatches, and both get used. Grep for them specifically.

**Treating authenticated as authorized.** The single most common real-world finding, and the easiest to miss by reading the route table instead of the query.

**Reporting the model as trusted.** If a tool call can be influenced by content the model read, its arguments are attacker-controlled.

**Severity inflation to seem thorough.** It costs you the reader's attention on the finding that matters.
