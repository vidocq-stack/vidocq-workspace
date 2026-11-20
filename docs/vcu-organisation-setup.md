# Setting up the VidocqCodeUniverse_VCU organisation

Status: plan, 2026-11-19. Nothing below is configured yet unless marked **done**. Source of the intent: MONOREPO.md §8
"VCU (after the weekend)" and the RFC "Vidocq monorepo, incubator and VCU" (2026-11-17).

VCU hosts extensions written and maintained by people outside the core team, with third-party dependencies
allowed. Its CI therefore runs code the Vidocq maintainers did not write. Everything below follows from one rule:
**a VCU workflow must not be able to reach anything that belongs to `Vidocq`** — its bot, its signing keys, its
Maven namespace, its runners' hosts.

## 1. What exists today (read on 2026-11-19 through the API)

| Item | Vidocq | VidocqCodeUniverse_VCU |
|------|--------|------------------------|
| Visibility | public | public, created 2026-10-26, **no repository** |
| Members | — | `yblazart`, `vidocq-ci-bot` |
| Teams | `Owners`, `devs` (write) | `Owners`, `devs` (write, "Developers") |
| Org variables | `SONAR_HOST_URL`, `PORTAINER_MACUNTU_URL` | `SONAR_HOST_URL` |
| Org secrets | 24 (Central, GPG, CI bot GPG, Reposilite, Sonar, Slack, mirror, Portainer, registry, bot token) | `VIDOCQ_BOT_TOKEN` only |
| Runners | Montreuil01/02, Mac, Foix, Villejuif-runner1/2, CracRunnerKikanux | `CodefloeRunnerVCU01` (macuntu), labels `ubuntu-latest`, `vidocq-runner`, `docker` |
| Webhooks | none | none |

The name in MONOREPO.md (`VidocqCodeUniverse`) differs from the real one (`VidocqCodeUniverse_VCU`).

## 2. Two problems in what exists

**Decision (Yann, 2026-11-19): VCU is not really open for now** — only the core team writes there. So VCU keeps
`VIDOCQ_BOT_TOKEN` and the runner VCU01 on macuntu, and may reuse Vidocq's credentials (§3) for the time being.
The two points below, and the scoping of §3, become **the checklist to clear before VCU accepts an outside
maintainer**.

1. **`VIDOCQ_BOT_TOKEN` in VCU.** If it is the same token as Vidocq's (`vidocq-ci-bot`, write on every Vidocq
   repository), any VCU workflow can read it and push to Vidocq. A VCU maintainer edits their own workflows, so
   "the workflow does not print it" is no protection. → VCU gets **its own bot account** (`vcu-ci-bot`), member of
   VCU only, and its own token. The Vidocq bot leaves the VCU organisation, or stays without a token stored there.
2. **`CodefloeRunnerVCU01` runs on macuntu**, a machine on Yann's LAN, next to Vidocq's runners and with Docker
   (dind). MONOREPO.md says fork PRs never run on the maintainers' machines. → Either fork PR workflows wait for an
   approval (Forgejo setting, to check on 17.0.1), or VCU gets isolated ephemeral runners (a cloud VM per job, or
   a VM with no LAN route). Until then: VCU01 takes jobs of trusted branches only.

**Decision (Yann, 2026-11-19): no merge-bot in VCU at first.** VCU repositories start without the merge-bot and
without `require_signed_commits`; Yann merges by hand. The reasons:

- the `CI_BOT_GPG_*` private key (`38A7110A14A77BFA`) was generated on 2026-08-28 by Antoine Sabot-Durand with
  Copilot (governance `a683bce`, `63f5c4d`); it is in no keyring of Yann's and cannot be read back from the Vidocq
  secrets;
- Yann has no access to the `vidocq-ci-bot` account, so he cannot generate a token for VCU from it either.
  `VIDOCQ_BOT_TOKEN` was removed from VCU on 2026-11-19.

The VCU template therefore drops the jobs that need the bot (merge-bot, the Sonar PR comment, dep-graph and docs
triggers) until a bot account Yann controls exists (`vcu-ci-bot`, §3).

## 3. Secrets: what a VCU repository needs, and with which scope

