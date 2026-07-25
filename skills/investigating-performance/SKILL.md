---
name: investigating-performance
description: Use when something is too slow, uses too much memory or CPU, degrades under load, or times out — and before making any change intended to speed something up. Triggers include "this is slow", "optimize this", "high latency", "p99", "memory leak", "it's fine locally but not in production", "the query takes forever", "reduce bundle size", and any request to make code faster.
---

# Investigating Performance

## Overview

Performance work fails in a specific way: the engineer reads the code, forms an intuition about what must be slow, optimizes that, and ships a change that measurably does nothing. The bottleneck is somewhere else, because the bottleneck is almost always somewhere else.

**Core principle:** Measure, localize, change one thing, measure again. Intuition selects what to measure; it never selects what to fix.

**Companion skills:** `systematic-debugging` — same discipline applied to wrongness rather than slowness. Both refuse to act before the cause is located.

## The Iron Law

```
NO OPTIMIZATION WITHOUT A MEASUREMENT THAT NAMES THE BOTTLENECK
```

You must be able to say "X accounts for N% of the time" *before* you change X. Not "X looks expensive." Not "X is O(n²)." A measurement, with a number.

**No exceptions:**
- Not for "this is obviously the slow part" — obvious is what makes it worth measuring
- Not for "the fix is cheap anyway" — a cheap fix to a non-bottleneck is pure risk with zero payoff
- Not for changes you would make on style grounds regardless. Make them; just don't call it performance work

**The corollary:** a change without an after-measurement is not an optimization, it is a guess that shipped.

## Step 0: Define the Target

"Slow" is not a bug report. Write down all four before touching anything:

| | Example |
|---|---|
| **Metric** | End-to-end latency of `POST /documents` |
| **Statistic** | p99, not mean — means hide the problem users complain about |
| **Load** | 200 concurrent clients, production-shaped data volume |
| **Target** | Under 300ms, from 2.1s today |

Without a target you cannot tell when you are done, and performance work has no natural stopping point. Without a statistic you will optimize the average and never touch the tail that generated the complaint.

## Step 1: Reproduce It

You need a harness that produces the slow behavior on demand, repeatably.

- **Real data shape.** A thousand dev rows will not reproduce a missing index; ten million will.
- **Warm up first**, then measure. JIT compilation, connection pools, and page cache all make the first run a different program.
- **Repeat and take the distribution.** A single timing is noise. Report min/p50/p99, not one number.
- **Pin the environment.** Same machine, same build flags, no other load. Especially: measure a **production build** — a dev-mode framework build can be 10× slower and is not the thing you are shipping.

If you cannot reproduce it locally, measure in the environment where it happens. Production profiling at low sample rates is safe and is better than a faithful reproduction you do not have.

## Step 2: Characterize Before Profiling

Two minutes here saves an hour of profiling the wrong dimension.

| Observation | What it implicates |
|---|---|
| Slow on the first call, fast after | Cold cache, lazy init, connection setup, JIT |
| Slow always, uniformly | An algorithm or a per-call fixed cost |
| Fast at low load, cliff at high load | Contention, pool exhaustion, or a queue — not the code path |
| Time scales with input size superlinearly | Complexity bug — find the nested loop before you profile |
| p50 fine, p99 terrible | GC pauses, lock convoy, retries, a rare slow path |
| CPU at 100% | Compute-bound → CPU profile |
| CPU low, latency high | Waiting — I/O, network, lock, or a `sleep` |
| Memory grows and never returns | Retention, not allocation rate → heap profile with two snapshots |
| Slow only in production | Data volume, concurrency, network topology, or config |

