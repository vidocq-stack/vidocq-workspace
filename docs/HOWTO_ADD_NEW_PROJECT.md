# HOWTO — Add a new project to the Vidocq ecosystem

> Moved here on 2026-10-05 from `GestionProjet/HOWTO_ADD_NEW_PROJECT.md` (that repository was deleted from
> the forge) and translated from French. The content is unchanged: the paths and steps that mention
> `GestionProjet` describe the dependency-graph mechanism as it was written.

This guide describes the complete procedure for integrating a **new producer sub-project** into the
Vidocq ecosystem (e.g. `cyrano`, `knock`, future ones). It covers the repository structure conventions,
the mandatory meta files (including the Claude / agents / skills files), the Maven wiring on the
`vidocq/vidocq` side, and the registration in the `GestionProjet` graph.

> **Audience**: Vidocq maintainers, and AI agents that must bootstrap a new module without surprises.
> Referenced by the `claude` agent and the `init` skill.

---

## 0. Prerequisites & naming

- **GroupId**: `io.vidocq.<short-name>` (e.g. `io.vidocq.cyrano`). The `groupId` must match the regex
  `^io\.vidocq(\..+)?$`: it is the filter of the GestionProjet graph (see `data/schema.json`).
- **Forgejo repository name**: `vidocq/<short-name>` (e.g. `vidocq/cyrano`). Strict whitelist on the
  GestionProjet side.
- **Name of the Maven property** in consumers: `<short-name>.version` (e.g. `<cyrano.version>`). This
  property has the same name as the short repository name; otherwise `ci/build-impacted` cannot rewrite
  the PR version of the upstream dependency (`versions:set-property <short-name>.version=<PR>`) during an
  upstream PR.
- **Initial version**: `0.2.0` by default (Mansart is the historical exception at `1.0.0-SNAPSHOT`).
- **Java / Maven**: Java 25 Temurin + Maven 3.9.16, pinned via `.sdkmanrc`.

---

## 1. Structure of the producer repository

Minimal expected tree (take `vauban/`, `chappe/`, `cyrano/` as models):

```
<short-name>/
├── .sdkmanrc                  ← java=25-tem, maven=3.9.16
├── .gitignore                 ← target/, *.iml, .idea/, etc.
├── LICENSE                    ← EPL-2.0 OR EUPL-1.2 OR GPL-2.0-or-later (ecosystem consistency)
├── README.md                  ← product view: modules, prerequisites, commands
├── CLAUDE.md                  ← guide specific to Claude Code in this repository
├── AGENTS.md (optional)       ← inventory of the agents available in .claude/agents/
├── ROADMAP.md (optional)      ← milestones M1/M2/Mx
├── TCK.md (optional)          ← official TCK procedure, if applicable
├── BUG.md                     ← bug traceability (see the workspace CLAUDE.md)
├── BENCH.md                   ← benchmark traceability (same)
├── pom.xml                    ← root POM (Model 4.1.0, root="true", no <parent>)
├── <name>-api/                ← public API
├── <name>-core/               ← standalone implementation
├── <name>-cdi-vauban/         ← CDI integration through Vauban (if applicable)
├── <name>-tck/                ← official TCK, OUTSIDE the reactor (see §5)
├── .claude/                   ← local Claude Code configuration
│   ├── agents/                ← specialised agents (jpms-guardian, etc.)
│   └── skills/                ← skills (/log-bug, /log-bench)
└── .forgejo/workflows/        ← CI/CD (see §4)
    ├── ci.yml                 ← build + deploy snapshots on push to main
    ├── pr.yml                 ← PR validation in a single job (local build + ci/build-impacted)
    └── update-dep-graph.yml   ← GestionProjet maintenance
```

### 1.1 Root POM (Model 4.1.0)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.1.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.1.0 http://maven.apache.org/xsd/maven-4.1.0.xsd"
         root="true">
    <modelVersion>4.1.0</modelVersion>

    <groupId>io.vidocq.<short-name></groupId>
    <artifactId><short-name>-parent</artifactId>
    <version>0.2.0</version>
    <packaging>pom</packaging>
    <name><Short-Name></name>
    <description>… short description mentioning zero-dep / Java Modules / virtual threads …</description>

    <subprojects>
        <subproject><short-name>-api</subproject>
        <subproject><short-name>-core</subproject>
        <subproject><short-name>-cdi-vauban</subproject>
        <!-- NOT the tck: deliberately outside the reactor -->
    </subprojects>

    <properties>
        <maven.compiler.release>25</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <!-- versions of the upstream Vidocq deps (Vauban, Chappe, etc.) if this is a consumer -->
    </properties>

    <distributionManagement>
        <repository>
            <id>vidocq-releases</id>
            <url>https://repo.vidocq.dev/releases</url>
        </repository>
        <snapshotRepository>
            <id>vidocq-snapshots</id>
            <url>https://repo.vidocq.dev/snapshots</url>
        </snapshotRepository>
    </distributionManagement>