Every credential below is **distinct from Vidocq's** and limited to VCU. The values are created and entered by
Yann (in the forge UI or the issuer's), never by an agent.

| Secret / variable | Used by | Scope it must have |
|-------------------|---------|--------------------|
| `VCU_BOT_TOKEN` | merge-bot, status comments, dep-graph trigger | token of `vcu-ci-bot`: write on VCU repositories, nothing in Vidocq |
| `VCU_BOT_GPG_*` (key id, private key, passphrase) | merge-bot re-signing | a key of `vcu-ci-bot`, registered in governance as a bot key |
| `SONAR_TOKEN` | sonar job | an analysis token of a SonarQube user limited to `vcu-*` projects |
| `SONAR_HOST_URL` (variable) | sonar job | **done**, same server |
| `REPOSILITE_USERNAME` / `_PASSWORD` | SNAPSHOT publishing | a Reposilite user that can write `io/vidocq/vcu/**` only |
| `CENTRAL_USERNAME` / `_PASSWORD` | release | a Central Portal token for the `io.vidocq.vcu` namespace only, if Central allows that granularity; otherwise releases stay manual for now |
| `GPG_*` (release signing) | release | the dedicated subkey or association key of MONOREPO.md, **not** Yann's YubiKey key |
| `SLACK_WEBHOOK_URL` | notifications | a webhook to a VCU channel, or none |

Not copied to VCU: Portainer, registry, mirror, `MYGITHUB_MIRROR_TOKEN`, the CI bot GPG key of Vidocq.

Forgejo does not hand secrets to `pull_request` runs from forks, but it does to `pull_request_target`. VCU
workflows using `pull_request_target` (as bodoni's `notify-slack.yml` does) must not check out the PR's code.

## 4. Runners

| Option | Cost | Isolation |
|--------|------|-----------|
| A. Keep VCU01 on macuntu, require approval for fork PR workflows | none | trusted branches only; a mistaken approval runs foreign code on the LAN |
| B. A VM with no route to the LAN (Lima VM or macuntu VM, firewall to the internet only) | a few hours | good; runner token stays on a machine Yann owns |
| C. Ephemeral cloud runners (one VM per job) | money, setup | best |

Labels: VCU runners take `vcu-runner` (not `vidocq-runner`), so that a VCU workflow copied from a Vidocq one does not
silently match a Vidocq runner if the runner is ever shared, and the template uses `runs-on: vcu-runner`.

## 5. Organisation settings

- Teams: `Owners` (Yann), `devs` stays empty; one team per extension (`ext-<name>`, write on its repository only),
  whose members are its named maintainers.
- Default branch protection on each repository (from the template): signed commits, `pr-validate` and
  `governance-checks` required, no push to `main`.
- Actions: enable on each repository created from the template; approval of fork workflows (§2).
- Description, website (`https://vidocq.dev`), avatar.

## 6. Template repository `VidocqCodeUniverse_VCU/template`

Parent POM (inherits `io.vidocq:vidocq-parent`), licence header and REUSE, CLA and DCO checks (governance-checks
from `Vidocq/ci`), README skeleton (maintainer, groupId `io.vidocq.vcu.<name>`, declared runtime version), the
workflows of a brick adapted to VCU (secrets of §3, `vcu-runner`, nightly build against the runtime SNAPSHOT),
`AGENTS.md` with the VCU rules (third-party dependencies allowed; the rest of the ecosystem rules apply).

## 7. Order

1. Yann decides §2 (bot, runner isolation) and §4.
2. Bot account `vcu-ci-bot`, its token and GPG key (Yann); governance registers the key.
3. Scoped Reposilite user, Sonar user/token, Central and signing decisions (Yann creates the values).
4. Secrets entered in the VCU organisation (Yann).
5. Runner per §4.
6. Template repository (agent work, PR reviewed by Yann).
7. First extension: Flyway, then Vaadin, then the langchain4j-cdi MCP extension (vidocq#204), in the repository
   `vidocq_vcu_extension_lc4jcdi` (name chosen by Yann on 2026-11-19).
8. `mani.yaml`: a `vcu` tag; forge-dashboard: the organisation added (MONOREPO.md §9).
