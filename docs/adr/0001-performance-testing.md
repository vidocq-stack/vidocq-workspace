# ADR 0001 — Performance testing of the ecosystem

* Status: Accepted
* Date: 2026-10-22
* Deciders: Yann Blazart

## Context

Every brick must show what load it sustains, how it holds that load over time, and where it stands against the
alternatives a user would otherwise pick. Today the figures exist, but by hand and one brick at a time:

* eleven bricks carry a JMH module (`chappe-bench`, `champollion-bench`, `vauban-bench`, `peano-bench`,
  `tassis-bench`, `ravel-bench`, `heisenberg-bench`, `dirac-bench`, `cervantes-bench`, `erasmus-bench`,
  `grimm-bench`), and fourteen repositories a `BENCH.md` filled by hand;
* Chappe has the only external load harness: a `wrk2` open-loop shootout (fresh container per rate,
  coordinated-omission correction, `p99 < 10 ms` filter) against nginx, Jetty 12, Netty 4, Helidon SE, the JDK
  server, Go and Vert.x, run by hand on macuntu through `chappe-bench/docker/run-remote.sh`. `BENCHMARKS.md` makes it
  the canonical method;
* a Grafana was installed on 2026-10-20 as a stack of the Foix Portainer (`grafana.dev.vidocq.io`, Codefloe OAuth
  `GRAFANA_DEV`) to draw these results. It has no data source and no dashboard yet;
* no figure is measured on a schedule, so a regression is found when someone happens to rerun a bench.

A benchmark run on a shared CI runner measures its neighbours: the Foix runner shares its host with SonarQube,
Grafana, Kroki and the reverse proxy. The machine matters more than the harness.

## Decision

### Three levels, three questions

| Level | Question | Tool | Scope |
|---|---|---|---|
| L1 — micro | Did this hot path regress? | JMH, `-rf json` | Every brick with a `*-bench` module |
| L2 — capacity and endurance | Which rate does the brick sustain under its latency objective, and does it hold it? | `wrk2` open-loop rate steps, then a soak at ~70 % of that capacity | Bricks that take traffic: chappe, foy, cassini, mansart/noether (PostgreSQL in a container), tassis |
| L3 — competition | Where does Vidocq stand against the alternatives? | The same scenarios on every target | See below |

The L2 soak lasts 30 to 60 minutes and records, over time: p99 drift, RSS and old generation (must level off),
file descriptors and threads (must not climb), errors. A JFR recording is kept for the last minutes.

L3 compares like with like:

* **Chappe**, an HTTP server, against HTTP servers: Helidon SE WebServer, Jetty, Netty, Vert.x (the existing
  shootout). Quarkus is not a Chappe competitor: its HTTP layer is Vert.x, already in the shootout.
* **The assembled Vidocq runtime** (cassini + champollion + vauban on chappe) against **Quarkus, Helidon MP, Spring
  Boot and Open Liberty**.
* Scenarios are the TechEmpower ones (plaintext, JSON, single query, fortunes): known, so the figures read without
  explanation.
* Besides throughput and latency, L3 measures cold start, time to first response and RSS, on the JVM and, where the
  competitor supports it, as a GraalVM native image (Open Liberty runs on the JVM only).
* Every target runs on the same JDK with the same heap, configured by its own performance guide. Versions are pinned
  and bumped by Renovate; the configurations are published with the results, and a competitor's maintainers may
  propose a better tuning.

### The machine: macuntu

The benches run on **macuntu**, a Mac mini 2018 (`Macmini8,1`, Intel Core i7-8700B, 6 cores / 12 threads, 32 GB,
Ubuntu 22.04, kernel 5.15), at Montreuil.

Why this machine:

* it is already where the Chappe shootout ran since May 2026, so the existing series continue;
* hardware that no longer changes keeps a series comparable over years;
* a 6-core box is close to what an application gets in a container or a small VM, so the figures are
  conservative rather than flattering;
* what L1 and L3 report is a ratio — this commit against the previous one, Vidocq against a competitor — which a
  modest machine measures as well as a large one.

Its limits, and how they are handled:

* **Frequency and heat.** The small chassis throttles under sustained all-core load. During a bench window the
  governor is set to `performance` and turbo is disabled (`intel_pstate/no_turbo=1`): the CPU stays at its 3.2 GHz
  base, steady rather than fast. The harness samples frequency and temperature during the run, and a run whose
  frequency drops below base is marked `throttled` and kept out of trends and alerts.
* **Six cores for two processes.** The load generator and the server are pinned to disjoint physical cores, each with
  its hyper-thread sibling (mapping read from `lscpu -e`), as the shootout already does with `cpuset`.
* **Absolute figures.** They describe this machine, not a server; every published figure names the hardware.
* **A single machine.** If it dies, its series end. A replacement starts new series, calibrated by running the last
  release on both machines when possible.

Every result carries a fingerprint of the environment: CPU model, kernel, governor and turbo state, JDK, JVM flags,
commit SHA.

### The bench window

