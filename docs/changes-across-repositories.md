# Changes across repositories

Since 2026-11-20 the components, their parent and the runtime live in one repository, the monorepo
`Vidocq/vidocq`. Most changes that used to span several repositories are now one pull request. This guide covers
that case and the few repositories still around the monorepo.

## Inside the monorepo: one pull request

- **A shared API change fixes every caller in the same pull request.** The pull request build
  (gitflow-incremental-builder, `.forgejo/workflows/pr.yml`) builds the modules the change touches and tests every
  module downstream of them: a change that breaks a caller does not get a green check.
- **A change under `vauban/` goes in its own pull request**, with its own test in `vauban/` reproducing the problem
  without the module that found it.
- **No feature on top of a feature**: what another branch needs merges first.
- There are no companion branches in the monorepo. The maintainer merges, by hand.

## Repositories outside the monorepo

`erasmus` and `tassis` (until they move into the monorepo's `incubator/`), `verne` (until it moves to VCU) and the
extensions of the `VidocqCodeUniverse_VCU` organisation build against the monorepo's SNAPSHOTs, with the same GAVs
as before. The monorepo's pull request does not build them, so a monorepo change they must follow goes in two
steps:

1. **Open both pull requests and link them** in their descriptions ("needs vidocq#123"). Giving the follower's
   branch the same name as the monorepo's keeps the pair easy to find. Until the monorepo change is merged, the
   follower's pull request is red: its build resolves the published SNAPSHOT, which still has the old API. This is
   expected.
2. **Merge the monorepo first**, then wait for its `main` build to publish the SNAPSHOT (to `maven.vidocq.dev`;
   read the commit in the published build-info before relying on it). Push the follower's branch again (a rebase
   on its `main`), so that its checks run against the new SNAPSHOT, and merge it as soon as they are green.

Between the two merges the follower's `main` does not build against the new SNAPSHOT: keep that window short, and
keep an API change additive across it where you can (add a method or a type rather than change a signature or a
record's components).

erasmus, tassis and verne keep their multi-repo CI until they move: their `pr-validate` reads
[`Vidocq/dep-graph`](https://codefloe.com/Vidocq/dep-graph) and the workflow templates of
[`Vidocq/GestionProjet`](https://codefloe.com/Vidocq/GestionProjet), and the companion-branch rule of that CI
(a consumer built on the branch of the same name as its producer's) still applies between them. None of them
depends on another today, so it rarely matters.

Never lift a branch protection to merge around a red build: that leaves a `main` red until someone notices.
