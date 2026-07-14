# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dépôt

Ce répertoire est un **workspace** regroupant sept projets Maven indépendants — il n'y a **pas de POM racine**, **pas de `mvnw` racine**, et **pas de reactor unifié**. Chaque sous-projet a son propre reactor, son propre `.sdkmanrc`, son propre `mvnw`, et la plupart ont leur propre `CLAUDE.md` à consulter en priorité quand on travaille dedans.

```
chappe/        Serveur HTTP/1.1+H2/H3 pur Java 25, zéro dépendance — couche transport
vauban/        Container CDI 4.1 Lite, JPMS natif, zéro dépendance — DI
champollion/   Implémentation Jakarta JSON-P 2.1 + JSON-B 3.0, zéro dépendance
foy/           Implémentation Jakarta Servlet 6.1 (transport via chappe, CDI via vauban)
cassini/       Implémentation Jakarta REST 4.0 / JAX-RS (transport via chappe, CDI via vauban)
mansart/       Jakarta Data 1.0 + Jakarta Persistence 3.2 (en conception — voir mansart/PLAN.md)
vidocq/    Vidocq Runtime — orchestrateur, mécanisme d'extensions, packaging
```

Graphe de dépendances logique : `chappe` + `vauban` + `champollion` sont des briques fondatrices sans dépendances entre elles. `foy` et `cassini` les composent. `vidocq` orchestre l'ensemble via une SPI d'extensions inspirée de Quarkus.

## Conventions de commit

- **Pas de `Co-Authored-By: Claude` ni de mention de l'IA** dans les commit messages. Les commits sont signés par l'auteur humain seul, comme tout commit standard. Cette règle s'applique à tous les sous-projets du workspace.

## Philosophie de l'écosystème Vidocq

Règles transverses qui s'appliquent à **tous** les sous-projets, sauf dérogation explicite documentée :

