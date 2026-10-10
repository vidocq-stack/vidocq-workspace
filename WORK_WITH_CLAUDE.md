# WORK_WITH_CLAUDE.md — Working with Yann on the Vidocq ecosystem

> **What this is.** A *collaboration* meta-guide, complementary to `AGENTS.md`
> (imported by `CLAUDE.md`). `AGENTS.md` states the **technical conventions** (Java Modules, zero-dep, codegen,
> TDD…); this file states **how Yann works with Claude**: his stance, his rituals,
> his signals, what earns his trust and what loses it.
>
> **How it was produced.** Analysis of the workspace's real transcripts:
> **44 sessions, 1,156 prompts**, processed out of context (extraction of the human
> messages, themes, verbatim quotes). This is not guesswork — it is what the
> exchanges show. To be re-read and amended over time.
>
> **Language.** This file is written in **English**, like `AGENTS.md`, the code, the
> CI and team messages (European project, multiple contributors). Reminder: the
> *chat* stays in **French**. Verbatim quotes are kept in their original French —
> they are evidence, not prose — with an English rendering in brackets.
>
> **Publication note.** This public version is redacted of the section describing the
> internal infrastructure (hosts, secrets, local paths). The methodological content
> is intact.

---

## 1. In one sentence

> Yann is an **architect-maintainer** who thinks in terms of the **ecosystem**,
> steers through **short, direct prompts**, **challenges** decisions with
> "…right?" hypotheses, and accepts a claim only once it is **proven** (green build,
> TCK, `clean install`, commit pushed). He alternates between in-depth **studies**
> and **executions** delegated with a plain "go".

---

## 2. Who you are dealing with

- **Role**: sole main human maintainer of ~15 independent Maven sub-projects
  (zero-dependency Jakarta/MicroProfile reimplementations). Co-contributors:
  **Antoine** and occasional external PRs.
- **Level**: very high. He knows the spec, the JVM, the CI, the infrastructure. He is
  **often right** when he corrects — do not contradict him lightly, verify.
- **Stance**: he is not an order-giver processing tickets. He is a **peer thinking out
  loud**, who delegates execution and digging, but keeps the architectural decision
  and demands to understand the "why" behind it.
- **Real context**: real infrastructure (forge, CI, registry, mirrors, Maven Central)
  and real operational incidents. He **gives me access** to the tools and expects me
  to use them.

---

## 3. The work loop

```mermaid
flowchart TD
    A["Session opening<br/>resync: git pull rebase, locate sources, load into memory"] --> B{"Mode?"}
    B -->|"Understand / decide"| C["STUDY<br/>diagnosis, comparison, written artefact<br/>RELEASE.md / PLAN.md / BENCH.md"]
    B -->|"Do"| D["EXECUTION<br/>TDD red→green→refactor"]
    C --> E["Hypothesis submitted<br/>'…right?'"]
    E -->|"Yann approves: 'go'"| D
    E -->|"Yann corrects course"| C
    D --> F["PROOF<br/>green clean install · TCK · CI build · commit+push"]
    F -->|"unproven / incomplete"| D
    F -->|"proven"| G["TRACE<br/>commit (Co-Authored-By if AI assisted) · BUG.md / BENCH.md · Antora docs FR+EN · memory"]
    G --> H["/compact to continue · /clear to start clean"]
    H --> A
```

**The non-negotiable point is `F` (the proof).** As long as it is not green and
proven *by me*, it is not done (see §5.2 and §7).

---

## 4. The two registers: Study vs Execution

Yann draws a sharp line between **thinking** and **doing**. Recognising the register
avoids the misunderstanding of charging ahead when he wants analysis, or dithering
when he wants a result.

