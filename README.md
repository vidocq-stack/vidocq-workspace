# Vidocq workspace

The root of the Vidocq working directory. It bundles the shared
**agent instructions** (`AGENTS.md`, read by Codex and imported by Claude Code's
`CLAUDE.md`), the shared **Claude Code** config (agents, skills), the **mani** orchestration
(`mani.yaml`), and the shared **git hooks** (`.githooks/`). Check this repository
out **as the root of your working directory**, then let mani clone the
repositories inside it.

Since 2026-11-20 the code of Vidocq lives in one repository, the monorepo
[`Vidocq/vidocq`](https://codefloe.com/Vidocq/vidocq): every component (Chappe, Vauban, Cassini, the
MicroProfile components, …), their parent POM and the runtime. The workspace gathers it with the repositories
around it: the documentation and the site, CI and governance, `erasmus`, `tassis` and `verne` (not in the monorepo
yet), and the third-party extensions of the `VidocqCodeUniverse_VCU` organisation.

## Layout

This repo is designed to be the workspace root. The repositories are cloned
**into** it by mani and each keeps its own independent git repository — they are
git-ignored here (see `.gitignore`), so this repo only ever tracks the shared
config and guides.

```
<your-workspace>/            ← clone of THIS repo (its .git lives here)
├── .claude/                 ← shared subagents + slash-skills + settings.json
├── AGENTS.md                ← workspace conventions, single source (commit rules, Java Modules/codegen/zero-dep, TDD, …)
├── CLAUDE.md                ← `@AGENTS.md` + Claude Code specific tooling
├── mani.yaml                ← mani orchestration: project list + cross-repo tasks
├── .githooks/               ← shared git hooks (DCO sign-off)
├── docs/                    ← workspace guides (getting started, mani & worktrees, changes across repositories)
├── .gitignore               ← ignores the nested project clones + local/secret files
├── README.md
│
├── vidocq/main/             ← the monorepo, cloned here (own git), ignored
│   └── <branch>/            ← optional sibling worktrees, dir name == branch name
├── vidocq-docs/main/  erasmus/main/  ci/main/  …   ← the other repositories, ignored
```

Because a git repository can only track files **below** its own root, keeping
the config at the workspace root (this repo) is what lets Claude Code pick up
`.claude/` and `CLAUDE.md` (and Codex pick up `AGENTS.md`) for the whole
session — no symlinks, no submodules. The monorepo (at its root and in each
component's folder) and every other repository also ship their own `AGENTS.md`
with a short summary of the ecosystem rules, because an agent started inside
`vidocq/main/` only sees that repository's files.

## Getting started

**New here? Follow [docs/getting-started.md](docs/getting-started.md).** It takes you from a
fresh machine to your first pull request, step by step, on macOS, Linux and Windows (WSL 2):
Codefloe account, SSH and GPG keys, CLA, tools, clone, Maven configuration, first build, and
the pull request from your fork. In short, once your account and keys are ready:

1. Clone this repo as your workspace directory:
   ```bash
   git clone git@codefloe.com:Vidocq/vidocq-workspace.git && cd vidocq-workspace
   ```
2. Install [mani](https://github.com/alajmo/mani) and populate the project repos:
   ```bash
   mani sync              # clones each project into <repo>/main/
   mani run -a install-hooks # wires the shared DCO sign-off hooks into every repo
   ```
   The projects — the monorepo (`vidocq`), the documentation and the site (`vidocq-docs`, `pages`,
   `vidocq-tutorial`), `vidocq-benchmarks`, CI and governance (`ci`, `governance`, and `dep-graph` /
   `GestionProjet` for the repositories outside the monorepo), `erasmus`, `tassis`, `verne`, and the VCU
   repositories — stay independent git repos and are ignored here. `mani.yaml` is the list.
3. Build the monorepo from its root:
   ```bash
   cd vidocq/main
   ./mvnw install                         # what your branch changed and its dependents
   ./mvnw -pl <module path> -am verify    # one module and what it needs
   ```
   A branch build resolves the modules it does not rebuild from the Vidocq snapshot repository: declare it in
   `~/.m2/settings.xml` ([how](docs/getting-started.md#5-configure-maven-for-the-vidocq-snapshots)).
4. Open Claude Code (or Codex) at the workspace root — the shared conventions
   (and, for Claude Code, the shared agents and skills) are available immediately.

Contributors push to their own fork; maintainers push to the Vidocq repositories. The rules of
both roles are in the [governance repository](https://codefloe.com/Vidocq/governance):
[contributor guide](https://codefloe.com/Vidocq/governance/src/branch/main/CONTRIBUTING.md),
[maintainer guide](https://codefloe.com/Vidocq/governance/src/branch/main/MAINTAINERS.md).

See **[docs/working-with-mani-and-worktrees.md](docs/working-with-mani-and-worktrees.md)**
for the mani use cases, the worktree workflow, git hooks, and IntelliJ setup.

A change to several components of the monorepo is one pull request. A monorepo change that
`erasmus`, `tassis`, `verne` or a VCU extension must follow is merged in two steps, the monorepo
first: see **[docs/changes-across-repositories.md](docs/changes-across-repositories.md)**.

How the code is measured (the SonarQube server, the CI action that feeds it, the tools plugged
into it and their settings) is in **[QUALITY.md](QUALITY.md)**.
Where each component stands on its SonarQube cleanup and its performance work (done, in
progress, to do) is tracked in **[OPTIMS.md](OPTIMS.md)**.

## What's shared

### Subagents (`.claude/agents/`)
| Agent | Role |
|-------|------|
| `java-modules-guardian` | Audits `module-info.java` — minimal exports, no unjustified opens, no automatic-module fallback, no split-packages |
| `classfile-codegen` | Class-File API (JEP 484) + APT codegen, replacing runtime reflection |
| `tck-runner` | Runs and triages the official TCKs (runners behind each component's `tck` profile) |
| `virtual-threads-reviewer` | Reviews concurrency for virtual-thread-first design (no pinning, no platform pools) |
| `dependency-gatekeeper` | Reviews `pom.xml` changes against the zero-dependency policy |

### Skills (`.claude/skills/`)
- `/log-bug` — append a bug entry to the `BUG.md` of the current component (its folder in the monorepo, or the repository root outside it)
- `/log-bench` — append a benchmark run to the `BENCH.md` of the current component

### Conventions (`AGENTS.md`)
The workspace-wide rules, kept in a single file read by every coding agent:
signed and signed-off (DCO) commits, strict Java Modules, compile-time codegen
over reflection, zero runtime dependencies, TDD, virtual threads for I/O,
English everywhere, and the `BUG.md` / `BENCH.md` traceability policy.
`CLAUDE.md` is just `@AGENTS.md` plus the Claude Code specific tooling — edit
the rules in `AGENTS.md`. The monorepo (at its root and in each component's
folder) and every other repository additionally ship their own `AGENTS.md`
(and a `CLAUDE.md` importing it).

## Personal vs shared config

- **`.claude/settings.json`** (this repo) — *shared*. Keep it **portable**: no
  absolute paths, no machine-specific entries, **no secrets**. Reviewed like code.
- **`.claude/settings.local.json`** — *personal*, per-machine. **Git-ignored.**
  Put your own permission grants here; they never get shared.
- **Secrets** (Codefloe/Forgejo tokens, etc.) live only in
  `~/.config/vidocq/tokens.env` — **never** in this repo. The `.gitignore` and a
  `deny` rule in `settings.json` guard against committing/reading them here.