- **JPMS strict** — chaque module a un `module-info.java` propre, `exports` minimaux, pas d'`opens` non justifié, pas de classpath.
- **Génération de code statique au maximum** — préférer **Class-File API** (JEP 484) et APT pour produire à la compilation ce qui serait sinon de la réflexion runtime. Pas de proxy dynamique, pas d'ASM/Byte Buddy, pas de réflexion à chaud quand on peut générer à `compile`/`process-classes`. Compatible AOT (GraalVM, Leyden CDS).
- **Zéro ou très peu de dépendances externes** — seulement les specs Jakarta / MicroProfile concernées. Toute nouvelle dépendance runtime doit être justifiée explicitement dans la PR.
- **TDD obligatoire** — écrire le test (ou le scénario TCK) avant le code. Rouge → vert → refactor.
- **Arquillian** pour les TCK officiels Jakarta et tout test d'intégration nécessitant un container.
- **Virtual Threads** partout pour l'I/O — `Executors.newVirtualThreadPerTaskExecutor()` par défaut, pas de pool de threads plateforme sans raison documentée.
- **Langue du code en anglais** — toute la Javadoc et tous les commentaires (`//`, `/* */`, `/** */`) sont rédigés en **anglais**, ainsi que les noms de symboles, de tests et de méthodes. Le **français** est réservé à la **documentation Antora** (`<sous-projet>/docs/fr/`) et aux fichiers de pilotage (`tasks/`, prompts d'agents). Les échanges avec le mainteneur restent en français.

## Traçabilité bugs & performance

- **Bugs** : tout bug reproductible (issue interne, régression, comportement incorrect non encore corrigé) doit être tracé dans un `BUG.md` à la racine du sous-projet concerné, avec : id court, date, symptôme, repro minimal, hypothèse de cause, statut. Mise à jour à chaque investigation.
- **Benchmarks** : tout chiffre de performance (JMH, wrk, comparatif vs Netty/Jetty/Parsson/Yasson/Jackson, etc.) doit être consigné dans un `BENCH.md` à la racine du sous-projet, avec : date, hardware/JVM, commande exacte, résultats bruts, et delta vs run précédent. Pas de chiffre de perf dans un README ou un commit message sans entrée correspondante dans `BENCH.md`.

## Prérequis (commun à tous les sous-projets)

- **Java 25** (Temurin) + **Maven 3.9.16** — pinés via `.sdkmanrc` dans chaque sous-projet : `cd <sous-projet> && sdk env`.
- Tous les POMs du workspace sont en `modelVersion 4.0.0` (le workspace est sorti de la RC Maven 4 pour la GA 3.9.x — voir l'historique de cette migration dans `vidocq-parent`).
- Pour les TCK officiels Jakarta : artefacts non publics à installer dans le M2 local (procédure dans le README du runner concerné).

## Travailler dans un sous-projet

Toujours `cd` dans le sous-projet d'abord. Build standard :

```bash
./mvnw -ntp install -DskipTests   # build complet
./mvnw test                        # tests unitaires
```

Scripts TCK spécifiques (à lancer depuis la racine du sous-projet, jamais depuis ce workspace) :

- `cassini/run-official-tck-restful-4.0.sh [all|-Dtest=…]` — TCK Jakarta REST 4.0
- `foy/run-official-tck-servlet6.1.sh [--all|-Dtest=…]` — TCK Jakarta Servlet 6.1
- `champollion/run-official-tck-jsonp-2.1.sh`, `run-official-tck-jsonb-3.0.sh`

## TCK runners hors reactor

`cassini-tck`, `foy-tck`, `champollion-tck`, `cervantes-tck`, `cyrano-tck`, `dirac-tck`, `grimm-tck`, `heisenberg-tck`, `humboldt-tck`, `knock-tck`, `ravel-tck`, `mansart-data-tck`, `mansart-transactions-tck`, `champollion-protobuf-tck` et le runner `vidocq-servlet-chappe-tck-runner` sont volontairement EXCLUS du `<modules>` de leur reactor parent et utilisent un POM `modelVersion 4.0.0` standalone (sans `<parent>`).

**Historique** : la contrainte initiale était ShrinkWrap Maven Resolver 3.3 (transitive du TCK officiel) qui ne parsait pas le `modelVersion 4.1.0` du workspace pré-migration. Cette contrainte a disparu avec le passage à Maven 3.9.16 + Model 4.0.0 partout.

**Pourquoi on garde la séparation** : découpler le cycle de release du runtime de celui du TCK officiel (un bump TCK upstream ne déclenche pas une release runtime, et vice-versa). Toute réintégration au reactor est un chantier dédié — modifie la matrice CI, l'install order et le découplage de release. Toujours passer par leur script `run-*-tck-*.sh`, jamais via `mvn -pl`.

**Exception — runners MP in-reactor du runtime (PR vidocq#19, certification MicroProfile 7.1)** : le repo `vidocq` embarque désormais 8 runners TCK MicroProfile dans `vidocq-runtime-integration-tests/vidocq-runtime-tck-*`, qui certifient **le runtime assemblé** (et non les briques isolées). Ils sont gardés derrière le profil Maven `tck` : un `mvn install` normal ne télécharge ni ne lance rien ; activation via `./mvnw -Ptck -pl vidocq-runtime-integration-tests/<module> test`. Les runners par-brique listés ci-dessus restent hors reactor et font toujours foi pour chaque implémentation.

## Agents et skills disponibles dans ce workspace

Définis dans `.claude/agents/` et `.claude/skills/` — utiliser proactivement quand le contexte s'y prête :

- Agents : `jpms-guardian` (audit `module-info.java`), `classfile-codegen` (Class-File API + APT), `tck-runner` (TCK Jakarta hors-reactor), `virtual-threads-reviewer` (revue concurrence), `dependency-gatekeeper` (revue `pom.xml` zéro-dep).
- Skills : `/log-bug` (ajoute une entrée à `<sous-projet>/BUG.md`), `/log-bench` (ajoute une entrée à `<sous-projet>/BENCH.md`).

## Guides par sous-projet

Lire le `CLAUDE.md` ou `README.md` du sous-projet ciblé avant de modifier son code — chacun documente ses propres conventions, modules, et roadmap (jalons M2a/M2h/etc., contraintes TDD, principes zéro-dépendance, etc.) :

- `chappe/CLAUDE.md`, `vauban/CLAUDE.md`, `cassini/CLAUDE.md` — guides Claude existants
- `chappe/README.md`, `vauban/README.md`, `cassini/README.md`, `foy/README.md`, `champollion/README.md`, `vidocq/README.md` — vue produit et architecture détaillée