</project>
```

⚠️ **Model 4.1.0**: child modules only declare `<parent>`, with no explicit version. The `<name>-tck`
module stays a standalone **Model 4.0.0** and **declares no `<parent>`** (ShrinkWrap Resolver 3.3 is
incompatible with Model 4.1.0; see the workspace CLAUDE.md).

---

## 2. Mandatory meta files

### 2.1 `.sdkmanrc`

```
java=25-tem
maven=3.9.16
```

### 2.2 `CLAUDE.md` (minimal template)

```markdown
# CLAUDE.md — <Short-Name>

This file complements the Vidocq workspace `CLAUDE.md`. Read it first, before any change in this
repository.

## Identity
- groupId: `io.vidocq.<short-name>`
- implemented spec: <e.g. MicroProfile Rest Client 4.0>
- philosophy: zero-dep, strict Java Modules, virtual threads, static codegen

## Modules
| Module | Role |
|---|---|
| `<name>-api` | … |
| `<name>-core` | … |
| `<name>-cdi-vauban` | … |
| `<name>-tck` | official TCK, outside the reactor |

## Commands
- `./mvnw -ntp install -DskipTests`: full build
- `./mvnw test`: unit tests
- `./run-official-tck-<spec>.sh`: official TCK (if applicable)

## Specific constraints
- … (known limitations, exceptions to the zero-dep philosophy, etc.)

## Traceability
- Bugs: see `BUG.md`
- Benchmarks: see `BENCH.md`
```

### 2.3 `BUG.md` and `BENCH.md`

Initialise them when the repository is created, even empty (otherwise the `/log-bug` and `/log-bench`
skills create them on the fly). The format is documented in the workspace `CLAUDE.md`.

### 2.4 `.claude/` (local Claude Code configuration)

```
.claude/
├── agents/      ← copy the relevant agents from the workspace
│                  (jpms-guardian, classfile-codegen, virtual-threads-reviewer,
│                   dependency-gatekeeper, tck-runner)
├── skills/      ← copy the /log-bug and /log-bench skills
└── settings.local.json (optional, not committed by default)
```

Reference the agents relevant to this sub-project; no need to include what is not used (a project
without a TCK does not need `tck-runner`).

---

## 3. Wiring on the `vidocq/vidocq` side

The `vidocq` orchestrator consumes the sub-project through an extension wrapper. Four places to change
in `vidocq/vidocq/`:

### 3.1 Property in the parent POM (`vidocq/pom.xml`)

```xml
<properties>
    …
    <<short-name>.version>0.2.0</<short-name>.version>
    …
</properties>
```

### 3.2 Entries in the `<dependencyManagement>`

For **each consumed artefact** (the Vauban pattern: api + core + cdi-vauban + indexer +
classloader-spi are all listed explicitly):

```xml
<dependency>
    <groupId>io.vidocq.<short-name></groupId>
    <artifactId><short-name>-api</artifactId>
    <version>${<short-name>.version}</version>
</dependency>
<dependency>
    <groupId>io.vidocq.<short-name></groupId>
    <artifactId><short-name>-core</artifactId>
    <version>${<short-name>.version}</version>
</dependency>
<!-- etc. -->

<!-- THEN the Vidocq extension wrapper itself: -->
<dependency>
    <groupId>io.vidocq.runtime</groupId>
    <artifactId>vidocq-runtime-<short-name>-extension</artifactId>
    <version>${project.version}</version>