```mermaid
flowchart LR
    subgraph STUDY["🔬 STUDY — produce understanding"]
      direction TB
      E1["'Je vais te lancer sur une etude'<br/>(I'm going to set you on a study)"]
      E2["'Nouvelle etude. À m'attendre dans RELEASE.md'<br/>(New study. To be waiting for me in RELEASE.md)"]
      E3["'On va etudier les perfs de chappe… bench vs jetty ?'<br/>(Let's study chappe's performance… bench vs jetty?)"]
      E4["'Rappel moi pourquoi ça c'est mieux que…'<br/>(Remind me why this is better than…)"]
    end
    subgraph EXEC["⚙️ EXECUTION — produce a result"]
      direction TB
      X1["'go' / 'non vas y' (no, go ahead)"]
      X2["'deploie le pr.yml partout stp'<br/>(deploy pr.yml everywhere please)"]
      X3["'fait un git pull rebase de tous mes projets'<br/>(do a git pull rebase of all my projects)"]
      X4["'tu peux fixer' (can you fix it)"]
    end
    STUDY -->|"hypothesis validated"| EXEC
```

| | **STUDY** | **EXECUTION** |
|---|---|---|
| Trigger | "étude", "bilan", "rappelle-moi pourquoi", "était-ce un bon choix ?" | "go", "vas y", "fixe", "déploie", "renomme" |
| Expected deliverable | a **written artefact** (`RELEASE.md`, `PLAN.md`, comparison, post-mortem) | **merged code + green proof** |
| My job | options, trade-offs, **one recommendation** (not a catalogue) | TDD, build, push, trace |
| Mistake to avoid | coding before the decision is aligned | re-debating what is already settled |

---

## 5. Interaction patterns (with real verbatim quotes)

### 5.1 — The "…right?" hypothesis (the most frequent)
He does not always give an order: he **states a technical hypothesis and asks for
refutation or confirmation**. It is an invitation to verify, not a certainty.

> « C'est à la BCE de Cassini de faire le Job **non ?** » [it's Cassini's
> `BuildCompatibleExtension` that should do the job, right?] · « en utilisant une
> `buildCompatibleExtension` tu dois pouvoir ajouter l'interceptor **non ?** » [using a
> `buildCompatibleExtension` you should be able to add the interceptor, right?] ·
> « cyrano est un rest client **non ?** » [cyrano is a REST client, right?] · « il
> manque un jpackage **non ?** » [a jpackage is missing, right?]

**Expected response:** check in the code, then **settle it with proof** — either agree
with him *or* disabuse him with the evidence. Above all, no complacent "yes": when his
Vauban fix was bad, he corrected course **three times** ("Le dernier fix sur Vauban
n'est pas bon… non ?" — the last fix on Vauban isn't good… right?) — he was right.

### 5.2 — Proof before assertion
A recurring question, almost a reflex:

> « tu as tout **commit et push** ? » [have you committed and pushed everything?] ·
> « tu as bien vérifier **TOUS** les sous répertoires ? » [did you really check ALL the
> subdirectories?] · « On **reverifie** tout ? » [shall we re-verify everything?] ·
> « compile tck etc ? » · « tu peux **vérifier les status des build** sur la CI ? »
> [can you check the build statuses on CI?]

**Expected response:** never declare "green / done / fixed" without having run the
command and read the output. Agents have already **lied in both directions** (false
"green", false "incomplete") → **re-verify it myself**. And **always `clean install`**,
never an isolated `install`/`test`: a stale `target/` manufactures false failures.

### 5.3 — The laconic "go"
Once the analysis is aligned, he triggers with two words. The terseness **is** the
green light.

> « go » · « non vas y » [no, go ahead] · « Non vas y, PR de test » [no, go ahead, test PR]

**Expected response:** execute, do not ask for confirmation again, do not re-debate.

### 5.4 — Thinking ecosystem (cross-cutting campaigns)
Many requests touch **every project at once**.

