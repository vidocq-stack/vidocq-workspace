# WORK_WITH_CLAUDE.md — Travailler avec Yann sur l'écosystème Vidocq

> **Ce que c'est.** Un méta-guide de *collaboration*, complémentaire de `CLAUDE.md`.
> `CLAUDE.md` dit les **conventions techniques** (JPMS, zéro-dep, codegen, TDD…) ;
> ce fichier dit **comment Yann travaille avec Claude** : sa posture, ses rituels,
> ses signaux, ce qui gagne sa confiance et ce qui la perd.
>
> **Comment il a été produit.** Analyse des transcripts réels du workspace :
> **44 sessions, 1 156 prompts**, traités hors-contexte (extraction des messages
> humains, thèmes, verbatim). Ce n'est pas une supposition — c'est ce que montrent
> les échanges. À relire et amender au fil du temps.
>
> **Langue.** Fichier de pilotage → **français** (comme `tasks/` et les prompts
> d'agents). Rappel : le *chat* reste en français, mais **code, commits, CI et
> messages d'équipe sont en anglais** (projet européen multi-contributeurs).
>
> **Note de publication.** Cette version publique est expurgée de la section
> décrivant l'infrastructure interne (hôtes, secrets, chemins locaux). Le contenu
> méthodologique est intact.

---

## 1. En une phrase

> Yann est un **architecte-mainteneur** qui pense **écosystème**, pilote par
> **prompts courts et directs**, **challenge** les décisions par des hypothèses
> en « …non ? », et n'accepte une affirmation que **prouvée** (build vert, TCK,
> `clean install`, commit poussé). Il alterne **études** approfondies et
> **exécutions** déléguées d'un simple « go ».

---

## 2. Qui est en face

- **Rôle** : seul mainteneur humain principal de ~15 sous-projets Maven indépendants
  (réimplémentations Jakarta/MicroProfile zéro-dépendance). Co-contributeurs :
  **Antoine** et des PR externes occasionnelles.
- **Niveau** : très haut. Il connaît la spec, la JVM, la CI, l'infra. Il a
  **souvent raison** quand il corrige — ne pas le contredire à la légère, vérifier.
- **Posture** : ce n'est pas un donneur d'ordres qui exécute des tickets. C'est un
  **pair qui réfléchit à voix haute**, délègue l'exécution et la fouille, mais
  garde la décision d'architecture et exige d'en comprendre le « pourquoi ».
- **Contexte réel** : vraie infra (forge, CI, registre, mirrors, Maven Central) et
  vrais incidents d'exploitation. Il me **donne accès** aux outils et attend que je
  m'en serve.

---

## 3. La boucle de travail

```mermaid
flowchart TD
    A["Ouverture de session<br/>resync : git pull rebase, localiser sources, charger en mémoire"] --> B{"Mode ?"}
    B -->|"Comprendre / décider"| C["ÉTUDE<br/>diagnostic, comparatif, artefact écrit<br/>RELEASE.md / PLAN.md / BENCH.md"]
    B -->|"Faire"| D["EXÉCUTION<br/>TDD rouge→vert→refactor"]
    C --> E["Hypothèse soumise<br/>« …non ? »"]
    E -->|"Yann valide : « go »"| D
    E -->|"Yann redresse"| C
    D --> F["PREUVE<br/>clean install vert · TCK · build CI · commit+push"]
    F -->|"non prouvé / incomplet"| D
    F -->|"prouvé"| G["TRACE<br/>commit (Co-Authored-By si IA a assisté) · BUG.md / BENCH.md · doc Antora FR+EN · mémoire"]
    G --> H["/compact pour continuer · /clear pour repartir propre"]
    H --> A
```

**Le point non négociable, c'est `F` (la preuve).** Tant que ce n'est pas vert et
prouvé *par moi-même*, ce n'est pas fini (voir §5.2 et §7).

---

## 4. Les deux registres : Étude vs Exécution

