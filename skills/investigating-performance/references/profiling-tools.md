# Profiling Tools

Concrete invocations per stack. Pick the dimension from the SKILL.md characterization table first, then the tool.

## Contents

- Go
- Node and the browser
- Python
- SQL: PostgreSQL and SQLite
- System level
- Comparing before and after

## Go

**Benchmarks with statistically valid comparison:**

```bash
go test -bench=BenchmarkParse -benchmem -count=10 > before.txt
# make the change
go test -bench=BenchmarkParse -benchmem -count=10 > after.txt
benchstat before.txt after.txt      # go install golang.org/x/perf/cmd/benchstat@latest
```

`benchstat` reports whether the difference survives the noise. A single `-count=1` pair does not, and cannot.

**Profiles from a benchmark:**

```bash
go test -bench=. -cpuprofile cpu.out -memprofile mem.out -blockprofile block.out
go tool pprof -http=:8080 cpu.out          # flame graph in a browser
go tool pprof -top -nodecount=20 cpu.out   # text, top by cumulative
```

**Profiles from a running server** — import `net/http/pprof`, then:

```bash
go tool pprof -http=:8080 'http://localhost:8080/debug/pprof/profile?seconds=30'  # CPU
go tool pprof -http=:8080 'http://localhost:8080/debug/pprof/heap'                # in-use
go tool pprof -http=:8080 'http://localhost:8080/debug/pprof/allocs'              # cumulative
go tool pprof -http=:8080 'http://localhost:8080/debug/pprof/goroutine'           # leaks
```

Block and mutex profiles are **off by default** and return nothing until enabled:

```go
runtime.SetBlockProfileRate(10000)     // sample one blocking event per ~10µs blocked
runtime.SetMutexProfileFraction(100)   // sample 1/100 contention events
```

**Leak hunting** — the diff, not the snapshot:

```bash
curl -s localhost:8080/debug/pprof/heap > h1.out
# let it run under load
curl -s localhost:8080/debug/pprof/heap > h2.out
go tool pprof -http=:8080 -base h1.out h2.out     # what grew between the two
```

**Execution trace** for latency spikes with no obvious owner — shows GC pauses, scheduler stalls, and syscall blocking on a timeline:

```bash
curl -s 'localhost:8080/debug/pprof/trace?seconds=5' > trace.out
go tool trace trace.out
```

Run with `GODEBUG=gctrace=1` to print every GC with its pause time; that alone often settles whether GC is the tail-latency cause.

## Node and the Browser

**Node CPU and heap:**

```bash
node --cpu-prof --cpu-prof-dir=./prof app.js       # .cpuprofile → load in DevTools
node --heap-prof --heap-prof-dir=./prof app.js
npx clinic doctor -- node app.js                   # guided: which dimension to chase
npx clinic flame -- node app.js
```

**Heap snapshots for leaks** — take two under load and compare in DevTools' Memory panel using "Objects allocated between snapshot 1 and 2". `--inspect` plus `writeHeapSnapshot()` gets you snapshots from a live process.

**Browser:** record a performance trace in DevTools, then look for long tasks (>50ms) on the main thread and the request waterfall. For a repeatable measurement rather than a manual recording, drive it with Playwright and read the Performance API:

```js
const entries = await page.evaluate(() =>
  JSON.stringify(performance.getEntriesByType('navigation').concat(
    performance.getEntriesByType('resource').slice(0, 20))));
```

Bundle size, before blaming runtime code:

```bash
npx vite-bundle-visualizer          # or: npx source-map-explorer dist/assets/*.js
```

## Python

```bash
py-spy top --pid 1234                     # live, no code change, works on prod
py-spy record -o profile.svg --pid 1234   # flame graph
py-spy dump --pid 1234                    # stack of every thread — for hangs

python -m cProfile -o out.prof script.py && snakeviz out.prof
python -m memray run script.py && memray flamegraph memray-*.bin   # allocations
```

`py-spy` attaches to an already-running process without restarting or instrumenting it, which makes it the right first tool for anything already slow in production.

## SQL: PostgreSQL and SQLite

**The plan with real numbers** — `ANALYZE` executes the query, `BUFFERS` shows cache behavior:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT ...;
```

Read for: `Seq Scan` on a large table, actual-vs-estimated row counts off by an order of magnitude (stale statistics — run `ANALYZE`), nested loops over large inputs, and `Rows Removed by Filter` far exceeding rows returned.

**Find the expensive queries** rather than guessing which one:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT calls, round(mean_exec_time::numeric, 2) AS mean_ms,
       round(total_exec_time::numeric) AS total_ms, query
  FROM pg_stat_statements
 ORDER BY total_exec_time DESC LIMIT 20;
```

Order by **total** time, not mean: a 4ms query called 90,000 times per minute outranks a 900ms report nobody runs. This is also how you find N+1 — it shows up as an enormous `calls` count on a trivial query.

Other useful checks:

```sql
-- Indexes that are never used (candidates for removal — they cost writes)
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Currently blocked queries
SELECT pid, wait_event_type, wait_event, left(query, 60) FROM pg_stat_activity
 WHERE state = 'active' AND wait_event IS NOT NULL;
```

`auto_explain` with `log_min_duration` captures plans for slow queries in production without running them by hand.

**SQLite:**

```sql
EXPLAIN QUERY PLAN SELECT ...;     -- look for SCAN vs SEARCH
ANALYZE;                           -- populate sqlite_stat1; plans are bad without it
PRAGMA optimize;                   -- run periodically
```

`SCAN TABLE x` where you expected `SEARCH TABLE x USING INDEX` is the finding. Also check `PRAGMA journal_mode` — WAL is usually the right answer for concurrent readers, and the default is not WAL.

## System Level

```bash
perf top -p <pid>                   # where CPU goes, including kernel and libs
perf record -g -p <pid> -- sleep 30 && perf report
strace -c -p <pid>                  # syscall counts — finds accidental chattiness
pidstat -p <pid> 1                  # per-process CPU, memory, I/O over time
iostat -xz 1                        # disk saturation (%util, await)
ss -ti                              # per-socket RTT, retransmits, congestion window
```

The USE method is a fast triage pass over these: for each resource — CPU, memory, disk, network — check **U**tilization, **S**aturation (queue depth), and **E**rrors. Saturation usually points at the bottleneck before utilization does.

## Comparing Before and After

Whatever the stack, the comparison rules are the same:

1. **Same machine, same build, same data.** Cross-machine comparisons are worthless.
2. **Warm up, then measure.** Discard the first runs deliberately, not accidentally.
3. **Repeat at least 5–10 times** and compare distributions, not single numbers.
4. **Report p50 and p99.** A change that improves the mean and worsens the tail is usually a regression.
5. **Interleave the runs** (A, B, A, B) when the machine may drift thermally or under background load.
6. **State the delta with its uncertainty** — "1.42s → 0.31s, ±0.02 over 10 runs" — not "much faster".