</dependency>
```

> ⚠️ **Anti-pattern spotted in the `add-cyrano` PR**: only `vidocq-runtime-cyrano-rest-client-extension`
> is in the dependencyManagement; the cyrano-api/core/cdi-vauban artefacts are consumed directly through
> `${cyrano.version}` in the extension's pom. It works, but it is inconsistent with the Vauban pattern
> (which lists *all* its artefacts). To stay homogeneous, always add every upstream artefact to the
> dependencyManagement.

### 3.3 Creating the wrapper module `vidocq-runtime-<short-name>-extension`

Under `vidocq-runtime-extensions/vidocq-runtime-<short-name>-extension/`, a Model 4.1.0 POM:

```xml
<project xmlns="http://maven.apache.org/POM/4.1.0" …>
    <modelVersion>4.1.0</modelVersion>
    <parent>
        <groupId>io.vidocq.runtime</groupId>
        <artifactId>vidocq-runtime-extensions</artifactId>
    </parent>
    <artifactId>vidocq-runtime-<short-name>-extension</artifactId>
    <name>Vidocq :: Core Extensions :: <Description>></name>
    <description>Maven/Java Modules wrapper that enables <Short-Name> in a vidocq deployment.</description>

    <dependencies>
        <dependency>
            <groupId>io.vidocq.<short-name></groupId>
            <artifactId><short-name>-api</artifactId>
        </dependency>
        <!-- core, cdi-vauban, etc.: versions managed by the parent's <dependencyManagement> -->
    </dependencies>
</project>
```

Add at least one wrapper class and a `module-info.java` that re-exports, or declares
`provides ServiceLoader …`, according to the vidocq SPI.

### 3.4 Registration in `vidocq-runtime-extensions/pom.xml`

```xml
<subprojects>
    …
    <subproject>vidocq-runtime-<short-name>-extension</subproject>
    …
</subprojects>
```

---

## 4. Forgejo CI/CD workflows

This is **the most important step for a new producer**: without it, its `0.2.0` artefact is not
published to `central-snapshots`, and **every consumer PR will fail** with
`Could not resolve dependencies for io.vidocq.<short-name>:…` (a consumer's PR job resolves its
unchanged upstream dependencies from `central-snapshots`).

> 💡 That is exactly why the `add-cyrano` PR in `vidocq/vidocq` failed in May 2026:
> `cyrano/.forgejo/workflows/` did not exist yet when the consumer PR was opened. Bootstrap the producer
> workflows BEFORE opening the vidocq PR.

### 4.1 `.forgejo/workflows/ci.yml`

Build + TCK + deploy on push to `main`. Take an existing repository as a model (cassini/vauban):
everything goes through the composite actions of the `Vidocq/ci` repository:
- `Vidocq/ci/setup-maven@v1`: Java 25 Temurin + Maven 3.9.16 + `settings.xml` (SNAPSHOT resolution from
  `central-snapshots`)
- `Vidocq/ci/run-tck@v1`: official TCK (if applicable)
- `Vidocq/ci/deploy-maven@v1`: publishes to Maven Central (SNAPSHOT through `maven-deploy-plugin` →
  `central-snapshots`; RELEASE through `central-publishing`). Secrets: `CENTRAL_USERNAME`,
  `CENTRAL_PASSWORD`, `GPG_PRIVATE_KEY`, `GPG_PASSPHRASE`.
- `Vidocq/ci/notify-slack@v1`: notification

### 4.2 `.forgejo/workflows/pr.yml`

Copy the template `GestionProjet/workflow-templates/pr-producer.yml` as is: a **single** job,
`pr-validate`.

- It builds the producer in a release-style PR version `<base>-PR<num>.<sha8>` (without `-SNAPSHOT`),
  then runs `mvn install` into the runner's `~/.m2`: **nothing is published**.
- The `Vidocq/ci/build-impacted@v1` action uses GestionProjet to find the impacted consumers
  (transitive closure, **topological order**) and re-clones and rebuilds them one by one against the
  local PR artefacts.
- The success of this single job is the **only required check** of the branch protection.

### 4.3 `.forgejo/workflows/update-dep-graph.yml`

Copy `GestionProjet/workflow-templates/update-dep-graph.yml` as is. It needs access to the
`VIDOCQ_BOT_TOKEN` secret. Run it once manually with `workflow_dispatch` to bootstrap
`data/vidocq_<short-name>.json` in GestionProjet.

### 4.4 No dedicated consumer workflow

The `upstream-pr.yml` + dispatch mechanism is **removed**: `ci/build-impacted` re-clones and rebuilds
the consumers directly in the producer's job. A consumer repository therefore has **nothing** to
configure on the receiving side: it only has to expose its upstream dependencies through
`<upstream-name>.version` properties (see §0).

---

## 5. Official TCK (if applicable)

If the implemented spec has an official TCK (Jakarta, MicroProfile):

- **`<name>-tck` module OUTSIDE the reactor**: standalone Model 4.0.0, no `<parent>`. Reason:
  ShrinkWrap Maven Resolver 3.3 (a transitive dependency of the official TCK) cannot parse Model 4.1.0.
- **`run-official-tck-<spec>.sh` script** at the root of the repository, which:
  1. installs the non-public artefacts into the local M2
  2. runs `mvn -f <name>-tck/pom.xml test [-Dtest=…]`
- Do **NOT** add the tck module to the parent's `<subprojects>`.
- Do **NOT** build it with `mvn -pl`.

---

## 6. Registration in `GestionProjet`

### 6.1 Bootstrapping the `data/vidocq_<short-name>.json` file

On the local machine (or through the `update-dep-graph.yml` workflow once it is configured):

```bash
cd /path/to/GestionProjet
bash scripts/extract_deps.sh /path/to/<short-name> "vidocq/<short-name>" \
  > data/vidocq_<short-name>.json