Yann sépare nettement **réfléchir** et **faire**. Reconnaître le registre évite le
contresens (foncer quand il veut analyser, ou tergiverser quand il veut un résultat).

```mermaid
flowchart LR
    subgraph ETUDE["🔬 ÉTUDE — produire de la compréhension"]
      direction TB
      E1["« Je vais te lancer sur une etude »"]
      E2["« Nouvelle etude. À m'attendre dans RELEASE.md »"]
      E3["« On va etudier les perfs de chappe… bench vs jetty ? »"]
      E4["« Rappel moi pourquoi ça c'est mieux que… »"]
    end
    subgraph EXEC["⚙️ EXÉCUTION — produire un résultat"]
      direction TB
      X1["« go » / « non vas y »"]
      X2["« deploie le pr.yml partout stp »"]
      X3["« fait un git pull rebase de tous mes projets »"]
      X4["« tu peux fixer »"]
    end
    ETUDE -->|"hypothèse validée"| EXEC
```

| | **ÉTUDE** | **EXÉCUTION** |
|---|---|---|
| Déclencheur | « étude », « bilan », « rappelle-moi pourquoi », « était-ce un bon choix ? » | « go », « vas y », « fixe », « déploie », « renomme » |
| Livrable attendu | un **artefact écrit** (`RELEASE.md`, `PLAN.md`, comparatif, post-mortem) | du **code mergé + preuve verte** |
| Mon job | options, trade-offs, **une reco** (pas un catalogue) | TDD, build, push, trace |
| Erreur à éviter | coder avant d'avoir aligné la décision | re-débattre ce qui est déjà tranché |

---

## 5. Les patterns d'interaction (avec verbatim réels)

### 5.1 — L'hypothèse en « …non ? » (le plus fréquent)
Il ne donne pas toujours un ordre : il **pose une hypothèse technique et demande
réfutation ou confirmation**. C'est une invitation à vérifier, pas une certitude.

> « C'est à la BCE de Cassini de faire le Job **non ?** » · « en utilisant une
> `buildCompatibleExtension` tu dois pouvoir ajouter l'interceptor **non ?** » ·
> « cyrano est un rest client **non ?** » · « il manque un jpackage **non ?** »

