# Vidocq workspace

The root of the Vidocq multi-repo working directory. It bundles the shared
**Claude Code** config (agents, skills, conventions), the **mani** orchestration
(`mani.yaml`), and the shared **git hooks** (`.githooks/`). Check this repository
out **as the root of your working directory**, then let mani clone the
individual project repos inside it.

## Layout

This repo is designed to be the workspace root. The Vidocq projects are cloned
**into** it (by the multi-repo checkout tooling) and each keeps its own
independent git repository — they are git-ignored here (see `.gitignore`), so
this repo only ever tracks the shared Claude config.

```
<your-workspace>/            ← clone of THIS repo (its .git lives here)
├── .claude/                 ← shared subagents + slash-skills + settings.json
├── CLAUDE.md                ← workspace conventions (commit rules, Java Modules/codegen/zero-dep, TDD, …)
├── mani.yaml                ← mani orchestration: project list + cross-repo tasks
├── .githooks/               ← shared git hooks (DCO sign-off)
├── docs/                    ← workspace guides (mani & worktrees)
├── .gitignore               ← ignores the nested project clones + local/secret files
├── README.md
│
├── vauban/main/  vidocq/main/  cassini/main/  …   ← cloned here (own git), ignored
│   └── <branch>/            ← optional sibling worktrees, dir name == branch name
```

Because a git repository can only track files **below** its own root, keeping
the config at the workspace root (this repo) is what lets Claude Code pick up
`.claude/` and `CLAUDE.md` for the whole multi-repo session — no symlinks, no
submodules.

## Getting started

1. Clone this repo as your workspace directory:
   ```bash
   git clone git@codeberg.org:Vidocq/vidocq-workspace.git vidocq && cd vidocq
   ```
2. Install [mani](https://github.com/alajmo/mani) and populate the project repos:
   ```bash
   mani sync              # clones each project into <repo>/main/
   mani run -a install-hooks # wires the shared DCO sign-off hooks into every repo
   ```
   The projects — the foundational bricks (`chappe`, `vauban`, `champollion`),
   the Jakarta EE layers (`foy`, `cassini`, `mansart`), the MicroProfile bricks
   (`ravel`, `knock`, `dirac`, `heisenberg`, `cervantes`, `cyrano`, `humboldt`,
   `grimm`), the runtime (`vidocq`), and the support repos (`vidocq-parent`,
   `vidocq-docs`, `ci`) — stay independent git repos and are ignored here.
3. Open Claude Code at the workspace root — the shared agents, skills and
   conventions are available immediately.

See **[docs/working-with-mani-and-worktrees.md](docs/working-with-mani-and-worktrees.md)**
for the mani use cases, the worktree workflow, git hooks, and IntelliJ setup.

## What's shared

### Subagents (`.claude/agents/`)
| Agent | Role |
|-------|------|
| `jpms-guardian` | Audits `module-info.java` — minimal exports, no unjustified opens, no automatic-module fallback, no split-packages |
| `classfile-codegen` | Class-File API (JEP 484) + APT codegen, replacing runtime reflection |
| `tck-runner` | Runs and triages the official Jakarta TCKs (out-of-reactor runners) |
| `virtual-threads-reviewer` | Reviews concurrency for virtual-thread-first design (no pinning, no platform pools) |
| `dependency-gatekeeper` | Reviews `pom.xml` changes against the zero-dependency policy |

### Skills (`.claude/skills/`)
- `/log-bug` — append a bug entry to the current sub-project's `BUG.md`
- `/log-bench` — append a benchmark run to the current sub-project's `BENCH.md`

### Conventions (`CLAUDE.md`)
The workspace-wide rules: signed-off/no-AI-mention commits, strict Java Modules,
compile-time codegen over reflection, zero/minimal dependencies, TDD, virtual
threads for I/O, English for code/docs, and the `BUG.md` / `BENCH.md`
traceability policy. Each sub-project additionally ships its own `CLAUDE.md`.

## Personal vs shared config

- **`.claude/settings.json`** (this repo) — *shared*. Keep it **portable**: no
  absolute paths, no machine-specific entries, **no secrets**. Reviewed like code.
- **`.claude/settings.local.json`** — *personal*, per-machine. **Git-ignored.**
  Put your own permission grants here; they never get shared.
- **Secrets** (Codeberg/Forgejo tokens, etc.) live only in
  `~/.config/vidocq/tokens.env` — **never** in this repo. The `.gitignore` and a
  `deny` rule in `settings.json` guard against committing/reading them here.