> « gros chantier, on va basculer en **triple license** EPL/GPL/EUPL, faut mettre tous
> les projets à jour » [big campaign, we're switching to triple licensing EPL/GPL/EUPL,
> all the projects need updating] · « on va passer **tous les projet** en maven 3.9.16 »
> [we're moving all the projects to maven 3.9.16] · « renommer Vidocq MicroProfile
> **Server → Runtime** (vidocq-mps → vidocqmpr) » [rename Vidocq MicroProfile
> Server → Runtime]

**Expected response:** reason at workspace scale (install order, parent first, mirrors,
CI, docs), not project by project in a silo.

### 5.5 — Justify & post-mortem
He challenges **past** decisions and wants the "why" re-anchored.

> « **Rappel moi pourquoi** ça c'est mieux que le discover de l'apt automatique ? »
> [remind me why this is better than automatic APT discovery?] · « on a fait le choix de
> ne pas utiliser le sdk OpenTelemetry. **Était-ce un bon choix in fine ?** » [we chose
> not to use the OpenTelemetry SDK. Was that a good choice in the end?] · « pourquoi tu
> ne l'as pas implémenté à la base quand tu as fait cassini !! » [why didn't you
> implement it in the first place when you did cassini!!]

**Expected response:** an honest, argued answer, including "it was a mistake / a
trade-off that has aged". No flattering rewrite of history.

### 5.6 — Debugging from a pasted symptom
He pastes the **raw trace** (build failed, stack, Central validation) + "tu peux fixer".

> « La release a failed pour chappe : 10 failed Component Validations… » [the release
> failed for chappe: 10 failed Component Validations…] · « webhook manquant — cannot
> send 'pr-open' notification » [missing webhook]

**Expected response:** systematic debugging from the real symptom (cf. the
`systematic-debugging` skill), reproduce, fix the cause, prove it.

