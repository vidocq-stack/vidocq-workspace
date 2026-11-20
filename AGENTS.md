# AGENTS.md

Single source of agent instructions for the Vidocq ecosystem (Codex, Claude Code and any
other coding agent). `CLAUDE.md` only imports this file (`@AGENTS.md`) and adds the
Claude-specific tooling. Edit the rules **here**, never in `CLAUDE.md`.

The monorepo's root `AGENTS.md`, each component's `AGENTS.md` and the `AGENTS.md` of every
repository outside the monorepo carry a short summary that points back to this file, which
prevails: an agent started inside `vidocq/main/` (or any other checkout) never sees this file
on its own.

## Repository nature

This directory is a **workspace**, not a build: there is **no root POM** and **no root `mvnw`** here. mani
(`mani.yaml`) clones the repositories of the ecosystem into it; each keeps its own git repository and is
git-ignored here. All of them live on [Codefloe](https://codefloe.com/Vidocq).

**`Vidocq/vidocq`, the monorepo** (`vidocq/main/`), holds since 2026-11-20 every component, their shared parent
and the runtime: one Maven reactor, one version (in the root POM), one CI. Their former repositories are deleted.
`components.json` at its root lists each component with its PR title tag, its folder and its maturity level.

| Folder of the monorepo | What it holds |
|---|---|
| `vidocq-parent/` | The parent POM of every module; repositories outside the monorepo use it too. |
| `vidocq-components/vidocq-components-transport/` | `chappe` (pure Java 25 HTTP/1.1 + HTTP/2 server, transport). |
| `vidocq-components/vidocq-components-jakartaee/vidocq-components-jakartaee-core/` | `vauban` (CDI 4.1 Lite container, Java Modules native), `champollion` (JSON-P 2.1 + JSON-B 3.0), `cassini` (REST 4.0). |
| `vidocq-components/vidocq-components-jakartaee/vidocq-components-jakartaee-webprofile/` | `foy` (Servlet 6.1, transport via chappe, CDI via vauban), `peano` (Expression Language 6.0, on the `jakarta.el` API alone), `ibarra` (Pages 4.0, build-time page compilation, runs on `foy` with `peano`), `bodoni` (Standard Tag Library 3.0, tag handlers on the JSTL API alone; optional build-time inlining by `ibarra`), `mansart` (Data 1.0, JDBC pool and Transactions). |
| `vidocq-components/vidocq-components-microprofile/` | `ravel` (Config 3.1), `knock` (Health 4.0), `dirac` (Metrics 5.1), `heisenberg` (Fault Tolerance 4.1), `cervantes` (JWT 2.1), `cyrano` (REST Client 4.0), `humboldt` (Telemetry 2.1), `grimm` (OpenAPI 4.1). |
| `preview/vidocq-components-jakartaee/vidocq-components-jakartaee-webprofile/` | Usable and released, not complete or not certified: `kerckhoffs` (Security 4.0; see its `PLAN.md` for the open Authentication/Authorization question), `noether` (Persistence 3.2; includes the non-published `noether-validation` test/TCK stopgap). |
| `incubator/` | Built and tested, never released, not in the BOM (empty for now). |
| `vidocq-runtime/` | The runtime: orchestrator, extension SPI inspired by Quarkus, the runtime extensions, Maven plugin, CLI, dev mode, BOM, and the MicroProfile 7.2 readiness of the assembled runtime. |

A component moves to the next maturity level in one commit: its folder moves to the same group path at that level,
with the grouping POMs, `components.json` and the BOM.

**Outside the monorepo, until they move:** `erasmus` (Bean Validation) and `tassis` (Messaging 3.1) go into the
monorepo's `incubator/`; `verne` (template engine, no specification behind it) goes to the VCU organisation. Each
keeps its own reactor, `.sdkmanrc`, `mvnw` and `AGENTS.md`, its multi-repo CI (it reads `Vidocq/dep-graph` and the
workflow templates of `Vidocq/GestionProjet`), and builds against the monorepo's SNAPSHOTs (same GAVs). No module of
the monorepo depends on them.

**Support repositories:** `vidocq-docs` (Antora docs site, English-only), `pages` (vidocq.dev site), `ci` (shared
composite actions and reusable workflows), `governance` (CLA, contributor GPG keys, processes), `vidocq-benchmarks`,
`vidocq-tutorial`; `dep-graph` and `GestionProjet` serve only the three repositories above and are archived once
they have moved.

**`VidocqCodeUniverse_VCU`** hosts third-party extensions, where third-party dependencies are allowed: `template`,
`vidocq_vcu_extension_lc4jcdi`, `vidocq_vcu_extension_vaadin`, `vaadin-on-vidocq`. They build against the monorepo's
SNAPSHOTs. Setup and its open points: `docs/vcu-organisation-setup.md`.

Logical dependency graph: the foundational components (`chappe` + `vauban` + `champollion`) have no dependencies
between them; `foy`, `cassini` and `mansart` compose them; `noether` provides Persistence with optional Vauban
integration and uses Mansart's pool/transactions; `peano` stands alone on the `jakarta.el` API, and `ibarra`
composes `foy` + `peano`; `kerckhoffs` depends on the Jakarta Security API (Authentication, Authorization, Servlet,
CDI and EL APIs `provided`) and runs on `foy` + `vauban` through its runtime extension; `bodoni` depends only on the
JSTL API (Pages, Servlet and EL APIs `provided`), and its runtime extension assembles it with `ibarra` + `peano`; the
MicroProfile components build on `vauban` (CDI) and, depending on the case, on `cassini` or `chappe`; and
`vidocq-runtime` orchestrates the whole via its extension SPI.

## Changes that cross components or repositories

- **Inside the monorepo, one pull request.** A shared API change fixes every caller in the same pull request: the
  pull request build (gitflow-incremental-builder) builds and tests every module downstream of what changed, so a
  change in `vauban` rebuilds almost the whole reactor. There are no companion branches in the monorepo.
- **A change under `vauban/` goes in its own pull request, with its own test in `vauban/`** reproducing the problem
  without the module that found it. It must pass the CDI TCK and every stable dependent.
- **Short-lived branches, small pull requests.** No feature on top of a feature: what another branch needs merges
  first; incomplete is fine if nothing breaks.
- **A monorepo change that a repository outside (erasmus, tassis, verne) or a VCU extension must follow**: the
  monorepo's pull request does not build them. Merge the monorepo first, wait for `main`'s SNAPSHOT, then push the
  follower's branch again so that it builds against it. erasmus, tassis and verne keep the multi-repo rules
  (`dep-graph/graph/inverted.json`, companion branches) between themselves until they move.
- Never lift a branch protection to merge around a red build. Workflow: `docs/changes-across-repositories.md`.

## Workspace orchestration

This workspace is managed with **mani** (`mani.yaml`): each repository is cloned as `<repo>/main/` (the monorepo as
`vidocq/main/`), with optional sibling worktrees `<repo>/<branch>/` (directory name == branch name), one per task:
`vidocq/<branch>/` for monorepo work. Handy commands: `mani run -a status`, `mani run -a sync-all`,
`mani run -a install-hooks` (wires the shared DCO sign-off hooks), `BRANCH=… BASE=origin/main mani run wt-add -p
vidocq`. `mani run`/`mani exec` always need a target (`-a`/`-t`/`-p`). Full guide:
`docs/working-with-mani-and-worktrees.md`.

## Commit and pull request conventions

These rules apply to every repository of the ecosystem.

- **Work on a branch, open a pull request.** `main` is protected in every repo: it requires signed commits and green `pr-validate` / `governance-checks` checks. Never push to `main`.
- **Signed and signed-off commits** — `git commit -S -s`: a GPG signature (key registered in `Vidocq/governance`, CLA signed) and a DCO `Signed-off-by` trailer. The shared `.githooks` auto-append and enforce the sign-off.
- **Conventional Commits, in English**, with the project ticket when there is one (e.g. `fix(core): … (#123)`).
- **Monorepo pull request titles** — `[WIP]` first while not ready (Forgejo then blocks the merge button), one tag per component touched (`components.json`: `[VAUBAN]`, `[RUNTIME]`, …) plus `[BOM]`, `[TCK]`, `[BUILD]`, `[CI]`, `[DOCS]` where they apply, then the Conventional Commits title: `[WIP] [NOETHER] fix(persistence): flush order on nested transactions (#123)`. Details: the monorepo's `AGENTS.md`.
- **Monorepo merges are manual**: the maintainer merges; an agent reports a pull request ready and does not arm a merge.
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
  - **Jakarta platform APIs** (CDI, Inject, Interceptor, Annotation, REST, Servlet, ...) are `provided`. Exception: a brick ships the API of the spec it implements, at `compile` scope (Vauban CDI, Champollion JSON-P/JSON-B, Cassini REST, Foy Servlet, Peano EL, Ibarra Pages, Mansart Data/Transactions, Noether Persistence, Erasmus Validation, Tassis Messaging).
  - **The spec API a brick implements reaches the application transitively** — a MicroProfile brick ships its spec API through its repackaged named module (`ravel-mp-config-api`, `dirac-mp-metrics-api`, `heisenberg-mp-ft-api`, ...), a `compile` dependency of its `*-api`, and the upstream `microprofile-*-api` jar stays `provided` (Grimm takes the upstream OpenAPI jar at `compile` directly, as it already has a `module-info`). The application never declares that API: Getting started snippets list the brick only. Never tell users to add the upstream MicroProfile API jar — it has no `module-info`, and its automatic module duplicates the repackaged one on the module path.
  - **Other APIs** (JSON-P, JSON-B, MicroProfile Config, OpenTelemetry, ...) may be `provided` or `compile`. Every API the brick leaves `provided` must be brought by its Vidocq runtime extension, together with an implementation: an application with that extension alone must start (for example Knock leaves JSON-P `provided`, and the Health extension brings `champollion-jsonp`).
  - **Never another brick's implementation** — no `champollion-jsonb` in Cassini, no `ravel-core` in Heisenberg. The extension declares it. Engine adapters (`*-cdi-vauban`, `cassini-chappe`) are the documented exception until each brick has a container-neutral integration.
  - **Documented and tested** — each brick's Reference page has a `WARNING` block "Deploying on an application server": the server features to keep off, the jars to exclude, the `<exclusions>` to copy. The brick's `<brick>-it-openliberty` module builds its WAR with exactly those dependencies, so the block is tested.
- **A build compatible extension works at build, and only there** — `vidocq:generate` runs the build compatible extensions of an application once and freezes what they did; the container start loads that record instead of running them (Vidocq/vauban#288). In a packaged application an extension does not run at all, so a brick's `BuildCompatibleExtension` (guide: `docs/writing-a-build-compatible-extension.md`):
  - **computes from the classes of the deployment only** — no configuration value, environment variable, outside file or network resource in a phase: at build they are the build machine's.
  - **checks the start environment in an observer of `Startup`** that throws a `DeploymentException` (a required configuration value, a key that must parse), fed by `withParam` data collected at build: Ravel's `ConfigStartCheck`, Cervantes's `JwtConfigurationCheck`.
  - **adds annotations, never removes them**, and carries data in parameters, not in fields: a removal cannot be frozen: the extension that removes runs again at each start, alone, and the others stay frozen (Vidocq/vauban#343), so its work is still done at every start.
  - **asks `ExtensionPhase.isBuildTime()` only as a last resort** — an extension that asks runs again at each start; put that phase in a class of its own.
  - **reaches the processor path through the `-codegen` bundle of its Vidocq extension**, which adds its own beans with `addHostBean`, never `addBeanClass`.
  - **lists in `@io.vidocq.vauban.api.ClientProxies` every interface it registers as a synthetic bean of a normal scope** (`@ApplicationScoped`, `@TransactionScoped`, ...). The reason: Vauban generates a client proxy at build from the classes it compiles, and a synthetic bean has none. The freeze records its descriptor, not a proxy, and a deployment that runs its extensions at start has no build step. Without the list, the container builds a `java.lang.reflect.Proxy` at every start: every call goes through reflection, the boot is slower, nothing runs ahead of time, and every application prints the `RUNTIME CODE GENERATION FALLBACK` warning (Vauban BUG-20261113-19: Noether's `EntityManager` and `EntityManagerFactory`).
    - **where**: on a class of a module compiled with `vauban-processor` that provides its `_VaubanComponents`. That is the `*-cdi-vauban` extension, or, for a container-neutral brick, its Vidocq runtime extension (`NoetherPersistenceExtension`).
    - **what**: public interfaces only, no class, no `@Dependent` bean.
  - **is tested both ways** — the extensions run at start (TCK, Weld, Open Liberty), and frozen: `extensionsAtStart().ranAtStart()` is empty, the startup report says `cdi extensions  N extensions frozen at build`, and an invalid environment still stops the start.
- **Mandatory TDD** — write the test (or the TCK scenario) before the code. Red → green → refactor.
- **Arquillian** for the official Jakarta TCKs and any integration test requiring a container.
- **Virtual Threads** everywhere for I/O — `Executors.newVirtualThreadPerTaskExecutor()` by default, no platform-thread pool without a documented reason.
- **English is the official project language** — code, Javadoc, comments (`//`, `/* */`, `/** */`), symbol/test/method names, commit messages, CI, issues/PRs, and **every Markdown file, including steering files (`tasks/`, studies, plans, agent prompts)**. The **Antora documentation is English-only** (`docs/en`, vidocq-docs ADR 0004 — the `docs/fr/` mirrors were removed). Exchanges with the maintainer remain in French.

## Bug & performance traceability

- **Bugs**: every reproducible bug (internal issue, regression, incorrect behaviour not yet fixed) must be tracked in a `BUG.md` in the folder of the relevant component (monorepo) or at the root of the relevant repository, with: short id, date, symptom, minimal repro, hypothesised cause, status. Updated at each investigation. A bug id is unique across the monorepo and the repositories around it.
- **Benchmarks**: every performance figure (JMH, wrk, comparison vs Netty/Jetty/Parsson/Yasson/Jackson, etc.) must be recorded in a `BENCH.md` in the folder of the component (or at the root of the repository), with: date, hardware/JVM, exact command, raw results, and delta vs the previous run. No performance figure in a README or a commit message without a corresponding entry in `BENCH.md`.

## Code quality

SonarQube analyses the monorepo and the Java repositories outside it (`erasmus` is not wired yet); the tools plugged into the analysis, their
settings and the pitfalls met so far are in `QUALITY.md`. The monorepo is one SonarQube project, key
`the-vidocq-project`: `pr-validate` analyses the modules holding a changed file, from its own build, in blocking
mode (a red gate fails the pull request), and the nightly build analyses `main`. A repository outside the monorepo
has its own project, key `vidocq-<repository>`, in report mode: a red gate does not block a merge, but it turns
`main`'s gate red. Read the SonarQube comment of a pull request before merging it, and leave no new issue behind.

**An agent runs the SonarQube analysis on its changes before it pushes them**, and fixes every new issue first.
This applies to the first push of a pull request and to every later push that changes code. A push sent back by the
SonarQube comment costs a full CI round, and so does the fix after it. The server accepts branch analyses (community
branch plugin). From the monorepo checkout, with a personal token (*My Account → Security*) in `SONAR_TOKEN`:

```bash
./mvnw -ntp -Pquality verify     # what the branch changed and its dependents, with JaCoCo
./mvnw -ntp -Pquality -Dgib.disable=true -pl <modules> \
  org.sonarsource.scanner.maven:sonar-maven-plugin:5.8.0.7211:sonar \
  -Dsonar.host.url=https://sonar.vidocq.dev -Dsonar.token="$SONAR_TOKEN" \
  -Dsonar.projectKey=the-vidocq-project -Dsonar.branch.name=<branch> -Dsonar.newCode.referenceBranch=main
```

`<modules>` is what the `sonar-scope` step of the monorepo's `.forgejo/workflows/pr.yml` computes: the modules
holding a changed file and every aggregator above them up to `.` (the scanner refuses a reactor without them). In a
repository outside the monorepo, run the same two commands from its checkout without `-Dgib.disable=true -pl …`,
with `-Dsonar.projectKey=vidocq-<repository>`.

Then read the new issues and the gate of that branch, and fix them before the push:
`https://sonar.vidocq.dev/project/issues?id=the-vidocq-project&branch=<branch>&resolved=false&inNewCodePeriod=true`
(`id=vidocq-<repository>` outside the monorepo).
The gate also counts duplicated lines in new code (3 % at most): code repeated across sibling classes fails it
even without an issue.

## Prerequisites (common to all projects)

- **Java 25** (Temurin) + **Maven**, pinned via `.sdkmanrc` in each repository (Maven 3.10.0 in the monorepo): `cd vidocq/main && sdk env install`. Always build with the repository's `./mvnw`.
- All POMs are on `modelVersion 4.0.0` (the workspace moved off the Maven 4 RC to the 3.x GA — see the history of this migration in `vidocq-parent`).
- For the official Jakarta TCKs: non-public artifacts to install into the local M2 (procedure in the README of the relevant runner).

## Working in the monorepo

Always `cd` into the monorepo checkout first (`vidocq/main/` or a worktree `vidocq/<branch>/`) and build from its
root, with its wrapper:

```bash
./mvnw install                              # what the branch changed and its dependents (gitflow-incremental-builder)
./mvnw -pl <module path> -am verify         # one module and what it needs
./mvnw install -Dgib.disable=true           # everything
./mvnw install -P '!incubator'              # what a release builds
```

The incremental build compares with `origin/main`: fetch first. A component depends on another at
`${project.version}`. **Never install into `~/.m2` from a branch build**: add
`-Dmaven.repo.local=<scratch>/m2 -Dmaven.repo.local.tail=$HOME/.m2/repository`, or stop at `verify`. A repository
outside the monorepo builds on its own: `cd <repo>/main && ./mvnw -ntp install`.

## TCK runners

A pull request runs no TCK. The `TCK nightly` workflow of the monorepo (`.forgejo/workflows/tck-nightly.yml`) runs
them once a day, on demand (dispatched on a branch, with the component tags, e.g. `CASSINI,FOY`) and for a release:
a pull request that needs one dispatches it on its branch. What it runs for a component is named in that
component's root POM (`ci.tck.modules`, each run with `-Ptck`; `ci.tck.command`, run in its folder).

Locally, the runners stay behind each component's **`tck` Maven profile**: a normal build neither downloads nor
runs anything TCK-related. The entry point is the component's script, run from its folder
(`run-official-tck-*.sh`, e.g. `cassini/run-official-tck-restful-4.0.sh [all|-Dtest=…]`,
`foy/run-official-tck-servlet6.1.sh [--all|-Dtest=…]`, `champollion/run-official-tck-jsonp-2.1.sh`,
`vauban/run-tck.sh`), or `./mvnw -Ptck[,tck-official] -pl <runner path> test` from the root.

- **In-reactor under `-Ptck`**: `vauban-tck-runner`, `vauban-atinject-tck-runner`, `cassini-tck`, `champollion-tck`, `foy-tck`, `peano-tck`, `ibarra-tck`, `bodoni-tck`, `ravel-tck`, `knock-tck`, `dirac-tck`, `heisenberg-tck`, `cervantes-tck`, `cyrano-tck`, `humboldt-tck`, `kerckhoffs-tck`.
- **Standalone POMs** (no `<parent>`), run with `-f` by their component's `ci.tck.command` or script: `grimm-tck`, `mansart-data-tck`, `mansart-transactions-tck`, `champollion-protobuf-tck`, `noether-jpa-tck`, `noether-validation-tck`. Check the component's `pom.xml` before asserting either state.
- **Runtime runners**: `vidocq-runtime/vidocq-runtime-integration-tests/vidocq-runtime-tck-*` certify **the assembled runtime** (not the isolated components), behind `tck` too: `./mvnw -Ptck -pl vidocq-runtime/vidocq-runtime-integration-tests/<module> test`. The per-component runners remain authoritative for each implementation.
- **History**: at the v0.2.0 tag every runner was out of its reactor (ShrinkWrap Maven Resolver could not parse `modelVersion 4.1.0`); the Antora docs of the 0.2.0 line reflect that state: do not "fix" those pages.

erasmus and tassis keep their own TCK scripts (`erasmus-tck` in-reactor; `tassis/run-official-tck-messaging-3.1.sh`).

## Per-component guides

Read the targeted component's `AGENTS.md` and `README.md` before modifying its code — each documents its own
conventions, modules and roadmap. In the monorepo they sit in the component's folder (`<component path>/AGENTS.md`,
paths in `components.json`); outside it, at the repository root.

- **`AGENTS.md`** — conventions specific to the component. It takes precedence over this file in case of local divergence.
- **`README.md`** — product view and detailed architecture.
- **`ROADMAP.md`** or **`PLAN.md`** — milestones and remaining work (`PLAN.md` is the design of record for components still in design, e.g. kerckhoffs, bodoni). There is no unified roadmap: each component carries its own, with `vidocq-runtime/ROADMAP.md` acting as the entry point for the assembled runtime.
- **`BUG.md` and `BENCH.md`** — traceability (see above). Bug ids cross component boundaries when the cause lies upstream.
- **`tasks/todo.md` and `tasks/lessons.md`**, where a component has them — current work plan and numbered lessons, to be re-read when opening a session.

At workspace level, `WORK_WITH_CLAUDE.md` complements this file: it describes **how the maintainer works** (Study/Execution registers, the "…right?" hypothesis pattern, requirement of proof before assertion) where this file describes the **technical conventions**. It applies to any agent, not only Claude.
