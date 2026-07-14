# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

This directory is a **workspace** grouping some fifteen independent Maven projects — there is **no root POM**, **no root `mvnw`**, and **no unified reactor**. Each sub-project has its own reactor, its own `.sdkmanrc`, its own `mvnw`, and most have their own `CLAUDE.md` to consult first when working inside them.

**Foundational building blocks** (no dependencies between them):

```
chappe/        Pure Java 25 HTTP/1.1 + HTTP/2 server, zero dependencies — transport layer
vauban/        CDI 4.1 Lite container, Java Modules native, zero dependencies — DI
champollion/   Jakarta JSON-P 2.1 + JSON-B 3.0 implementation, zero dependencies
```

**Jakarta EE implementations** (compose the foundational building blocks):

```
foy/           Jakarta Servlet 6.1 (transport via chappe, CDI via vauban)
cassini/       Jakarta REST 4.0 / JAX-RS (transport via chappe, CDI via vauban)
mansart/       Jakarta Data 1.0 + Jakarta Persistence 3.2, JDBC pool and transactions
```

**MicroProfile implementations**:

```
ravel/         MicroProfile Config 3.1
cervantes/     MicroProfile JWT 2.1
knock/         MicroProfile Health 4.0
dirac/         MicroProfile Metrics 5.1
heisenberg/    MicroProfile Fault Tolerance 4.1
humboldt/      MicroProfile Telemetry 2.1
cyrano/        MicroProfile Rest Client 4.0
grimm/         MicroProfile OpenAPI 4.1
```

**Assembly and tooling**:

```
vidocq/           Vidocq Runtime — orchestrator, extension mechanism, packaging
vidocq-parent/    Shared parent POM (versions, plugins, profiles)
ci/               Shared Forgejo Actions workflows
GestionProjet/    Inverted dependency graph + multi-repo impact scripts
```

Logical dependency graph: `chappe` + `vauban` + `champollion` are the foundational building blocks. `foy`, `cassini` and `mansart` compose them. The MicroProfile implementations build on `vauban` (CDI) and, depending on the case, on `cassini` or `chappe`. `vidocq` orchestrates the whole via an extension SPI inspired by Quarkus and carries the MicroProfile 7.1 certification of the assembled runtime.

**Multi-repo impact**: before modifying a foundational building block, check its consumers via `GestionProjet/graph/inverted.json` — a change in `vauban` ripples through almost the entire workspace.

## Commit conventions

- **Author and committer: the human alone.** An AI is not an author (Thaler v. Perlmutter, 2026).
- **AI assistance recorded via `Co-Authored-By:`** naming the tool (e.g. `Co-Authored-By: Claude Opus 4.x <noreply@anthropic.com>`) on the commits it helped produce. This is a **provenance record, not a claim of legal co-authorship**. Reference rule: `AI-POLICY.md`, which prevails in case of doubt.
- **Commit messages in English**, like the code, the CI and team exchanges.
- This convention applies to all sub-projects of the workspace.

## Terminology

Use **Java Modules** (or **Java module** for a single module) when referring to the Java Platform Module System. Do **not** use the abbreviation **JPMS** — in prose, identifiers, or documentation. In code identifiers, where a spaced term is impossible, use `module` (e.g. a module-path integration test is `*-module-it`, package `…moduleit`). Exception: the `jpms-guardian` agent name stays unchanged until it is renamed at its source.

## Vidocq ecosystem philosophy

Cross-cutting rules that apply to **all** sub-projects, unless an explicitly documented exception:

- **Strict Java Modules** — every module has its own `module-info.java`, minimal `exports`, no unjustified `opens`, no classpath.
- **Maximum static code generation** — prefer the **Class-File API** (JEP 484) and APT to produce at compile time what would otherwise be runtime reflection. No dynamic proxies, no ASM/Byte Buddy, no on-the-fly reflection when it can be generated at `compile`/`process-classes`. AOT-compatible (GraalVM, Leyden CDS).
- **Zero or very few external dependencies** — only the relevant Jakarta / MicroProfile specs. Any new runtime dependency must be explicitly justified in the PR.
- **Mandatory TDD** — write the test (or the TCK scenario) before the code. Red → green → refactor.
- **Arquillian** for the official Jakarta TCKs and any integration test requiring a container.
- **Virtual Threads** everywhere for I/O — `Executors.newVirtualThreadPerTaskExecutor()` by default, no platform-thread pool without a documented reason.
- **Code language is English** — all Javadoc and all comments (`//`, `/* */`, `/** */`) are written in **English**, as are symbol, test, and method names. **French** is reserved for the **Antora documentation** (`<sub-project>/docs/fr/`) and steering files (`tasks/`, agent prompts). Exchanges with the maintainer remain in French.

## Bug & performance traceability

