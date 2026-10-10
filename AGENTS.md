# AGENTS.md

Single source of agent instructions for the Vidocq ecosystem (Codex, Claude Code and any
other coding agent). `CLAUDE.md` only imports this file (`@AGENTS.md`) and adds the
Claude-specific tooling. Edit the rules **here**, never in `CLAUDE.md`.

Each project repo carries its own `AGENTS.md` with a short, self-contained "Ecosystem
rules" summary that points back to this file: in the mani layout every project is its own
git repository, so an agent started inside `<repo>/main/` never sees this file on its own.

## Repository nature

This directory is a **workspace** grouping the independent Maven projects of the Vidocq ecosystem — there is **no root POM**, **no root `mvnw`**, and **no unified reactor**. Each project has its own reactor, its own `.sdkmanrc`, its own `mvnw`, and its own `AGENTS.md` / `CLAUDE.md` to consult first when working inside it.

The ecosystem spans several groups of repositories (all under the `Vidocq` organisation on [Codefloe](https://codefloe.com/Vidocq)):

- **Foundational bricks** (no dependencies between them): `chappe` (pure Java 25 HTTP/1.1 + HTTP/2 server — transport), `vauban` (CDI 4.1 Lite container, Java Modules native — DI), `champollion` (Jakarta JSON-P 2.1 + JSON-B 3.0).
- **Jakarta EE layers** (compose the bricks): `foy` (Servlet 6.1 — transport via chappe, CDI via vauban), `cassini` (REST 4.0 / JAX-RS), `mansart` (Jakarta Data 1.0 + Persistence 3.2 — JDBC pool and transactions), `erasmus` (Bean Validation), `tassis` (Messaging 3.1).
- **Jakarta EE web tier** (in design): `peano` (Jakarta Expression Language 6.0 — depends on nothing beyond the `jakarta.el` API), `ibarra` (Jakarta Pages 4.0 — build-time page compilation, runs on `foy` with `peano` as the default EL provider).
- **MicroProfile bricks:** `ravel` (Config 3.1), `knock` (Health 4.0), `dirac` (Metrics 5.1), `heisenberg` (Fault Tolerance 4.1), `cervantes` (JWT 2.1), `cyrano` (REST Client 4.0), `humboldt` (Telemetry 2.1), `grimm` (OpenAPI 4.1).
- **Runtime & support:** `vidocq` (the runtime — orchestrator, extension mechanism, packaging), `vidocq-parent` (shared parent POM), `vidocq-docs` (Antora docs site, English-only), `pages` (vidocq.dev site), `ci` (CI configuration & pipelines), `governance` (CLA, contributor GPG keys, processes), `GestionProjet` (inverted dependency graph + multi-repo impact scripts).

Logical dependency graph: the foundational bricks (`chappe` + `vauban` + `champollion`) have no dependencies between them; `foy`, `cassini` and `mansart` compose them; `peano` stands alone on the `jakarta.el` API, and `ibarra` composes `foy` + `peano`; the MicroProfile bricks build on `vauban` (CDI) and, depending on the case, on `cassini` or `chappe`; and `vidocq` orchestrates the whole via an extension SPI inspired by Quarkus and carries the MicroProfile 7.1 certification of the assembled runtime.

**Multi-repo impact**: before modifying a foundational brick, check its consumers via `GestionProjet/graph/inverted.json` — a change in `vauban` ripples through almost the entire workspace.

## Workspace orchestration

This workspace is managed with **mani** (`mani.yaml`): each project is cloned as `<repo>/main/`, with optional sibling worktrees `<repo>/<branch>/` (directory name == branch name). Handy commands: `mani run -a status`, `mani run -a sync-all`, `mani run -a install-hooks` (wires the shared DCO sign-off hooks), `BRANCH=… mani run wt-add -p <repo>`. `mani run`/`mani exec` always need a target (`-a`/`-t`/`-p`). Full guide: `docs/working-with-mani-and-worktrees.md`.

## Commit and pull request conventions

These rules apply to every repository of the ecosystem.

- **Work on a branch, open a pull request.** `main` is protected in every repo: it requires signed commits and green `pr-validate` / `governance-checks` checks. Never push to `main`.
- **Signed and signed-off commits** — `git commit -S -s`: a GPG signature (key registered in `Vidocq/governance`, CLA signed) and a DCO `Signed-off-by` trailer. The shared `.githooks` auto-append and enforce the sign-off.
- **Conventional Commits, in English**, with the project ticket when there is one (e.g. `fix(core): … (#123)`).
- **Author and committer: the human alone.** An AI is not an author (Thaler v. Perlmutter, 2026).
- **AI assistance recorded via `Co-Authored-By:`** naming the tool (e.g. `Co-Authored-By: Claude Opus 4.x <noreply@anthropic.com>`, or the Codex equivalent) on the commits it helped produce. This is an honest **provenance record, not a claim of legal co-authorship**, consistent with the project's "AI-assisted" positioning. Reference rule: `AI-POLICY.md`, which prevails in case of doubt.

## Terminology

Use **Java Modules** (or **Java module** for a single module) when referring to the Java Platform Module System. Do **not** use the abbreviation **JPMS** — in prose, identifiers, or documentation. In code identifiers, where a spaced term is impossible, use `module` (e.g. a module-path integration test is `*-module-it`, package `…moduleit`).

## Vidocq ecosystem philosophy

Cross-cutting rules that apply to **all** projects, unless an explicitly documented exception:

- **Strict Java Modules** — every module has its own `module-info.java`, minimal `exports`, no unjustified `opens`, no classpath.
- **Maximum static code generation** — prefer the **Class-File API** (JEP 484) and APT to produce at compile time what would otherwise be runtime reflection. No dynamic proxies, no ASM/Byte Buddy, no on-the-fly reflection when it can be generated at `compile`/`process-classes`. AOT-compatible (GraalVM, Leyden CDS).
- **Zero external dependency for what ships** — published libraries depend only on the Jakarta / MicroProfile specs they implement. The rule targets the **runtime**: build tooling (Maven plugins, packaging goals) runs on the build machine and never inside the application, so it may take a dependency when that avoids rewriting work already done elsewhere. Two conditions: the dependency is justified in the PR, and it is **named in the reference page of the module concerned**.
- **A brick depends on APIs; the Vidocq runtime extension assembles** — a brick does not pick the implementations it runs on: its Vidocq runtime extension does, and so does an application server or an application that uses the brick alone. So the brick runs unchanged under Vidocq, on another CDI container, or in a WAR on a server (vidocq-workspace#15, #17):
  - **Jakarta platform APIs** (CDI, Inject, Interceptor, Annotation, REST, Servlet, ...) are `provided`. Exception: a brick ships the API of the spec it implements (Vauban CDI, Cassini REST, Foy Servlet, Champollion JSON-P/JSON-B, Mansart Persistence/Transactions/Data).
  - **Other APIs** (JSON-P, JSON-B, MicroProfile Config, OpenTelemetry, ...) may be `provided` or `compile`. Every API the brick leaves `provided` must be brought by its Vidocq runtime extension, together with an implementation: an application with that extension alone must start (for example Knock leaves JSON-P `provided`, and the Health extension brings `champollion-jsonp`).
  - **Never another brick's implementation** — no `champollion-jsonb` in Cassini, no `ravel-core` in Heisenberg. The extension declares it. Engine adapters (`*-cdi-vauban`, `cassini-chappe`) are the documented exception until each brick has a container-neutral integration.
  - **Documented and tested** — each brick's Reference page has a `WARNING` block "Deploying on an application server": the server features to keep off, the jars to exclude, the `<exclusions>` to copy. The brick's `<brick>-it-openliberty` module builds its WAR with exactly those dependencies, so the block is tested.
- **Mandatory TDD** — write the test (or the TCK scenario) before the code. Red → green → refactor.
- **Arquillian** for the official Jakarta TCKs and any integration test requiring a container.
- **Virtual Threads** everywhere for I/O — `Executors.newVirtualThreadPerTaskExecutor()` by default, no platform-thread pool without a documented reason.
- **English is the official project language** — code, Javadoc, comments (`//`, `/* */`, `/** */`), symbol/test/method names, commit messages, CI, issues/PRs, and **every Markdown file, including steering files (`tasks/`, studies, plans, agent prompts)**. The **Antora documentation is English-only** (`docs/en`, vidocq-docs ADR 0004 — the `docs/fr/` mirrors were removed). Exchanges with the maintainer remain in French.

## Bug & performance traceability

- **Bugs**: every reproducible bug (internal issue, regression, incorrect behaviour not yet fixed) must be tracked in a `BUG.md` at the root of the relevant project, with: short id, date, symptom, minimal repro, hypothesised cause, status. Updated at each investigation.
- **Benchmarks**: every performance figure (JMH, wrk, comparison vs Netty/Jetty/Parsson/Yasson/Jackson, etc.) must be recorded in a `BENCH.md` at the root of the project, with: date, hardware/JVM, exact command, raw results, and delta vs the previous run. No performance figure in a README or a commit message without a corresponding entry in `BENCH.md`.

## Prerequisites (common to all projects)

- **Java 25** (Temurin) + **Maven 3.9.16** — pinned via `.sdkmanrc` in each project: `cd <repo>/main && sdk env`.
- All workspace POMs are on `modelVersion 4.0.0` (the workspace moved off the Maven 4 RC to the 3.9.x GA — see the history of this migration in `vidocq-parent`).
- For the official Jakarta TCKs: non-public artifacts to install into the local M2 (procedure in the README of the relevant runner).

## Working in a project

Always `cd` into the project checkout first (`<repo>/main/` or one of its worktrees). Standard build:

```bash
./mvnw -ntp install -DskipTests   # full build
./mvnw test                        # unit tests
```

Specific official-TCK scripts (run from the project checkout root, never from this workspace):

- `cassini`: `run-official-tck-restful-4.0.sh [all|-Dtest=…]` — Jakarta REST 4.0 TCK
- `foy`: `run-official-tck-servlet6.1.sh [--all|-Dtest=…]` — Jakarta Servlet 6.1 TCK
- `champollion`: `run-official-tck-jsonp-2.1.sh`, `run-official-tck-jsonb-3.0.sh`
- `tassis`: `run-official-tck-messaging-3.1.sh`

## TCK runners — in-reactor behind the `tck` profile

Since the TCK harmonisation (summer 2026, after the 0.2.0 release, following the pattern of the `vidocq-runtime-tck-*` runners of PR vidocq#19), most per-brick runners are back **inside** their brick's reactor, guarded by the **`tck` Maven profile**: a normal `mvn install` neither downloads nor runs anything TCK-related. Activate via the brick's `run-*-tck-*.sh` script (recommended entry point) or `./mvnw -Ptck[,tck-official] -pl <runner> test`.

- **In-reactor under `-Ptck`**: `cassini-tck`, `foy-tck`, `champollion-tck`, `cervantes-tck`, `cyrano-tck`, `dirac-tck`, `heisenberg-tck`, `humboldt-tck`, `knock-tck`, `ravel-tck`, `erasmus-tck`, and the new `peano-tck` / `ibarra-tck` (in-reactor from day one). `vauban-tck-runner` + `vauban-atinject-tck-runner` are in the vauban reactor too.
- **Still out-of-reactor** (standalone `modelVersion 4.0.0` POM, without `<parent>`): `grimm-tck`, `mansart-data-tck`, `mansart-transactions-tck`, `champollion-protobuf-tck`, and the `vidocq-servlet-chappe-tck-runner` runner.
- **At the v0.2.0 tag**, every runner was still out-of-reactor — the Antora docs of the 0.2.0 line reflect that state; do not "fix" those pages towards the in-reactor state.

**History**: the initial constraint was ShrinkWrap Maven Resolver 3.3 (transitive of the official TCK) which did not parse the workspace's pre-migration `modelVersion 4.1.0`; it disappeared with Maven 3.9.16 + Model 4.0.0. The remaining separation (grimm / mansart / protobuf) keeps the runtime release cycle decoupled from the official TCK — check the `pom.xml` of the relevant reactor before asserting either state for a brick.

**Runtime MicroProfile runners (PR vidocq#19, MicroProfile 7.1 certification)**: the `vidocq` repo embeds 8 MicroProfile TCK runners in `vidocq-runtime-integration-tests/vidocq-runtime-tck-*`, which certify **the assembled runtime** (not the isolated bricks). They are guarded behind the `tck` profile too: activate via `./mvnw -Ptck -pl vidocq-runtime-integration-tests/<module> test`. The per-brick runners listed above remain authoritative for each implementation.

## Per-project guides

Read the targeted project's `AGENTS.md` (or `CLAUDE.md`) and `README.md` before modifying its code — each documents its own conventions, modules, and roadmap (milestones, TDD constraints, zero-dependency principles, etc.):

- **`<repo>/AGENTS.md`** — conventions specific to the brick. It takes precedence over this file in case of local divergence.
- **`<repo>/README.md`** — product view and detailed architecture.
- **`<repo>/ROADMAP.md`** or **`PLAN.md`** — milestones and remaining work (`PLAN.md` is the design of record for bricks still in design, e.g. peano, ibarra). There is no unified roadmap: each brick carries its own, with `vidocq/ROADMAP.md` acting as the entry point for the assembled runtime.
- **`<repo>/BUG.md` and `BENCH.md`** — traceability (see above). Bug ids cross project boundaries when the cause lies upstream.
- **`<repo>/tasks/todo.md` and `tasks/lessons.md`** — current work plan and numbered lessons, to be re-read when opening a session.

At workspace level, `WORK_WITH_CLAUDE.md` complements this file: it describes **how the maintainer works** (Study/Execution registers, the "…right?" hypothesis pattern, requirement of proof before assertion) where this file describes the **technical conventions**. It applies to any agent, not only Claude.