**Réponse attendue :** vérifier dans le code, puis **trancher avec preuve** — lui
donner raison *ou* le détromper avec l'évidence. Surtout pas un « oui » de
complaisance : quand son fix Vauban était mauvais, il a redressé **trois fois**
(« Le dernier fix sur Vauban n'est pas bon… non ? ») — il avait raison.

### 5.2 — Preuve avant affirmation
Question récurrente, presque un réflexe :

> « tu as tout **commit et push** ? » · « tu as bien vérifier **TOUS** les sous
> répertoires ? » · « On **reverifie** tout ? » · « compile tck etc ? » ·
> « tu peux **vérifier les status des build** sur la CI ? »

**Réponse attendue :** ne jamais déclarer « vert / fait / corrigé » sans avoir
lancé la commande et lu la sortie. Les agents ont déjà **menti dans les deux sens**
(faux « vert », faux « incomplet ») → **revérifier moi-même**. Et **toujours
`clean install`**, jamais `install`/`test` isolé : un `target/` périmé fabrique de
faux échecs.

### 5.3 — Le « go » laconique
Une fois l'analyse alignée, il déclenche en deux mots. La concision **est** le feu vert.

> « go » · « non vas y » · « Non vas y, PR de test »

**Réponse attendue :** exécuter, ne pas re-demander confirmation, ne pas re-débattre.

### 5.4 — Penser écosystème (chantiers transverses)
Beaucoup de demandes touchent **tous les projets à la fois**.

> « gros chantier, on va basculer en **triple license** EPL/GPL/EUPL, faut mettre
> tous les projets à jour » · « on va passer **tous les projet** en maven 3.9.16 » ·
> « renommer Vidocq MicroProfile **Server → Runtime** (vidocq-mps → vidocqmpr) »

**Réponse attendue :** raisonner à l'échelle du workspace (ordre d'install, parent
d'abord, mirrors, CI, docs), pas projet par projet en silo.

### 5.5 — Justifier & post-mortem
Il challenge les décisions **passées** et veut réancrer le « pourquoi ».

> « **Rappel moi pourquoi** ça c'est mieux que le discover de l'apt automatique ? » ·
> « on a fait le choix de ne pas utiliser le sdk OpenTelemetry. **Était-ce un bon
> choix in fine ?** » · « pourquoi tu ne l'as pas implémenté à la base quand tu as
> fait cassini !! »

**Réponse attendue :** réponse honnête et argumentée, y compris « c'était une
erreur / un compromis daté ». Pas de réécriture flatteuse de l'histoire.

### 5.6 — Debugging par symptôme collé
Il colle la **trace brute** (build failed, stack, validation Central) + « tu peux fixer ».

> « La release a failed pour chappe : 10 failed Component Validations… » ·
> « webhook manquant — cannot send 'pr-open' notification »

**Réponse attendue :** debug systématique depuis le symptôme réel (cf. skill
`systematic-debugging`), reproduire, corriger la cause, prouver.

### 5.7 — Entretien de la mémoire
> « ajoute le projet a ta mémoire et jette y un oeil je viens de le cloner »

**Réponse attendue :** tenir la mémoire à jour (faits non dérivables du code), et
**vérifier** qu'une note n'est pas périmée avant de s'y fier.

### 5.8 — Resync d'ouverture
Une session démarre souvent par une remise à niveau de l'état.

> « tu peux **git pull rebase** les projets ? » · « On reprend sur Arago, **tu
> localise les sources** ? » · « tout est à jour ? »

**Réponse attendue :** synchroniser, localiser, charger le contexte **avant** d'agir.

### 5.9 — Exiger la complétude
Il relève les oublis et les demi-finitions, parfois avec une frustration légitime.

> « Il semblerait que humboldt ne soit pas fini. On vérifie et on **fini** ? » ·
> « il manque un jpackage non ? » · « vidocq docs **manque de composants** »

**Réponse attendue :** finir le périmètre (« faire le reste » n'est pas une tâche
à reporter, c'est à terminer maintenant), et le prouver.

---

## 6. Cadence & rituels de session

- **Prompts courts** : médiane **58 caractères**, 68 % ≤ 120 c. Les longs (p90 ≈
  2 900 c.) sont des **briefs d'étude** ou des specs/erreurs collées. → Je peux
  répondre dense ; lui écrit vite et avec des fautes de frappe assumées (la vitesse
  prime, ne pas s'en formaliser).
- **`/compact` (×41) et `/clear` (×29)** : il mène des **sessions longues** qu'il
  compacte souvent, puis **repart propre** pour un nouveau chantier. Le travail est
  découpé en gros blocs thématiques.
- **Début de session** : resync (§5.8).
- **Fin de chantier** : commit + push + trace (BUG/BENCH/doc/mémoire) **avant** de
  clore — sinon « tu as tout commit et push ? » tombe.

---

## 7. Ce qui gagne sa confiance / ce qui la perd

| ✅ Gagne la confiance | ❌ La perd |
|---|---|
| Lancer la commande et **lire la sortie** avant de conclure | Annoncer « vert/fait » sans preuve |
| `./mvnw clean install` | `install`/`test` isolé sur `target/` périmé |
| Vérifier le **TCK soi-même** (REST 2535, JWT 206…) | Faire confiance au rapport d'un agent sur le vert |
| **Finir** le périmètre et le prouver | Laisser un « il manque… » traîner |
| Le **détromper avec l'évidence** quand il a tort | Acquiescer par complaisance |
| Post-mortem honnête (« c'était un compromis daté ») | Réécrire l'histoire en flatteur |
| Penser **workspace** (parent d'abord, mirrors, CI, docs) | Corriger un projet en ignorant ses impacts transverses |
| Commits transparents : **`Co-Authored-By` quand l'IA a assisté** | Effacer l'IA d'un commit qu'elle a aidé à produire |

---

## 8. Langue, commits, artefacts (rappels durs)

- **Commits** : auteur et committer **humain seul**, mais **assistance IA tracée
  via `Co-Authored-By`** (provenance honnête, pas co-paternité légale — une IA n'est
  pas un auteur : Thaler v. Perlmutter 2026), message en **anglais**. Cf. `AI-POLICY.md`.
- **Langue** : chat **FR** · code/Javadoc/commentaires/symboles **EN** · CI,
  commits, messages d'équipe **EN** · doc **Antora** **FR + EN** (`docs/fr`, `docs/en`).
- **Notifications CI** : tout message automatique est préfixé par le nom du bot.
- **CI** : paramètres non sensibles via `vars.X`, secrets via `secrets.X`. Jamais de
  secret en clair dans un workflow, un README ou un commit.
- **Traçabilité** : tout bug reproductible → `BUG.md` du sous-projet ; tout chiffre
  de perf → `BENCH.md` (via les skills `/log-bug`, `/log-bench`). Pas de perf dans
  un README/commit sans entrée `BENCH.md`.

---

## 9. La chronologie des grands chantiers

L'arc narratif observé dans les 44 sessions (utile pour situer une demande) :

```mermaid
timeline
    title Vidocq — chantiers observés dans les sessions
    Genèse        : Graphe de dépendances du workspace : 7 puis ~15 modules Maven
    Expansion     : Implémentations MicroProfile : cyrano, humboldt, grimm, ravel, knock, dirac, heisenberg : noms d'après des personnages historiques
    Industrialisation CI : Forgejo Actions : PR validation downstream : notifications d'équipe
    Incident & migration : perte du matériel d'hébergement : bascule sur une forge externe : remise des mirrors
    Releases      : 0.1.0 manuelle (Vauban d'abord) : validation Maven Central : jlink / jpackage des exemples
    Performance   : Chappe Virtual Threads : plafond 100k req/s : bench vs Jetty/Netty
    Documentation : Antora FR+EN : nivellement des docs faibles : date de MAJ par module
    Licensing     : Triple licence EPL 2.0 + GPL + EUPL 1.2 sur tous les projets
    Application   : Arago — app phare sur la stack Vidocq (OIDC, RGPD, i18n, a11y)
    Méta          : réglages de l'outillage Claude (rétention conversations 90j)
```

---

## 10. Carte mémoire

```mermaid
mindmap
  root(("Travailler avec Yann"))
    Posture
      Architecte-mainteneur
      Pense écosystème
      Pair qui réfléchit à voix haute
    Signaux
      Hypothèse soumise en « non »
      « go » est le feu vert
      Étude versus Exécution
    Exigences
      Preuve avant affirmation
      clean install toujours
      Vérifier le TCK soi-même
      Complétude du périmètre
    Garde-fous
      Co-Authored-By si IA a assisté
      Anglais CI commits
      BUG.md et BENCH.md
```

---

## 11. Checklist de démarrage de session

1. **Resync** : `git pull --rebase` des projets concernés, localiser les sources.
2. **Charger le contexte** : `CLAUDE.md` du sous-projet + mémoire pertinente
   (et **vérifier** qu'une note n'est pas périmée).
3. **Identifier le registre** : étude (artefact) ou exécution (« go ») ?
4. **Travailler en TDD**, à l'échelle du workspace si le chantier est transverse.
5. **Prouver** : `clean install` vert, TCK lancé moi-même, build CI OK.
6. **Tracer** : commit (EN, `Co-Authored-By` si l'IA a assisté) + push, `BUG.md`/`BENCH.md`, doc
   Antora FR+EN, mémoire.
7. Répondre à « tu as tout commit et push ? » **avant** qu'il ne la pose.
