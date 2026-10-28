# Optimisation and quality tracker

Where each Vidocq component stands on two efforts: **SonarQube cleanup** (the whole project, not only the new-code gate) and **performance work**. One row per component; the details below say what was done, by which pull request, and what is left.

How the tables are kept:

- **SonarQube figures** come from `sonar.vidocq.dev` (project `vidocq-<component>`, branch `main`). Refresh them at each update; the date of the snapshot is in the table heading. `QUALITY.md` explains the server, the gate and the tools.
- **Performance figures** are never written here without their source: every number points to an entry of a `BENCH.md` (the component's own, or `vidocq-benchmarks/BENCH.md` for the cross-runtime shootout).
- **Status** words: *done* (nothing known left), *in progress* (pull requests open or a pass under way), *to do* (identified, not started), *not started* (no pass yet).

## At a glance

SonarQube snapshot of 2026-10-28 (evening), branch `main`. Ratings: reliability / security / security review / maintainability. Target for the Jakarta EE Core, MicroProfile and Jakarta Data bricks: A everywhere, coverage of at least 80 % (TCK runs are not counted) and no open issue. All fifteen bricks of that scope reach it.

Since 2026-10-28 the SonarQube check is **blocking** on these fifteen repositories: `blocking: 'true'` on the `Vidocq/ci` sonar action and `sonar / sonar (pull_request)` among the required checks of `main`. The server's default profile and gate are "Vidocq way": Sonar way, with field injection (`java:S6813`) lowered to INFO, and a gate that fails on new issues of LOW severity and above, so INFO findings show without blocking.

| Component | Gate | Ratings | Open issues | Coverage | Sonar cleanup | Performance |
|---|---|---|---|---|---|---|
| chappe | OK | A / A / A / A | 0 | 82.1 % | done | done for now, see below |
| cassini | OK | A / A / A / A | 0 | 84.5 % | done | in progress |
| champollion | OK | A / A / A / A | 0 | 91.3 % | done | in progress |
| vidocq (runtime) | OK | A / A / A / A | 0 | 85.1 % | done | — |
| vauban | OK | A / A / A / A | 0 | 86.1 % | done | to do (small) |
| foy | OK | A / A / A / A | 0 | 86.5 % | done | not started |
| bodoni | OK | A / A / A / A | 0 | 92.4 % | done | not started |
| verne | OK | A / A / A / A | 0 | — | done (empty) | — |
| knock | OK | A / A / A / A | 0 | 82.6 % | done | not started |
| ravel | OK | A / A / A / A | 0 | 92.8 % | done | not started |
| cervantes | OK | A / A / A / A | 0 | 91.2 % | done | not started |
| dirac | OK | A / A / A / A | 0 | 91.9 % | done | not started |
| grimm | OK | A / A / A / A | 0 | 95.6 % | done | not started |
| heisenberg | OK | A / A / A / A | 0 | 91.7 % | done | not started |
| cyrano | OK | A / A / A / A | 0 | 90.1 % | done | not started |
| humboldt | OK | A / A / A / A | 0 | 92.5 % | done | not started |
| mansart | OK | A / A / A / A | 0 | 86.6 % | done | not started |
| peano | OK | C / A / A / A | 197 | 76.9 % | not started | not started |
| ibarra | OK | C / D / E / A | 504 | 85.4 % | not started | not started |
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
- The `main` analysis finds what a PR analysis cannot: moving a method's only caller brings `S3398` ("move this method into…") on `main` after the merge. Plan a small follow-up PR after each large one.
- With the blocking gate, marking a deliberate finding in the PR analysis turns the gate green, but the failed `sonar` job stays red (Forgejo has no job rerun API): push a new commit to run it again.

| Component | Done | Left |
|---|---|---|
| chappe | Pilot, 0 issues (chappe#50 and earlier); #72 blocking gate. | Keep it at 0. |
| cassini | #79–#85 cleanup (500 → 280 issues, C/E/E/A → A/A/A/A); coverage passes #87 (core API), #88 (client), #90 (multipart, Maven plugin, test harness, SSE, `UriInfo`), 57 % → 83 %, with 21 spec bugs fixed (CASSINI-009..031); #89 escaping of generated string literals (CASSINI-025); #91 zero-issues pass and blocking gate; #92 the last three findings of the `main` analysis. | Keep it at 0; processor, cdi and jdk-http modules below 80 % on their own. |
| champollion | #37, #39 mechanical; #41 the 25 bugs (C → A); #42 about 85 smells; #43 coverage 68 % → 91 % with ten JSON-B / protobuf bugs fixed; #44 zero-issues pass (four more JSON-B bugs) and blocking gate; #45 the findings of the `main` analysis; Opengrep false positives marked. | Keep it at 0. |
| vidocq (runtime) | #384–#390 (1303 → 632 issues, E/D/E/A → A/A/A/A); #391 zero-issues pass and blocking gate; #392 the findings left on `main`; #393 the langchain4j-cdi MCP extension; deliberate findings (CLI output of the jlink/jpackage goals, stub servers that sleep on purpose…) marked with their reason. | Keep it at 0. |
| vauban, foy, bodoni | Clean; vauban#226 and foy#87 blocking gate. | Keep them at 0. |
| cervantes | #38: CERV-009 (raw token in `toString`), coverage 67 % → 91 %, smells 68 → 7; JWE/JCA false positives marked; zero-issues pass and blocking gate. | Keep it at 0. |
| dirac | #36: DRC-007 (metrics registered twice), coverage 68 % → 92 %, smells 87 → 5; #37 zero-issues pass and blocking gate. | Vauban refuses an `@Inject` constructor on an interceptor (to check in Vauban); field injection is INFO in "Vidocq way". |
| heisenberg | #46: BUG-011..013 (lost counter updates under load, missing `uses` in `module-info`), coverage 54 % → 91 %; #47 zero-issues pass and blocking gate; #48 policy-chain helpers kept inside `Chain`. | `S107` on the public `FtMetricsRecorder.register` SPI is marked, pending a decision on the SPI shape. |
| ravel | #37: coverage 67 % → 92 %, 112 issues fixed; #38 zero-issues pass and blocking gate. | Keep it at 0. |
| cyrano | #47: three bugs (duplicate `@ClientHeaderParam`, wrapped interceptor exceptions, case-sensitive `Content-Type`), coverage 64 % → 90 %; #48 zero-issues pass and blocking gate. | Keep it at 0. |
| humboldt | #36: three metrics bugs (observable counters added up, double final export, `join` timeout), coverage 66 % → 92 %; #37, #38 zero-issues pass and blocking gate. | Keep it at 0. |
| grimm | #36: six OpenAPI bugs (YAML reader rewritten, path joining, OAuth flows…), coverage 60 % → 95 %; #37, #38 zero-issues pass and blocking gate. | Keep it at 0. |
| mansart | #53: twelve Jakarta Data bugs (MANSART-010..022: `findFirst`, CRUD inserts, `@By`, projections, batch methods…), coverage 44 % → 84 %, reliability C → A; #54 MANSART-023: a JDQL literal could name a class to load (dev console path), now resolved against the model; #55 zero-issues pass and blocking gate; #56 the findings of the `main` analysis. | Keep it at 0. |
| knock | #46 zero-issues pass and blocking gate. | Keep it at 0. |
| other components | — | Not in the Core / MicroProfile / Data scope: peano, ibarra, tassis, noether. |

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

1. Keep the fifteen in-scope bricks at 0 issues: the blocking gate refuses any pull request that adds one.
2. Cassini's remaining request-path copies, then a new performance measurement.
3. The components outside the scope (peano, ibarra, tassis, noether) when they come back into focus.
