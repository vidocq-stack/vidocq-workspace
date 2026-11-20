# Working with mani & worktrees

This workspace is orchestrated with [mani](https://github.com/alajmo/mani): one
config (`mani.yaml`) lists every repository of the ecosystem and provides
cross-repo tasks. Each repository is cloned as `<repo>/main/` (a normal clone)
plus optional sibling worktrees `<repo>/<branch>/`.

Since 2026-11-20 most of the work happens in one repository, the monorepo
`Vidocq/vidocq`, cloned as `vidocq/main/`: one worktree per task,
`vidocq/<branch>/`. The other projects are the repositories around it.

## Layout

```
vidocq-workspace/            ← this repo (its .git lives here)
├── .claude/  AGENTS.md  CLAUDE.md  README.md  mani.yaml  .githooks/  docs/
├── vidocq/
│   ├── main/                ← the monorepo clone (its .git), tracks origin/main
│   ├── feat/123-foo/        ← worktree, branch feat/123-foo
│   └── fix/405-bar/         ← worktree, branch fix/405-bar
├── vidocq-docs/
│   └── main/
├── erasmus/
│   └── main/
└── …                        ← all git-ignored in this repo (see .gitignore)
```

`mani.yaml` points each project's `path` at `<repo>/main`, so mani always
operates on the primary clone; worktrees are created with git (or the `wt-add`
task) as siblings of `main`.

## The projects

| Tag | Projects |
|---|---|
| `vidocq` | `vidocq` (the monorepo), `vidocq-docs`, `pages`, `governance`, `vidocq-benchmarks`, `vidocq-tutorial` |
| `ci` | `ci`, `dep-graph`, `GestionProjet` |
| `legacy` | `dep-graph`, `GestionProjet` (they serve only the repositories below), `erasmus`, `tassis` (both to the monorepo's `incubator/`), `verne` (to VCU) |
| `vcu` | `vcu-template`, `vidocq_vcu_extension_lc4jcdi`, `vidocq_vcu_extension_vaadin`, `vaadin-on-vidocq` (organisation `VidocqCodeUniverse_VCU`) |
| `code` | the projects with a Java build: `vidocq`, `vidocq-benchmarks`, `erasmus`, `tassis`, `verne`, the VCU extensions and `vaadin-on-vidocq` |
| `docs` | `vidocq-docs`, `pages`, `vidocq-tutorial` |
| `flat-worktree` | `vidocq-docs` (see [Exemptions](#exemptions)) |

`mani.yaml` is the reference; `mani list projects` prints the current list with
its tags.

## mani — key use cases

Install: `brew install mani` (or see the mani repository).

```bash
mani sync                             # clone any missing project into <repo>/main
mani run -a status                    # short git status of every repo (table)
mani run -a sync-all                  # fetch + ff-only pull across all repos (parallel)
mani run -a sync-all-default          # switch each repo to its default branch, then pull
mani run -a ahead-behind              # ahead/behind vs upstream, per repo
mani run -a dirty --output table      # flag repos with uncommitted changes
mani run -a log-recent                # last 10 commits per repo
mani exec -a -- <cmd>                 # run an arbitrary command in every repo
```

`mani run` and `mani exec` always need a target — there is no implicit default:
`-a`/`--all` for every project, `-t <tag>` for a tag, or `-p <project>` for a
single project.

```bash
mani run status -t code         # only the projects tagged 'code'
mani run status -p vidocq       # only the monorepo
```

## Git hooks (DCO sign-off)

The workspace ships shared hooks in `.githooks/` that enforce the DCO
`Signed-off-by` trailer — `prepare-commit-msg` auto-appends it, `commit-msg` is a
safety net that blocks any commit still missing it. Wire them into every repo
once:

```bash
mani run -a install-hooks       # sets core.hooksPath -> <workspace>/.githooks per repo
```

A repo and its worktrees share one config, so this also covers the worktrees.
Alternatively, an `includeIf "gitdir:<workspace>/"` block in your global
`~/.gitconfig` can set `core.hooksPath` for everything under the workspace.

## Worktrees

Convention: **the directory name equals the branch name**, as a sibling of
`main`. `wt-add` branches from the local `main` by default, which is often
behind: fetch first and pass `BASE=origin/main`.

```bash
# via mani (the task runs inside <repo>/main):
git -C vidocq/main fetch origin
BRANCH=feat/123-foo BASE=origin/main mani run wt-add -p vidocq

# or manually, from vidocq/main:
git worktree add -b feat/123-foo ../feat/123-foo origin/main   # new branch
git worktree add    ../fix/405-bar fix/405-bar                 # existing branch
git worktree list
git worktree remove ../feat/123-foo                            # when done
```

A change to several components of the monorepo is one branch and one pull
request. A change that a repository outside the monorepo, or a VCU extension,
must follow is described in [Changes across repositories](changes-across-repositories.md).

Branch names with slashes create nested dirs (`vidocq/feat/123-foo/`) — the
directory still mirrors the branch name. Note the consequence: **a checkout's
depth below the workspace root is not constant** — `main/` sits one level under
`<repo>/`, `fix/mani-layout-paths/` two. Anything that depends on that depth
breaks; see the exemptions below.

## Exemptions

> **Rule:** the plain convention holds unless a checkout's filesystem *location*
> is part of the repo's contract — because it **contains** the other repos, or
> because it **reaches outside itself by relative path**. The first case rules
> worktrees out entirely; the second only rules out *nesting*.

Two repos qualify today, in the two different ways:

### 1. No worktrees at all — vidocq-workspace (this repo)

It *is* the container. A worktree of it is an empty shell in which `mani.yaml`'s
`<repo>/main` paths resolve to nothing, so `mani sync` there clones every
project a second time — a duplicate workspace that drifts from the real one.
Work on branches in place:

```bash
git switch -c feat/123-foo     # in the workspace root, no worktree
```

The workspace repo is not a mani project, so nothing can intercept a manual
`git worktree add` here — just don't. If you truly need two branches at once,
clone the workspace repo elsewhere instead.

### 2. Flat worktrees only — vidocq-docs

`antora-playbook-local.yml` reaches its sources (the monorepo, erasmus, tassis)
by relative path, so what matters is **depth, not the name `main`**. A worktree
is fine as long as it sits at the same level as `main/` — which means the
directory name must not contain a slash:

| checkout | depth below `vidocq-docs/` | same relative paths as `main/` |
|---|---|---|
| `vidocq-docs/main/` | 1 | yes |
| `vidocq-docs/fix-mani-layout-paths/` | 1 | yes |
| `vidocq-docs/fix/mani-layout-paths/` | 2 | no: every relative path is one level off |

So the workspace convention "directory name equals branch name" is **relaxed
here to a flattened name**: `fix/foo` → `fix-foo`. `mani run wt-add` does this
for you — such projects carry the `flat-worktree` tag in `mani.yaml`:

```bash
$ BRANCH=fix/foo mani run wt-add -p vidocq-docs
note: 'vidocq-docs' is flat-worktree — using directory 'fix-foo' (not 'fix/foo')
worktree: <workspace>/vidocq-docs/fix-foo  (branch fix/foo)
```

The branch itself keeps its normal slashed name; only the directory is flattened.

Failure here is silent rather than loud — Antora finds no content at the wrong
paths and cheerfully builds a site with every component page missing.

To make a further repo flat-worktree, add the tag to its `tags:` in `mani.yaml`
and note the reason above.

## IntelliJ

- **The monorepo:** open `vidocq/main/` (its root `pom.xml`) as one project:
  every component is a module of that one reactor.
- **Focused branch work:** open a worktree (`vidocq/feat/123-foo/`) as its
  **own** project window — it indexes that branch separately, so switching
  "branches" becomes switching windows, with no re-index churn on the main
  project.
- **Aggregate view:** open `vidocq-workspace/` and *Link* the `pom.xml` of each
  checkout you need (`vidocq/main/`, `erasmus/main/`, …) as a Maven project —
  the Git panel shows all repos (each `main/` is its own VCS root).
- Don't mix a repo's `main` and one of its worktrees in the *same* project
  window (VCS-mapping / Maven-import confusion). Give each window a distinct name
  (`vidocq-main`, `vidocq/123-foo`).
- `.idea/` and `*.iml` are git-ignored per repo — each window gets its own,
  which is intended.

## Migrating existing flat clones to `<repo>/main/`

If your projects are currently flat clones (`<repo>/` directly), move each into a
`main/` subdir — branches, remotes and worktree metadata travel with the clone.
Loop over every top-level flat clone from the workspace root:

```bash
# from the workspace root — migrate every flat project clone to <repo>/main:
for r in */; do
  r=${r%/}
  [ -d "$r/.git" ] || continue        # skip docs/, .githooks etc. (only real clones)
  [ -d "$r/main/.git" ] && continue    # already migrated
  mv "$r" "$r.tmp" && mkdir "$r" && mv "$r.tmp" "$r/main"
done
mani run -a install-hooks             # re-point each repo's hooks at the shared .githooks
```

Do this only when no repo has an in-flight push/PR tied to its old path. (A
single repo, by hand: `mv vidocq vidocq.tmp && mkdir vidocq && mv vidocq.tmp
vidocq/main`.)

Directories left over from the repositories merged into the monorepo
(`vauban/`, `cassini/`, …) are no longer in `mani.yaml`; push or drop their
unmerged work, then delete them.

### Moving a clone (or the workspace root) breaks its worktrees

Worktree links are **absolute paths recorded on both sides** — `.git/worktrees/<name>/gitdir`
in the clone, and the `.git` *file* inside the worktree. Moving either end leaves
them dangling: `git worktree list` marks the entry `prunable` and commands inside
the worktree fail with `fatal: not a git repository`. The directory contents are
untouched, so nothing is lost — but do **not** run `git worktree prune`, which
just forgets them.

Repair instead, from each clone, passing the worktrees' *new* paths:

```bash
# from the workspace root — repair every moved worktree in every project:
for c in */main; do
  find "${c%/main}" -mindepth 2 -maxdepth 3 -name .git -type f \
    | sed 's|/\.git$||' | while read -r wt; do
        git -C "$c" worktree repair "$PWD/$wt"
      done
done
git worktree list   # per repo: no 'prunable' entries left
```

This is exactly what happened when the workspace repo itself was migrated into
`main/`: 14 project worktrees were silently orphaned. It is also the second
reason the workspace repo is worktree-exempt.
