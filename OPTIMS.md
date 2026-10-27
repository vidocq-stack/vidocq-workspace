# Optimisation and quality tracker

Where each Vidocq component stands on two efforts: **SonarQube cleanup** (the whole project, not only the new-code gate) and **performance work**. One row per component; the details below say what was done, by which pull request, and what is left.

How the tables are kept:

- **SonarQube figures** come from `sonar.vidocq.dev` (project `vidocq-<component>`, branch `main`). Refresh them at each update; the date of the snapshot is in the table heading. `QUALITY.md` explains the server, the gate and the tools.
- **Performance figures** are never written here without their source: every number points to an entry of a `BENCH.md` (the component's own, or `vidocq-benchmarks/BENCH.md` for the cross-runtime shootout).
- **Status** words: *done* (nothing known left), *in progress* (pull requests open or a pass under way), *to do* (identified, not started), *not started* (no pass yet).

## At a glance

SonarQube snapshot of 2026-10-27 (evening), branch `main`. Ratings: reliability / security / security review / maintainability.

| Component | Gate | Ratings | Open issues | Coverage | Sonar cleanup | Performance |
|---|---|---|---|---|---|---|
| chappe | OK | A / A / A / A | 0 | 82.1 % | done | done for now, see below |
| cassini | OK | A / A / A / A | 280 | 57.3 % | in progress (smells, coverage) | in progress |
| champollion | OK | C / C / A / A | 402 | 68.0 % | to do | in progress |
| vidocq (runtime) | OK | A / A / A / A | 632 | 83.0 % | in progress (smells) | — |
| vauban | OK | A / A / A / A | 0 | 86.1 % | done | to do (small) |
| foy | OK | A / A / A / A | 0 | 86.5 % | done | not started |
| bodoni | OK | A / A / A / A | 0 | 92.4 % | done | not started |
| verne | OK | A / A / A / A | 0 | — | done (empty) | — |
| knock | OK | A / A / A / A | 16 | 82.8 % | to do (small) | not started |
| ravel | OK | A / C / A / A | 170 | 66.7 % | not started | not started |
| peano | OK | C / A / A / A | 197 | 76.9 % | not started | not started |
| cervantes | OK | C / C / A / A | 68 | 66.9 % | not started | not started |
| dirac | OK | C / C / A / A | 87 | 68.2 % | not started | not started |
| grimm | OK | C / C / A / A | 249 | 60.4 % | not started | not started |
| heisenberg | OK | C / C / E / A | 179 | 53.9 % | not started | not started |
| cyrano | OK | E / C / A / A | 214 | 64.0 % | not started | not started |
| humboldt | OK | E / A / E / A | 159 | 65.6 % | not started | not started |
| ibarra | OK | C / D / E / A | 504 | 85.4 % | not started | not started |
| mansart | OK | C / D / E / A | 561 | 43.9 % | not started | not started |
| tassis | OK | E / D / A / A | 350 | 86.1 % | not started | not started |
| noether | OK | C / D / A / A | 1187 | 81.1 % | not started | not started |

Request-path performance, Todo API at 40k req/s (vidocq-benchmarks `BENCH-20261027-05`): Vidocq 0.4.0-RC1 used 17.5 % of a CPU per 1k req/s; the 0.4.0-SNAPSHOT of `main` on 2026-10-27 uses 8.1, below Helidon MP, Open Liberty and Spring Boot, close to Quarkus classic, above Quarkus reactive. That SNAPSHOT predates cassini#81, chappe#70 and champollion#40.

## SonarQube cleanup

The method that works (from Chappe, the pilot, and the October 2026 passes):

1. **Reliability and security first**: bugs, vulnerabilities, hotspots. A fix that changes behaviour gets a failing test first.
2. **Then code smells**, mechanical rules first (`S7467`, `S1192`, `S108`, `S1186`, `S1128`…), cognitive complexity (`S3776`) only on well-tested methods.
3. **Then coverage** of the least covered classes.
4. **False positives and safe hotspots** are marked in SonarQube with a comment saying why, after reading the code; never silenced blindly.

Pitfalls met:

- The PR analysis counts as *new* every line that differs from `main`, so an old finding on a line we only touched cosmetically comes back as new. A line that cannot be fixed goes back to `main`'s exact text rather than getting a `NOSONAR`.
- A green gate is not a clean project: the gate only looks at new code. Check the overall ratings too.
- Removing a constant can make its literal count as duplicated elsewhere (`S1192`); method splits can leave unused parameters (`S1172`) that only the `main` analysis reports.
- Replacing a literal by a constant puts its whole method in the diff: a long method then brings its old cognitive complexity (`S3776`) back as new. Split it in the same pull request.
- External analysers (Opengrep) may publish their findings only on some analyses: a project can drop from security A to D between two runs with no code change. Review them, fix or mark them.

| Component | Done | Left |
|---|---|---|
| chappe | Pilot, 0 issues (chappe#50 and earlier). | Keep it at 0. |
| cassini | #79 request path; #80 tests (coverage 63 % → gate OK); #81; #82 bugs and vulnerabilities (XXE, interrupt flag, record equality); #83 about 160 smells plus 15 `S3776` splits; #84 owner-only upload file, #85 unused parameters; 10 false positives and 2 safe hotspots marked. Issues 500 → 280, ratings C/E/E/A → A/A/A/A. | `S3776`, `S135`, `S112`, the `S7467` catches no test reaches; coverage 57 % → 80 %. |
| champollion | #37 mechanical pass with tests; #39 `S1192` that turned the gate red. | Whole project: 402 issues, reliability and security C. Seven files with out-of-scope findings were left out of #37 (BUG-20261027-01..04). |
| vidocq (runtime) | #384 gate fix; #385 mechanical pass; #387 20 vulnerabilities and 84 of 85 bugs; #388 smells; #389, #390 literals the cleanup turned into constants; 14 safe hotspots and 16 false positives (Opengrep, one `S3077`) marked after review. Issues 1303 → 632, ratings E/D/E/A → A/A/A/A. | The 174 `S7467` catches no test reaches, `S3776`, `S135`, `S6813` (field injection CDI needs), test-source smells. |
| vauban, foy, bodoni | Clean. | Keep them at 0. |
| other components | — | Not started. Largest: noether (1187), mansart (561), ibarra (504), tassis (350). |

## Performance work

Origin: the cross-runtime shootout of `vidocq-benchmarks` (Todo API, wrk2, 100 connections) showed Vidocq 0.4.0-RC1 last, at 700 % CPU for 40k req/s. A JFR analysis per brick drives the list. Measurements are run by the benchmark session on the dedicated machine; numbers live in `vidocq-benchmarks/BENCH.md`.

| Component | Done (pull request: change) | Left (estimated gain, points of CPU per 1k req/s) |
|---|---|---|
| chappe | #68 one watchdog virtual thread per connection instead of two per request; #69 drain a request body without a 4 KB buffer; #70 one blocking read per keep-alive request (no non-blocking probe, no blocking-mode toggles). | `Http2FrameWriter` still on `BoundedWrites`. The remaining kernel gap with an event loop (about 10 system calls per request against 2.9, `strace -c`, vidocq-benchmarks `BENCH-20261027-06`) is the JDK's virtual-thread socket read: a non-blocking read that returns EAGAIN, then an `EPOLL_CTL_MOD` one-shot re-arm by the poller. Parking before the read (through `sun.nio.ch`, an experiment never merged) removed the EAGAIN read only, a gain inside the noise: dropped. Only a hybrid event-loop model would remove it; deferred. |
| cassini | #75 request-path caches (no `ClassNotFoundException` per request, pre-matching filters run once, base URI cache, media-type caches, verb-first router, body read sized by `Content-Length`); #76 dispatch inline on the connection's virtual thread; #77 per-method parameter metadata, injectable fields, bean resolution cache, headers through Chappe, `Invoker` split; #78 response body handed over without copies; #81 SSE stream end fix; #86 entity buffer and response headers handed to the transport, status-code table, base URI without a `URI` per request, lazy request-context map. | Measure #86 (expected 0.3–0.5). Writer cache per route left out: `findWriter` is already under 512 B per call and a cache would skip `isWriteable` calls the TCK observes. CASSINI-007 left open. |
| champollion | #35 generator buffer instead of a synchronised `BufferedWriter`; #36 static bindings below the root and through the context class loader; #38 small bodies read without an 8 KB decoder buffer; #40 UTF-8 encoded straight to the stream, buffer growing from 128. | Re-measure after #40 (expected 0.3–0.5). |
| vauban | Bean resolution cache (cassini#77, `VaubanBeanProvider`). | `RequestContext.deactivate` copies its map; cache the scope lookup in `RequestScope.current` (about 0.1). |
| JVM / model | — | Measure syscalls and context switches per request (`perf trace -s`, `perf stat`) and the kernel share with async-profiler `--cstack` on the benchmark machine: JFR does not see the 2.9 points of system time. |

## Next

1. Cassini's remaining request-path copies (list above), then a new measurement.
2. Champollion's whole-project Sonar pass (reliability and security C).
3. Then the next components by size of their backlog, MicroProfile ones first where the gate is about to be used.