macuntu also hosts two CI runners, `CodefloeRunnerMontreuil01` and `CodefloeRunnerMontreuil02`, each with its
Docker-in-Docker container (`-dind`). Benchmarks and CI jobs never run at the same time:

* a third runner on macuntu, `BenchMontreuil01`, carries the label `vidocq-bench` only, with a capacity of one job,
  and runs only inside the window;
* a scheduled workflow of `Vidocq/ci` opens the window every night at 00:30 UTC, through the Portainer API of
  macuntu (`ci/bench-window`): it stops both CI runners and their `-dind` containers once their running jobs, if
  any, have ended (the runners need `runner.shutdown_timeout`), sets governor and turbo from a short-lived
  privileged container, and starts `BenchMontreuil01`. At 02:45 UTC it closes the window the other way round, so
  that `tck-nightly` (03:00 UTC) has every runner again. The Saturday window runs until 06:00 UTC for the long runs.
  The workflow runs on the Foix runner (label `vidocq-foix`), not on a runner it stops; it is the only one to hold
  the Portainer token, which is root on macuntu. Nothing is installed on the host, and the window is versioned
  and visible in the CI;
* a bench workflow (`runs-on: vidocq-bench`) only ever finds a runner inside the window. A job dispatched during the
  day waits for the next window, so a release run needs no special handling;
* the first step of every bench job checks that nothing else runs on the host (no other container, both CI runners
  stopped) and aborts otherwise rather than produce a noisy figure. The harness keeps watching during the run: each
  measurement records the CPU used by containers outside the benchmark, and a measurement disturbed above a
  threshold is marked and left out of the published figures. The Chappe pilot of 2026-10-22, run outside any window,
  showed why: a CI job started on `CodefloeRunnerMontreuil02` during the shootout (its `-dind` container at 304 %
  CPU at the end of the run), and the last three servers measured fell far below the reference run; without a
  timestamp per measurement, the link could not be proven.

### Cadence

| When | What | Purpose |
|---|---|---|
| Pull request | Nothing by default | A noisy, long check helps no one at review time |
| Nightly | L1 short profile, plus L2 capacity of the HTTP bricks, **only for repositories whose `main` moved** | A regression is known the next morning |
| Saturday | L1 full (more forks), L2 soaks, L3 full shootout | Competitors do not change every night |
| Release | L1 + L2 + L3, on the release commit, before deploying | The reference figures of the version |

The competitors also act as a **control group**: when their figures move between two Saturdays while their version
did not, the machine changed, and that week's trends are read with care.

The release run happens on the commit about to be released, not after the deploy: a regression found once the
artefact is on Maven Central is found too late. Its results become the version's frozen figures.

### Regressions alert, they never block

* After P0 (below), each benchmark has a noise band: the coefficient of variation over ten identical runs.
* A nightly result outside its band **two nights in a row** opens an issue on the brick's repository and posts to
  Slack (`ci/notify-slack`). One night is not enough: a signal that is red every other night teaches people to
  ignore it.
* At release, the report compares the version with the previous one. It is read in the release checklist; it never
  blocks the release, the same report mode as SonarQube.

### Storage

Results live in three places, each with one role:

| Where | What | Role |
|---|---|---|
| **`Vidocq/bench-results`**, a data repository on Codefloe | The raw results of every run: JMH JSON, `wrk2` output with its HdrHistogram, soak time series, environment fingerprint | **Source of truth.** Append-only, versioned, holds no secret |
| **PostgreSQL**, in the Grafana stack on the Foix Portainer | The same data in tables | Grafana's data source only. **Disposable**: an importer reloads it from the repository |
| **CI artefacts**, with the runner's retention | JFR recordings, logs | Too heavy for git; useful for a few weeks to analyse a regression |

The repository is laid out by run, and a release run is also copied under `releases/` and tagged
(`<brick>-<version>`, e.g. `chappe-0.3.0`):

```
bench-results/
  runs/2026-10-23/chappe/<sha>-nightly/    fingerprint.json, jmh.json, wrk2/…
  runs/2026-10-24/vidocq/<sha>-weekly/     …, competitors/quarkus-<version>.json, …
  releases/chappe/0.3.0/                   the release run, plus report.md
```

* The bench job pushes to the repository with the bot token; the importer, next to Grafana and PostgreSQL on Foix,
  loads each new run. The bench machine holds no database credential, and the database can be rebuilt from the
  repository at any time.
* Prometheus is not used: it pulls live metrics, and these are batch results.
* Schema: `run` (repository, SHA, ref, kind, version, fingerprint, date, flags such as `throttled`), `result` (run,
  benchmark, parameters, metric, value, error, unit), `series` (soak time series).
* Dashboards: one trend per brick with releases as annotations; the comparison with competitors per scenario; the
  soak view (p99, RSS, GC over time); "last night", each delta coloured against its noise band.

### Snapshot and release

The two kinds of run have different status:

* **Runs of `main`** (nightly, Saturday) measure a `-SNAPSHOT`: code nobody has received yet. They go to `runs/` and
  to Grafana, which stays private behind the Codefloe login. They feed trends and regression alerts, and are never
  published or quoted as the figures of Vidocq.