- **Bugs**: every reproducible bug (internal issue, regression, incorrect behaviour not yet fixed) must be tracked in a `BUG.md` at the root of the relevant sub-project, with: short id, date, symptom, minimal repro, hypothesised cause, status. Updated at each investigation.
- **Benchmarks**: every performance figure (JMH, wrk, comparison vs Netty/Jetty/Parsson/Yasson/Jackson, etc.) must be recorded in a `BENCH.md` at the root of the sub-project, with: date, hardware/JVM, exact command, raw results, and delta vs the previous run. No performance figure in a README or a commit message without a corresponding entry in `BENCH.md`.

## Prerequisites (common to all sub-projects)

- **Java 25** (Temurin) + **Maven 3.9.16** — pinned via `.sdkmanrc` in each sub-project: `cd <sub-project> && sdk env`.
- All workspace POMs are on `modelVersion 4.0.0` (the workspace moved off the Maven 4 RC to the 3.9.x GA — see the history of this migration in `vidocq-parent`).
- For the official Jakarta TCKs: non-public artifacts to install into the local M2 (procedure in the README of the relevant runner).

## Working in a sub-project

Always `cd` into the sub-project first. Standard build:

```bash
./mvnw -ntp install -DskipTests   # full build
./mvnw test                        # unit tests
```

Specific TCK scripts (run from the sub-project root, never from this workspace):

- `cassini/run-official-tck-restful-4.0.sh [all|-Dtest=…]` — Jakarta REST 4.0 TCK
- `foy/run-official-tck-servlet6.1.sh [--all|-Dtest=…]` — Jakarta Servlet 6.1 TCK
- `champollion/run-official-tck-jsonp-2.1.sh`, `run-official-tck-jsonb-3.0.sh`

## Out-of-reactor TCK runners

`cassini-tck`, `foy-tck`, `champollion-tck`, `cervantes-tck`, `cyrano-tck`, `dirac-tck`, `grimm-tck`, `heisenberg-tck`, `humboldt-tck`, `knock-tck`, `ravel-tck`, `mansart-data-tck`, `mansart-transactions-tck`, `champollion-protobuf-tck` and the `vidocq-servlet-chappe-tck-runner` runner are deliberately EXCLUDED from the `<modules>` of their parent reactor and use a standalone `modelVersion 4.0.0` POM (without `<parent>`).

**History**: the initial constraint was ShrinkWrap Maven Resolver 3.3 (transitive of the official TCK) which did not parse the workspace's pre-migration `modelVersion 4.1.0`. This constraint disappeared with the move to Maven 3.9.16 + Model 4.0.0 everywhere.

**Why we keep the separation**: to decouple the runtime's release cycle from that of the official TCK (an upstream TCK bump does not trigger a runtime release, and vice versa). Any reintegration into the reactor is a dedicated effort — it changes the CI matrix, the install order, and the release decoupling. Always go through their `run-*-tck-*.sh` script, never via `mvn -pl`.

**Exception — in-reactor MP runners of the runtime (PR vidocq#19, MicroProfile 7.1 certification)**: the `vidocq` repo now embeds 8 MicroProfile TCK runners in `vidocq-runtime-integration-tests/vidocq-runtime-tck-*`, which certify **the assembled runtime** (not the isolated building blocks). They are guarded behind the Maven `tck` profile: a normal `mvn install` downloads and runs nothing; activate via `./mvnw -Ptck -pl vidocq-runtime-integration-tests/<module> test`. The per-building-block runners listed above stay out-of-reactor and remain authoritative for each implementation.

## Agents and skills available in this workspace

Defined in `.claude/agents/` and `.claude/skills/` — use proactively when the context is suitable:

- Agents: `jpms-guardian` (`module-info.java` audit), `classfile-codegen` (Class-File API + APT), `tck-runner` (out-of-reactor Jakarta TCK), `virtual-threads-reviewer` (concurrency review), `dependency-gatekeeper` (zero-dep `pom.xml` review).
- Skills: `/log-bug` (adds an entry to `<sub-project>/BUG.md`), `/log-bench` (adds an entry to `<sub-project>/BENCH.md`).

## Per-sub-project guides

Read the targeted sub-project's `CLAUDE.md` or `README.md` before modifying its code — each documents its own conventions, modules, and roadmap (milestones M2a/M2h/etc., TDD constraints, zero-dependency principles, etc.):

- **`<sub-project>/CLAUDE.md`** — conventions specific to the building block. Most sub-projects have one; it takes precedence over this file in case of local divergence.
- **`<sub-project>/README.md`** — product view and detailed architecture.
- **`<sub-project>/ROADMAP.md`** — milestones and remaining work. There is no unified roadmap: each building block carries its own, with `vidocq/ROADMAP.md` acting as the entry point for the assembled runtime.
- **`<sub-project>/BUG.md` and `BENCH.md`** — traceability (see above). Bug ids cross project boundaries when the cause lies upstream.
- **`<sub-project>/tasks/todo.md` and `tasks/lessons.md`** — current work plan and numbered lessons, to be re-read when opening a session.

At workspace level, `WORK_WITH_CLAUDE.md` complements this file: it describes **how the maintainer works** (Study/Execution registers, the "…right?" hypothesis pattern, requirement of proof before assertion) where this `CLAUDE.md` describes the **technical conventions**.
