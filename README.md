# Vidocq Claude workspace

Shared **Claude Code** configuration for working across the Vidocq multi-repo
ecosystem — agents, skills, workspace conventions and portable settings. Check
this repository out **as the root of your working directory**, then let the
checkout tooling clone the individual project repos inside it.

## Layout

This repo is designed to be the workspace root. The Vidocq projects are cloned
**into** it (by the multi-repo checkout tooling) and each keeps its own
independent git repository — they are git-ignored here (see `.gitignore`), so
this repo only ever tracks the shared Claude config.

```
<your-workspace>/            ← clone of THIS repo (its .git lives here)
├── .claude/
│   ├── agents/              ← shared subagents (audit / codegen / TCK / concurrency / deps)
│   ├── skills/              ← shared slash-skills (/log-bug, /log-bench)
│   └── settings.json        ← SHARED, portable Claude Code settings (reviewed as team config)
├── CLAUDE.md                ← workspace conventions (commit rules, Java Modules/codegen/zero-dep, TDD, …)
├── .gitignore               ← ignores the nested project clones + local/secret files
├── README.md
│
├── vauban/   vidocq/   cassini/   champollion/   chappe/   foy/   mansart/   …   ← cloned here, own git, ignored
```

Because a git repository can only track files **below** its own root, keeping
the config at the workspace root (this repo) is what lets Claude Code pick up
`.claude/` and `CLAUDE.md` for the whole multi-repo session — no symlinks, no
submodules.

## Getting started

1. Clone this repo as your workspace directory:
   ```bash
   git clone <this-repo-url> vidocq && cd vidocq
   ```
2. Populate the project repos with the multi-repo checkout tooling *(provided
   separately)* — it clones `vauban`, `vidocq`, `cassini`, `champollion`,
   `chappe`, `foy`, `mansart`, and the MicroProfile bricks (`ravel`, `knock`,
   `dirac`, `heisenberg`, `grimm`, `cyrano`, `cervantes`, `humboldt`) into this
   directory. They stay independent git repos and are ignored here.
3. Open Claude Code at the workspace root — the shared agents, skills and
   conventions are available immediately.

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