make validate     # checks conformance to the schema
make graph        # rebuilds graph/inverted.json
git add data/vidocq_<short-name>.json graph/inverted.json
git commit -m "feat(graph): register vidocq/<short-name>"
```

### 6.2 Schema validation

The file must validate against `data/schema.json`:
- `schema_version: 1`
- `repo` matches `^vidocq/<name>$`
- each artefact in `produces[]` has a `groupId` matching `^io\.vidocq(\.[A-Za-z0-9_-]+)*$`
- `consumes[].scope` is one of `[compile, runtime, provided, test, system, import, build]`

---

## 7. Commit conventions

- **No `Co-Authored-By: Claude`** and no mention of AI (workspace rule).
- Conventional commits format: `feat(<scope>): …`, `fix(<scope>): …`, `ci(<scope>): …`,
  `M<milestone> — …` for roadmap milestones.

---

## 8. Integration checklist (TL;DR)

To tick before opening the consumer PR in `vidocq/vidocq`:

### New producer repository
- [ ] Root `pom.xml` Model 4.1.0, `root="true"`, groupId `io.vidocq.<name>`
- [ ] `.sdkmanrc`, `.gitignore`, `LICENSE`, `README.md`, `CLAUDE.md`
- [ ] `BUG.md` and `BENCH.md` (at least as stubs)
- [ ] `.claude/agents/` and `.claude/skills/` populated with what is used
- [ ] `<name>-tck/` as standalone Model 4.0.0 (if TCK) + `run-official-tck-*.sh` script
- [ ] `.forgejo/workflows/ci.yml` (setup-maven + deploy-maven on push to main)
- [ ] `.forgejo/workflows/pr.yml` (the single `pr-validate` job of the producer template)
- [ ] `.forgejo/workflows/update-dep-graph.yml` run once
- [ ] **`0.2.0` published to `central-snapshots`** (otherwise downstream PRs will fail when resolving
      their upstream dependencies)

### `vidocq/vidocq`
- [ ] `<<name>.version>` property added to the parent POM
- [ ] Upstream artefacts listed in the parent's `<dependencyManagement>`
- [ ] Wrapper `vidocq-runtime-<name>-extension` created under `vidocq-runtime-extensions/`
- [ ] Wrapper listed in the `<subprojects>` of `vidocq-runtime-extensions/pom.xml`
- [ ] Wrapper referenced in the parent's `<dependencyManagement>`
- [ ] `M5` non-regression test (ServiceLoader + Java Modules `provides`)

### `GestionProjet`
- [ ] `data/vidocq_<name>.json` validated and committed
- [ ] `graph/inverted.json` regenerated
- [ ] Organisation secret `VIDOCQ_BOT_TOKEN` accessible to the new repository

---

## 9. Associated agents and skills

Use them proactively during the integration:

- `jpms-guardian`: audit of the `module-info.java` of every new module
- `classfile-codegen`: review of the bytecode generation (proxies, indexers)
- `virtual-threads-reviewer`: concurrency review (no platform pool without a reason)
- `dependency-gatekeeper`: `pom.xml` review (zero-dep / Jakarta + MP specs only)
- `tck-runner`: TCK run + diagnosis (standalone Model 4.0.0)
- `/log-bug` skill: adds an entry to `<repo>/BUG.md`
- `/log-bench` skill: adds an entry to `<repo>/BENCH.md`

---

## 10. References

- Workspace: `vidocq/CLAUDE.md` (cross-cutting philosophy, BUG/BENCH conventions)
- Graph: `GestionProjet/README.md` (producer/consumer mechanism, data/ schema, workflow templates)
- Data schema: `GestionProjet/data/schema.json`
- Templates: `GestionProjet/workflow-templates/*.yml`