### 5.7 — Memory upkeep
> « ajoute le projet a ta mémoire et jette y un oeil je viens de le cloner » [add the
> project to your memory and take a look, I've just cloned it]

**Expected response:** keep the memory up to date (facts not derivable from the code),
and **verify** that a note has not gone stale before relying on it.

### 5.8 — Opening resync
A session often starts with bringing the state up to date.

> « tu peux **git pull rebase** les projets ? » [can you git pull rebase the projects?] ·
> « On reprend sur Arago, **tu localise les sources** ? » [we're resuming on Arago, can
> you locate the sources?] · « tout est à jour ? » [is everything up to date?]

**Expected response:** synchronise, locate, load the context **before** acting.

### 5.9 — Demanding completeness
He calls out omissions and half-finished work, sometimes with legitimate frustration.

> « Il semblerait que humboldt ne soit pas fini. On vérifie et on **fini** ? » [it seems
> humboldt isn't finished. Shall we check and finish it?] · « il manque un jpackage
> non ? » [a jpackage is missing, right?] · « vidocq docs **manque de composants** »
> [vidocq docs is missing components]

**Expected response:** finish the scope ("doing the rest" is not a task to postpone, it
is to be completed now), and prove it.

---

## 6. Session cadence & rituals

- **Short prompts**: median **58 characters**, 68 % ≤ 120 c. The long ones (p90 ≈
  2,900 c.) are **study briefs** or pasted specs/errors. → I can answer densely; he
  writes fast and with typos he owns (speed comes first, do not take offence).
- **`/compact` (×41) and `/clear` (×29)**: he runs **long sessions** which he compacts
  often, then **starts clean** for a new campaign. The work is cut into large thematic
  blocks.
- **Session start**: resync (§5.8).
- **End of a campaign**: commit + push + trace (BUG/BENCH/docs/memory) **before**
  closing — otherwise "tu as tout commit et push ?" lands.

---

## 7. What earns his trust / what loses it

| ✅ Earns trust | ❌ Loses it |
|---|---|
| Running the command and **reading the output** before concluding | Announcing "green/done" without proof |
| `./mvnw clean install` | An isolated `install`/`test` on a stale `target/` |
| Verifying the **TCK myself** (REST 2535, JWT 206…) | Trusting an agent's report that it is green |
| **Finishing** the scope and proving it | Leaving a "there's still…" hanging |
| **Disabusing him with the evidence** when he is wrong | Nodding along out of complacency |
| An honest post-mortem ("it was a trade-off that has aged") | Rewriting history flatteringly |
| Thinking **workspace** (parent first, mirrors, CI, docs) | Fixing one project while ignoring its cross-cutting impact |
| Transparent commits: **`Co-Authored-By` when the AI assisted** | Erasing the AI from a commit it helped produce |

---

## 8. Language, commits, artefacts (hard reminders)

- **Commits**: author and committer are **the human alone**, but **AI assistance is
  recorded via `Co-Authored-By`** (honest provenance, not legal co-authorship — an AI
  is not an author: Thaler v. Perlmutter 2026), message in **English**.
  Cf. `AI-POLICY.md`.
- **Language**: chat **FR** · code/Javadoc/comments/symbols **EN** · CI, commits, team
  messages **EN** · **Antora** docs **FR + EN** (`docs/fr`, `docs/en`).
- **CI notifications**: every automated message is prefixed with the bot's name.
- **CI**: non-sensitive parameters via `vars.X`, secrets via `secrets.X`. Never a secret
  in clear text in a workflow, a README or a commit.
- **Traceability**: every reproducible bug → the sub-project's `BUG.md`; every
  performance figure → `BENCH.md` (via the `/log-bug`, `/log-bench` skills). No
  performance figure in a README/commit without a `BENCH.md` entry.

---

## 9. The timeline of the major campaigns

The narrative arc observed across the 44 sessions (useful for situating a request):

```mermaid
timeline
    title Vidocq — campaigns observed in the sessions
    Genesis       : Workspace dependency graph : 7 then ~15 Maven modules
    Expansion     : MicroProfile implementations : cyrano, humboldt, grimm, ravel, knock, dirac, heisenberg : named after historical figures
    CI industrialisation : Forgejo Actions : downstream PR validation : team notifications
    Incident & migration : loss of the hosting hardware : switch to an external forge : mirrors restored
    Releases      : 0.1.0 by hand (Vauban first) : Maven Central validation : jlink / jpackage of the examples
    Performance   : Chappe Virtual Threads : 100k req/s ceiling : bench vs Jetty/Netty
    Documentation : Antora FR+EN : levelling up the weak docs : per-module update date
    Licensing     : Triple licence EPL 2.0 + GPL + EUPL 1.2 across all projects
    Application   : Arago — flagship app on the Vidocq stack (OIDC, GDPR, i18n, a11y)
    Meta          : Claude tooling settings (90-day conversation retention)
```

---

## 10. Memory map

```mermaid
mindmap
  root(("Working with Yann"))
    Stance
      Architect-maintainer
      Thinks ecosystem
      Peer thinking out loud
    Signals
      Hypothesis submitted with "right"
      "go" is the green light
      Study versus Execution
    Requirements
      Proof before assertion
      clean install always
      Verify the TCK myself
      Completeness of the scope
    Guardrails
      Co-Authored-By if AI assisted
      English for CI and commits
      BUG.md and BENCH.md
```

---

## 11. Session start-up checklist

1. **Resync**: `git pull --rebase` on the relevant projects, locate the sources.
2. **Load the context**: the sub-project's `AGENTS.md` + the relevant memory
   (and **verify** that a note has not gone stale).
3. **Identify the register**: study (artefact) or execution ("go")?
4. **Work in TDD**, at workspace scale if the campaign is cross-cutting.
5. **Prove it**: green `clean install`, TCK run by me, CI build OK.
6. **Trace it**: commit (EN, `Co-Authored-By` if the AI assisted) + push, `BUG.md`/
   `BENCH.md`, Antora docs FR+EN, memory.
7. Answer "tu as tout commit et push ?" **before** he asks it.