* **The release run**, on the release commit before deploying, gives the only official figures of a version. It is
  frozen under `releases/<brick>/<version>/` and tagged. Its `report.md` compares the version with the previous
  release and is read in the release checklist.

### Publication

Only release runs are published. A generator, the shared action `ci/bench-report`, turns the JSON of
`releases/<brick>/<version>/` into everything below:

```
release run (macuntu)
  └─► bench-results/releases/<brick>/<version>/        raw JSON, tag <brick>-<version>
        └─► ci/bench-report
              ├─ report.md                             release checklist (internal)
              ├─ BENCH.md entry                        bot pull request on the brick
              └─ partials/performance/<version>.adoc   bot pull request on the brick,
                                                       branches docs/<version> and main
```

1. **`BENCH.md`** of each measured brick: an entry in the format the rule of `AGENTS.md` already asks for (date,
   hardware/JVM, exact command, raw results, delta against the previous release). It stays the raw ledger. Scheduled
   runs never go to `BENCH.md`: an entry per night would bury the entries that matter. Figures measured by hand while
   investigating are recorded as today.
2. **The docs**: a Performance page per brick, in the brick's own `docs/en`, as Chappe's `performance.adoc` already
   is. The docs are versioned per release line (`docs/<version>` branches), so the 0.3 docs show the 0.3 figures for
   good.
   * The generated partial carries tables and charts. Charts are `[vegalite]` blocks with their data inline, drawn
     by the Kroki the docs build already uses (`kroki-fetch-diagram: true`): they become static SVG at build time,
     with no JavaScript, no Grafana, and no change to the UI bundle or the playbook. Soak series are downsampled
     (one point every 10 s, about 360 points for an hour) to keep the blocks readable.
   * The partial also lands on `main`, so the next release line inherits every earlier partial and its page can
     draw the evolution across releases.
   * The page mixes written and generated sections:

     | Section | Written by | Content |
     |---|---|---|
     | TL;DR and analysis | A maintainer | What the figures mean, why a ceiling is where it is. A generator cannot write it |
     | Figures of this version | Generated | Key metrics, delta against the previous release |
     | Evolution | Generated | Key benchmarks across releases |
     | Capacity (L2) | Generated | p99 against offered rate, with the latency objective drawn |
     | Endurance (L2) | Generated | p99 and RSS over the soak |
     | Competitors | Generated | For Chappe: against Helidon SE, Jetty, Netty, Vert.x |
     | Methodology and reproducibility | Generated | Machine fingerprint, exact commands, link to the `bench-results` tag and the configurations |

   * The runtime comparison (Vidocq against Quarkus, Helidon MP, Spring Boot and Open Liberty: throughput per
     TechEmpower scenario, cold start and RSS on the JVM and native) is the Performance page of the `vidocq`
     component.
3. **vidocq.dev**: the headline chart of the runtime comparison, the same SVG committed under
   `public/images/bench/<version>/`, linking to the docs page for the detail. A blog post per release may tell the
   figures.

Grafana is never embedded in the docs: it is private, depends on Foix, and changes every night, whereas the page of a
version must show that version forever. The SVG frozen in git with the version follows the rule the diagrams already
follow.

### Rollout

1. **P0 — Machine and noise.** `BenchMontreuil01` and the window workflow; ten identical runs to get each benchmark's
   noise band. Document the Grafana stack of the Foix Portainer (version, compose) in the CI rebuild runbook.
2. **P1 — One end-to-end chain on two pilots.** A shared action `ci/run-bench` (run, fingerprint, push to
   `Vidocq/bench-results`), the importer, the schema, the data source and a first dashboard, then `ci/bench-report`
   on Chappe's existing Performance page. Pilots: **chappe** (JMH and the shootout) and **champollion** (JMH,
   `bench-results.json` already exists).
3. **P2 — Nightly** on the eleven JMH modules, with the regression alerts.
4. **P3 — L2 capacity and soak** on foy, cassini, mansart/noether and tassis.
5. **P4 — L3**: the TechEmpower application on Vidocq, Quarkus, Helidon MP, Spring Boot and Open Liberty, JVM and
   native; then the release run, its `BENCH.md` entries, its docs page and the vidocq.dev page.

## Consequences

* No figure is produced on a machine shared with CI: a bench job either gets the window or aborts.
* `CodefloeRunnerMontreuil01` and `CodefloeRunnerMontreuil02` are offline about two hours and a quarter each night
  (five and a half on Saturday); Foix alone takes CI jobs during that time.
* A release waits for the next window to get its figures, at most one night.
* The `BENCH.md` paragraph of `AGENTS.md`, and the "Ecosystem rules" summary of each repository's `AGENTS.md`, are
  updated with P2, when scheduled runs start.
* Publishing a comparison with Quarkus, Helidon, Spring Boot and Open Liberty commits us to keep its configurations
  public and to rerun it when a competitor shows a better setup.