**A quick sanity check:** concurrency ≈ throughput × latency (Little's Law). If you serve 100 req/s at 2s each, roughly 200 requests are in flight. If the pool holds 20 connections, the pool is the bottleneck and no amount of query tuning will help.

## Step 3: Profile the Right Dimension

Profile the dimension the characterization implicated. A CPU profile of an I/O-bound program shows an idle process and teaches you nothing.

| Dimension | When | What it shows |
|---|---|---|
| **CPU** | CPU pegged, compute-bound | Which functions burn cycles |
| **Allocation** | High GC time, memory churn | Where garbage comes from |
| **Heap (in-use)** | Memory grows without bound | What is retained, and by whom |
| **Block / wait** | Low CPU, high latency | What the program waits on |
| **Mutex / lock** | Degrades with concurrency | Contended locks |
| **Execution trace** | Latency spikes with no obvious owner | GC pauses, scheduler stalls, serialization |
| **Query plan** | The database is involved at all | Scans, bad join order, missing indexes |

Exact invocations per stack — Go, Node, Python, browser, SQL, system-level: [references/profiling-tools.md](references/profiling-tools.md).

**Read the profile top-down by cumulative time**, and be suspicious of flat profiles. A profile with no peak usually means the cost is spread across a call made far too many times — count the calls, don't just time them.

## Step 4: The Usual Suspects

Once localized, the cause is usually on this list.

| Layer | Cause | Tell |
|---|---|---|
| Database | N+1 queries | Query count scales with result count |
| Database | Missing index | `Seq Scan` on a large table in the plan |
| Database | Index exists but is unused | Type mismatch, function on the column, or a leading-wildcard `LIKE` |
| Database | `SELECT *` over wide rows | Bytes transferred dwarf the rows needed |
| Application | Work inside a loop that could be hoisted | Same call, same arguments, n times |
| Application | Serialization/deserialization | JSON encode/decode dominates a CPU profile |
| Application | Unbounded concurrency | Goroutine/promise count grows with load; memory follows |
| Application | Lock held across I/O | Mutex profile shows a long hold, not many acquisitions |
| Application | Allocation in a hot path | Alloc profile dominated by one call site |
| Network | Chatty protocol | Many small round trips where one batch would do |
| Network | No connection reuse | TLS handshakes in the trace |
| Frontend | Render-blocking waterfall | Sequential dependent requests in the network panel |
| Frontend | Work on the main thread | Long tasks in the performance trace |
| Frontend | Shipping the whole bundle | Large initial JS payload, most of it unused |

**Before optimizing, ask whether the work can be avoided entirely.** Caching, batching, pagination, doing it asynchronously, or not doing it are all bigger wins than making it faster, and usually simpler.

## Step 5: Change One Thing, Then Measure Again

```
one change → re-measure → keep it or revert it → repeat
```

- **One variable at a time.** Two changes at once and you cannot attribute the result — including the case where one helped and the other hurt by the same amount.
- **Revert what does not measurably help.** Every optimization costs readability; unpaid-for complexity is a permanent tax.
- **Confirm the improvement is real**, not noise. Compare distributions across repeated runs (`benchstat` and equivalents do this properly), not two single numbers.
- **Commit the benchmark** with the fix. It is the only thing that will notice when the regression comes back.
- **Re-profile after each win.** The bottleneck moves. The second-biggest cost is now the biggest, and it is often somewhere entirely new.

Stop when you hit the target from Step 0. Continuing past it trades real maintainability for a number nobody asked for.

## Tail Latency

If the complaint is about p99, the mean is actively misleading — a fix that improves the mean often makes the tail worse.

Common causes, in rough order of frequency:

- **Queueing.** Utilization above ~70% makes wait time rise sharply. The fix is capacity or backpressure, not faster code.
- **GC pauses.** Look at pause distribution, not total GC time. Reduce allocation rate or retained set.
- **Lock convoy.** One slow holder makes every waiter slow; latency spikes correlate with contention, not load.
- **Retries.** A timeout plus a retry turns one slow request into three, exactly when the system is least able to serve them.
- **Cold paths.** Cache misses, first-request-after-idle, connection re-establishment.
- **Head-of-line blocking.** One slow item stalls everything behind it in the same connection, batch, or partition.

**Watch for coordinated omission in your load generator.** A harness that waits for each response before sending the next request stops sending load exactly when the system is slowest — which erases the tail you are trying to measure. Use a generator that sends at a fixed rate, or one that explicitly corrects for it.

## Red Flags

- "This is obviously the slow part" — with no profile
- Optimizing a function that a profile shows at 0.4% of runtime
- Benchmarking a dev build, or with an empty database
- A single timing used as evidence
- Two changes in one commit, both labeled performance
- A micro-benchmark improving while the end-to-end metric does not move
- Caching added before the cost of the uncached path was measured
- "It should be faster now"

**All of these mean: go back and measure.**

## Common Mistakes

**Optimizing the part you understand.** Familiarity is not evidence. The bottleneck is disproportionately in code you did not write.

**Micro-benchmarks that do not reflect real use.** Amdahl's law is unforgiving: making 5% of the runtime twice as fast buys 2.5%.

**Confusing allocation with retention.** High allocation rate is a GC-pressure problem. Growing in-use heap is a leak. They need different profiles and different fixes.

**Caching to hide a bug.** A cache in front of an accidentally-quadratic function makes the problem invisible until the cache misses under exactly the conditions where you need it most.

**Ignoring variance.** A change that improves p50 and degrades p99 is usually a regression, because the tail is what users report.

**No after-measurement.** Without it you have shipped a diff, not a fix — and you have no idea which it was.
