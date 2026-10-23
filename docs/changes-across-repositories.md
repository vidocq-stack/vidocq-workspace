# Changes across repositories

Some changes cannot land in one repository: a brick changes an API, and its consumers must
follow in the same move. Vauban removing its default `java:comp/env/jdbc/<name>` rule while the
Vidocq naming extension still relied on it is one (vauban#179 and vidocq#303). This guide is the
maintainer workflow for such a change. It needs push access to the Vidocq repositories: a
contributor working from a fork opens the producer pull request alone, and a maintainer takes
the consumer side over.

## Why the producer's pull request rebuilds its consumers

The `pr-validate` check of a brick does not stop at the brick. Its `build-impacted` step
([`Vidocq/ci/build-impacted`](https://codefloe.com/Vidocq/ci/src/branch/main/build-impacted))
reads the inverted dependency graph, then rebuilds every downstream consumer, in dependency
order, against the artifacts of the pull request, and runs their unit and integration tests.
A brick whose change breaks a consumer does not get a green check.

By default each consumer is rebuilt from its `main`. For a change that breaks the consumer on
purpose, that check can never pass: the consumer's `main` is the code that still uses the old
API, and the consumer's fix cannot be merged first, since it needs the new API.

## Companion branches

Give the consumer's change **the same branch name** as the producer's. `build-impacted` then
rebuilds that consumer from that branch, the *companion branch*, instead of from its `main`:

| Pull request of the producer | Consumer with a branch of that name | Consumer without one |
|---|---|---|
| from a branch of the producer repository | rebuilt on the companion branch | rebuilt on `main` |
| from a fork | rebuilt on `main` | rebuilt on `main` |
| none (a push on `main`, a release) | rebuilt on `main` | rebuilt on `main` |

- The name matches as a whole: `feat/naming` does not pick `other/feat/naming`.
- A fork never picks a companion branch, so a fork cannot choose the code that is rebuilt and
  tested next to its change.
- The log of the step names the branch of each consumer, and a notice at the end lists the
  consumers rebuilt on a companion branch.
- If the forge cannot be asked whether a consumer has the branch, the step fails rather than
  falling back on `main` and testing the wrong code.
- A repository that never wants them sets `companion-branches: 'false'` on the step.

## The workflow

1. **Create the branch in every repository involved, with one name.** From the workspace root:

   ```bash
   BRANCH=feat/naming-bindings mani run wt-add -p vauban,vidocq
   ```

   Repositories with flat worktrees (`vidocq-docs`) flatten the directory name, not the
   branch name, so they take part as well.

2. **Push the consumer's branch before the producer's last push**, or at least before its
   checks run. `build-impacted` looks for the companion branch when it runs: a branch pushed
   afterwards is not seen until the producer's checks run again.

3. **Open both pull requests and link them** in their descriptions ("needs vauban#179",
   "vidocq#303 follows"). Until the producer is merged, the consumer's own pull request is red:
   its build resolves the producer's published snapshot, which still has the old API. This is
   expected.

4. **Merge the producer first.** Its green `build-impacted` is the proof that the pair works.
   Read its SonarQube comment, then post `/merge`.

5. **Wait for the producer's `main` build to publish its snapshot**, then push the consumer's
   branch again (a rebase on its `main` is the usual way), so that its checks run against the
   new snapshot.

6. **Merge the consumer as soon as its checks are green.** Between steps 4 and 6 the consumer's
   `main` does not build against the producer's snapshot: keep that window short, and do not
   start another change on that consumer in between.

A chain works the same way: when a consumer of the consumer also has the branch, the producer's
`build-impacted` rebuilds it on that branch too, and the merges follow the dependency order.

## What a companion branch does not cover

- **New dependencies.** The consumers come from the dependency graph of each repository's
  `main`. A companion branch that starts depending on the producer is not found by the graph,
  so it is not rebuilt.
- **Later pushes on the consumer.** The producer's check tested the companion branch as it was
  when the check ran. Push the producer again after a change on the consumer's branch that
  matters to the pair.
- **Fork pull requests.** A contributor's cross-repository change is taken over by a maintainer,
  who pushes the branches to the Vidocq repositories.

Never lift a branch protection to merge a producer whose consumers fail: that leaves the
consumers' `main` red until someone notices. Push a companion branch instead.
