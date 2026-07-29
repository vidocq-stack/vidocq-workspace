# Prompt pour Claude Code — Bootstrap `vidocq-docs` (v2)



Tu vas créer un système de documentation pour la suite Vidocq. Tu te trouves dans un répertoire qui contient les clones des projets de la suite. Tu vas :

1. **Créer un nouveau sous-répertoire frère** `vidocq-docs/` qui héberge la playbook Antora, le UI bundle, le Dockerfile et la CI.
2. **Modifier les repos existants** `vidocq/`, `vauban/`, `cassini/`, `champollion/`, `chappe/` pour y ajouter un répertoire `docs/` contenant la documentation bilingue de chaque module.

**Pas de push à la fin**, sur aucun repo.  je reviewerai et pousserai moi-même.

## Contexte du projet

La suite Vidocq est un ensemble de runtimes Jakarta EE / MicroProfile dont les noms sont des hommages à des figures françaises de la fin XVIIIᵉ / début XIXᵉ siècle :

- **Vidocq** — runtime serveur MicroProfile (Eugène-François Vidocq, fondateur de la Sûreté Nationale, 1812)
- **Vauban** — container CDI 4.1 build-time (Sébastien Le Prestre de Vauban, ingénieur militaire de Louis XIV)
- **Cassini** — REST/JAX-RS (la dynastie des cartographes Cassini, première carte topographique de la France)
- **Champollion** — JSON-B / JSON-P (Jean-François Champollion, déchiffreur des hiéroglyphes)
- **Chappe** — serveur HTTP, qui servira ce site (Claude Chappe, télégraphe optique, 1794)

Identité visuelle : **époque Empire / Restauration, sobre, lettrée, technique**. Pas de pastiche grossier.

## Étape 0 — Pré-vol

Avant toute modification, vérifie l'état de chaque repo :

```bash
for repo in vidocq vauban cassini champollion chappe; do
  echo "=== $repo ==="
  cd "$repo" && git status --short && git branch --show-current && cd ..
done
```

**Refuse de continuer** si un repo a des modifications non committées et signale-les-moi. Je veux pouvoir reprendre proprement après ta passe.

Pour chaque repo, note :
- branche par défaut (`main` ou `master`)
- présence ou non d'un répertoire `docs/` existant — si oui, **arrête-toi et signale**, on en discutera avant
- conventions de commit observées (présence d'un `.gitmessage`, format des derniers commits)

## Étape 1 — Inspection des modules

Pour chacun des 5 modules :

1. `pom.xml` racine et de chaque sous-module (groupId, artifactId, version, modules)
2. `README*` s'il existe
3. Arborescence `src/main/java` — packages publics, annotations propriétaires, SPI, `module-info.java`
4. Modules `*-examples`, `*-it`, `*-tck`, `*-bom` s'il y en a
5. Tests d'intégration qui montrent l'usage réel

Note tout dans `vidocq-docs/NOTES.md` (à supprimer en fin de tâche). Tu **dois** baser le contenu de la doc sur ce que tu trouves réellement. Si un point est flou, mets une admonition `[NOTE]` ou `[TODO]` plutôt que d'inventer.

Pour **Chappe en particulier**, identifie :
- comment lancer Chappe en mode « serveur statique » (CLI, propriétés, fichier de config)
- présence d'un Dockerfile, d'une image officielle, ou d'instructions de packaging
- format attendu pour le document root, les rewrite rules, les cache headers
- version courante (sera utilisée dans le footer)

C'est ce qui pilotera le `Dockerfile` final.

## Étape 2 — Documentation par module (dans chaque repo)

Pour chaque module, dans son repo :

```bash
cd <module>
git checkout -b docs/initial-bootstrap   # adapte si la branche existe déjà
mkdir -p docs/en/modules/ROOT/pages docs/fr/modules/ROOT/pages
```

Structure cible dans chaque repo module :

```
<module>/
└── docs/
    ├── en/
    │   ├── antora.yml                       # name: <module>,    title: <Module>
    │   └── modules/ROOT/
    │       ├── nav.adoc
    │       └── pages/
    │           ├── index.adoc
    │           ├── getting-started.adoc
    │           ├── concepts.adoc
    │           ├── reference.adoc
    │           └── migration.adoc
    └── fr/
        ├── antora.yml                       # name: <module>-fr, title: <Module>
        └── modules/ROOT/
            ├── nav.adoc
            └── pages/
                ├── index.adoc
                ├── getting-started.adoc
                ├── concepts.adoc
                ├── reference.adoc
                └── migration.adoc
```

`antora.yml` minimal (exemple pour Vauban) :

```yaml
# docs/en/antora.yml
name: vauban
title: Vauban
version: ~                       # versionless tant qu'on est en 0.x
nav:
  - modules/ROOT/nav.adoc
asciidoc:
  attributes:
    lang: en
```

```yaml
# docs/fr/antora.yml
name: vauban-fr
title: Vauban
version: ~
nav:
  - modules/ROOT/nav.adoc
asciidoc:
  attributes:
    lang: fr
```

### Convention bilingue

- **Le français est la version canonique** (cohérent avec l'identité du projet). Tu écris d'abord en FR, puis tu traduis en EN.
- **Pas de mélange de langues** dans une même page.
- Les exemples de code, noms d'API, FQN sont **identiques** dans les deux langues — seul le texte autour change.
- Les titres de pages sont traduits (ex. `Démarrage rapide` / `Getting started`), mais les ID Asciidoc (`[#getting-started]`) restent en anglais pour stabilité des liens.
- La nav `nav.adoc` est traduite, mais l'ordre des entrées et les xref-cibles sont identiques.

### Contenu attendu par page

**`index.adoc`** (qualité élevée, dans les deux langues)

- Titre + lettrine
- Une phrase de positionnement (« Vauban est un container CDI 4.1 qui résout l'injection au moment de la compilation… »)
- Section « Pourquoi ? » / « Why? » — 2-3 paragraphes max, le manifeste, le lien historique avec le personnage
- Section « En bref » / « At a glance » — 4-5 bullets factuels
- Lien vers `getting-started.adoc`

**`getting-started.adoc`** (qualité élevée, dans les deux langues)

- Pré-requis (Java 25, Maven 4)
- Snippet Maven minimal (coordonnées GAV lues depuis le pom du module)
- « Hello world » utilisant un exemple **réellement présent** dans `*-examples` ou `src/test/java`. Si rien ne convient, `[TODO]` explicite.
- Build et lancement

**`concepts.adoc`**, **`reference.adoc`**, **`migration.adoc`** (squelette + premiers contenus si évidents)

- Liste les concepts/annotations/SPI repérés à l'étape 1
- `[TODO]` admonition pour ce qui n'est pas encore stabilisé
- Pour `migration.adoc` : Vauban ← Quarkus ArC/Weld, Cassini ← RESTEasy/Jersey, Champollion ← Yasson/Jackson, etc. `[TODO]` si trop tôt.

### Commit dans chaque repo module

```bash
git add docs/
git commit -m "docs: bootstrap bilingual documentation (en/fr)

Adds Antora component structure under docs/ with English and French
versions. Initial scaffolding for index, getting-started, concepts,
reference and migration pages. Detailed content TODO where APIs are
not yet stable.

Refs: vidocq-docs#1"
# PAS DE PUSH
cd ..
```

## Étape 3 — Repo `vidocq-docs/`

Crée le répertoire frère :

```
vidocq-docs/
├── antora-playbook.yml                 # production (sources Git distantes)
├── antora-playbook-local.yml           # dev local (../vidocq, ../vauban…)
├── content/
│   ├── home-en/
│   │   ├── antora.yml                  # name: home, title: Vidocq
│   │   └── modules/ROOT/{nav.adoc,pages/index.adoc}
│   └── home-fr/
│       ├── antora.yml                  # name: home-fr
│       └── modules/ROOT/{nav.adoc,pages/index.adoc}
├── ui-bundle/
│   ├── src/{css,js,img,layouts,partials,helpers,data}/
│   ├── gulpfile.js
│   └── package.json
├── scripts/
│   └── fetch-chappe-version.js
├── Dockerfile
├── chappe-config.yml                   # config Chappe pour servir le site
├── .forgejo/workflows/build.yml
├── .gitignore
├── .editorconfig
├── README.adoc
├── LICENSE
└── docs/adr/
    ├── 0001-antora-multi-component.md
    └── 0002-bilingual-fr-en.md
```

### Playbook locale

`antora-playbook-local.yml` :

```yaml
site:
  title: Vidocq
  start_page: home-fr::index.adoc
  url: https://staging-doc.vidocq.dev

content:
  sources:
    - url: ../vidocq
      branches: HEAD
      start_paths: [docs/en, docs/fr]
    - url: ../vauban
      branches: HEAD
      start_paths: [docs/en, docs/fr]
    - url: ../cassini
      branches: HEAD
      start_paths: [docs/en, docs/fr]
    - url: ../champollion
      branches: HEAD
      start_paths: [docs/en, docs/fr]
    - url: ../chappe
      branches: HEAD
      start_paths: [docs/en, docs/fr]
    - url: .
      branches: HEAD
      start_paths: [content/home-en, content/home-fr]

ui:
  bundle:
    url: ./ui-bundle/build/ui-bundle.zip
    snapshot: true

asciidoc:
  attributes:
    experimental: ''
    idprefix: ''
    idseparator: '-'
    source-highlighter: highlight.js
    chappe-version: '@'
    primary-language: fr
```

### Playbook production

`antora-playbook.yml` : identique mais `url: ssh://git@forge.vidocq.dev:55122/vidocq/<module>.git` et `branches: [main]` (ou `master` selon la branche par défaut détectée à l'étape 0). Tags sémantiques `v*` ajoutés aux branches une fois qu'on aura nos premières releases.

### Page d'accueil (home)

`content/home-fr/modules/ROOT/pages/index.adoc` :

- Manifeste de la suite : pourquoi un nouveau runtime, le pari souverain, l'inspiration historique
- Grille de cartes vers chaque component (lien xref vers `<module>::index.adoc` ou `<module>-fr::index.adoc` selon la langue)
- Mention du statut (early, snapshot, pas de garantie de stabilité d'API)
- Liens rapides : GitHub mirror, forge.vidocq.dev, Matrix/Discord

`content/home-en/modules/ROOT/pages/index.adoc` : version anglaise.

## Étape 4 — UI bundle XIXᵉ siècle

### Typographie (auto-hébergées dans le bundle, **pas** de Google Fonts en CDN)

- Corps : **EB Garamond** (sérif Renaissance)
- Titres : **Cormorant Garamond** ou **Playfair Display**
- Mono : **JetBrains Mono** ou **IBM Plex Mono**
- Sous-set latin + latin-ext (couvre FR et EN), woff2 uniquement
- Ligatures + chiffres elzéviriens activés : `font-feature-settings: "liga", "onum"`
- Petites capitales pour les titres de sections
- Numérotation des chapitres en chiffres romains dans la nav (helper `roman`)

### Palette

```css
--ink:        #1a1410;
--paper:      #faf6ed;
--paper-warm: #f4ecd8;
--cream:      #ede4cc;
--burgundy:   #7a1e1e;
--ochre:      #a07020;
--rule:       #c9b896;

/* mode sombre = encre sur parchemin ambré, pas un dark IDE */
--dark-ink:    #e8dcc4;
--dark-paper:  #1a1410;
--dark-cream:  #2a201a;
```

Liens en bordeaux, soulignés finement (`text-decoration-thickness: 1px; text-underline-offset: 0.2em`).

### Layout

- `max-width: 38rem` sur le contenu (≈70 caractères)
- `line-height: 1.7`
- Marges généreuses
- Nav latérale fine en sérif
- Header minimal : monogramme + titre + sélecteur de version + sélecteur de component + **toggle FR/EN**
- Toggle clair/sombre persistant (localStorage)

### Toggle de langue

Dans le header, un toggle `FR | EN`. Logique :

- Chaque page connaît son component (`vauban` ou `vauban-fr`).
- Le toggle calcule l'URL homologue : si on est sur `/vauban/page.html`, le toggle pointe vers `/vauban-fr/page.html`, et inversement. Pour `home` ↔ `home-fr` même règle.
- Si la page homologue n'existe pas (404), on retombe sur l'`index` du component cible.
- La langue préférée est persistée en localStorage et appliquée à la navigation suivante.
- L'attribut `<html lang="...">` est positionné à partir de l'attribut Asciidoc `lang` du component.

Implémentation en vanilla JS, ~30 lignes max.

### Éléments graphiques (SVG inline uniquement)

- **Monogramme V** entrelacé en SVG (~300 octets de path), style chiffre royal sobre
- **Filets décoratifs** ornés (`<hr class="ornament">`), motif point-trait-losange-trait-point, monochrome ocre
- **Lettrines** sur le premier paragraphe des `index.adoc` de chaque component, via CSS `::first-letter`
- **Admonitions stylées comme des cachets** :
  - `CAUTION` / `WARNING` : sceau bordeaux + bordure gauche bordeaux 3px
  - `NOTE` : filet ocre fin
  - `TIP` : étoile à 8 branches ocre
  - `IMPORTANT` : double filet bordeaux
- **Footer** : deux bras articulés du télégraphe Chappe en SVG simplifié (un mât + deux traits)

### Layouts Handlebars

- `default.hbs`, `home.hbs`
- Partials : `head.hbs`, `header.hbs`, `nav.hbs`, `footer.hbs`, `toolbar.hbs`, `pagination.hbs`, `language-toggle.hbs`

### Helpers Handlebars

- `roman` : nombre → chiffres romains
- `chappeVersion` : lit `data/versions.json`
- `i18n` : retourne une chaîne traduite selon la langue courante (libellés du chrome : « Sur cette page », « Éditer », « Version », « Langue »…)

### Build du bundle

`gulpfile.js` qui :

1. Compile `src/css/*.css` (PostCSS + autoprefixer + cssnano) → `build/ui/css/site.css`
2. Bundle `src/js/*.js` → `build/ui/js/site.js` (concat simple, pas de Webpack)
3. Copie layouts/partials/helpers/img/data + fonts woff2 → `build/ui/`
4. Zippe `build/ui/` → `build/ui-bundle.zip`

`package.json` : `npm run build` → `node ../scripts/fetch-chappe-version.js && gulp bundle`. Poids cible : **CSS + JS + fonts < 200 Ko gzipped total**.

## Étape 5 — Version de Chappe dans le footer

Footer affiché :

```
Propulsé par Chappe X.Y.Z[-SNAPSHOT]* · Documentation Vidocq · Apache 2.0 · MMXXVI
```

Version anglaise :

```
Powered by Chappe X.Y.Z[-SNAPSHOT]* · Vidocq Documentation · Apache 2.0 · MMXXVI
```

Si la version contient `-SNAPSHOT`, ajouter un astérisque ocre `*` avec `title` traduit. Année courante en chiffres romains via le helper `roman`.

`scripts/fetch-chappe-version.js` :

1. **Local** : lit `../chappe/pom.xml`, extrait le premier `<version>` racine.
2. **CI** : si `../chappe/pom.xml` absent, `curl https://forge.vidocq.dev/vidocq/chappe/raw/branch/main/pom.xml`.
3. Écrit `ui-bundle/src/data/versions.json` :

   ```json
   {
     "chappe": "0.1.0-SNAPSHOT",
     "isSnapshot": true,
     "buildDate": "2026-05-07T..."
   }
   ```

Appelé avant chaque build.

## Étape 6 — Servir le site avec Chappe

D'abord, **inspecte le repo `chappe`** pour déterminer :

1. La méthode canonique de packaging (fat jar, native image GraalVM, distribution `.tar.gz`, image Docker pré-publiée ?)
2. La CLI ou le fichier de configuration pour servir un répertoire statique
3. Le format des cache headers, gzip, fallback
4. Le port d'écoute par défaut
5. Comment ajouter un header conditionnel type `X-Robots-Tag: noindex`

S'il existe **déjà** un Dockerfile dans `chappe/` ou une image publiée sur `forge.vidocq.dev/vidocq/chappe`, **utilise-le comme base**. Sinon, build Chappe depuis les sources dans le multi-stage.

`Dockerfile` cible (à adapter selon ce que tu trouves) :

```dockerfile
# ------------------------------------------------------------------
# Stage 1 — Build du site Antora
# ------------------------------------------------------------------
FROM node:lts-alpine AS site-builder
WORKDIR /build
COPY ui-bundle/package*.json ui-bundle/
RUN cd ui-bundle && npm ci
COPY . .
RUN cd ui-bundle && npm run build
RUN npx antora antora-playbook.yml

# ------------------------------------------------------------------
# Stage 2 — Build de Chappe (si pas d'image publiée)
# ------------------------------------------------------------------
# OU bien : FROM forge.vidocq.dev/vidocq/chappe:0.1.0-SNAPSHOT AS chappe-runtime
# (selon ce que tu trouves dans le repo chappe)
FROM eclipse-temurin:25-jdk-alpine AS chappe-builder
# ... à compléter d'après l'inspection de chappe ...

# ------------------------------------------------------------------
# Stage 3 — Runtime
# ------------------------------------------------------------------
FROM eclipse-temurin:25-jre-alpine
WORKDIR /opt/chappe
COPY --from=chappe-builder /chappe/build/ /opt/chappe/
COPY --from=site-builder /build/build/site /var/www/vidocq-docs
COPY chappe-config.yml /etc/chappe/config.yml

LABEL org.opencontainers.image.source="https://forge.vidocq.dev/vidocq/vidocq-docs"
LABEL org.opencontainers.image.licenses="EPL-2.0 OR EUPL-1.2 OR GPL-2.0-or-later"
LABEL org.opencontainers.image.title="Vidocq Documentation"

ENV CHAPPE_DOCROOT=/var/www/vidocq-docs
ENV CHAPPE_PORT=8080

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8080/ || exit 1
ENTRYPOINT ["chappe", "serve", "--config", "/etc/chappe/config.yml"]
```

Crée également `chappe-config.yml` à la racine du repo `vidocq-docs` avec les directives correctes (cache, gzip, fallback, robots) selon ce que Chappe attend.

**Dogfooding** : Si Chappe n'a pas encore les directives requises (cache headers fins, fallback configurable, `X-Robots-Tag` conditionnel…), liste-les dans `NOTES.md` sous une section `## Issues à ouvrir sur chappe`, formatées en markdown prêt à coller. Je créerai les issues moi-même. C'est un excellent driver pour finir Chappe.

Pour le `noindex` sur staging : passer `STAGING=true` à Chappe. Si la mécanique exacte n'est pas claire, propose une convention (variable d'env, clé de config, header injecté).

## Étape 7 — Workflow Forgejo

`.forgejo/workflows/build.yml` :

```yaml
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: docker
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with: { node-version: 'lts/*' }

      - name: Fetch Chappe version
        run: node scripts/fetch-chappe-version.js

      - name: Build UI bundle
        run: cd ui-bundle && npm ci && npm run build

      - name: Build Antora site
        run: npx antora antora-playbook.yml

      - name: Login to Forgejo registry
        run: echo "${{ secrets.FORGEJO_TOKEN }}" | docker login forge.vidocq.dev -u "${{ secrets.FORGEJO_USER }}" --password-stdin

      - name: Build & push image
        run: |
          if [[ "$GITHUB_REF" == refs/heads/main ]]; then
            TAG="snapshot-${GITHUB_SHA::7}"
            EXTRA="snapshot"
          else
            TAG="${GITHUB_REF_NAME#v}"
            EXTRA="latest"
          fi
          docker build \
            -t forge.vidocq.dev/vidocq/vidocq-docs:$TAG \
            -t forge.vidocq.dev/vidocq/vidocq-docs:$EXTRA .
          docker push forge.vidocq.dev/vidocq/vidocq-docs:$TAG
          docker push forge.vidocq.dev/vidocq/vidocq-docs:$EXTRA

      - name: Trigger Portainer redeploy
        run: |
          if [[ "$GITHUB_REF" == refs/heads/main ]]; then
            curl -fsSL -X POST "${{ secrets.PORTAINER_WEBHOOK_STAGING }}"
          else
            curl -fsSL -X POST "${{ secrets.PORTAINER_WEBHOOK_PROD }}"
          fi
```

Adapte la syntaxe Forgejo Actions exacte si tu connais des particularités locales.

## Étape 8 — Documentation du projet docs lui-même

`README.adoc` :

- Présentation
- Pré-requis (Node LTS, Antora 3.x, accès aux clones frères pour le build local)
- `npm run build:local` (UI + playbook locale)
- Comment ajouter un nouveau component (créer `docs/en/` et `docs/fr/` dans le nouveau repo, ajouter une source dans la playbook)
- Comment contribuer à la doc d'un module existant (PR sur le repo du module, pas ici)
- Note : ce repo contient **uniquement** la playbook, le UI et l'orchestration. Le contenu vit dans chaque repo module.

`docs/adr/0001-antora-multi-component.md` (MADR) : Antora vs MkDocs/Docusaurus/Hugo, multi-repo doc, justifications.

`docs/adr/0002-bilingual-fr-en.md` (MADR) : composants parallèles `<module>` et `<module>-fr`, FR canonique, EN traduction, alternatives écartées (Antora i18n expérimental, fork par langue, sous-domaines `fr.docs.vidocq.dev`).

## Étape 9 — Git, sur 6 repos

Pour chaque repo module (`vidocq`, `vauban`, `cassini`, `champollion`, `chappe`) :

```bash
cd <module>
git checkout -b docs/initial-bootstrap
git add docs/
git commit -m "docs: bootstrap bilingual documentation (en/fr)"
# PAS DE PUSH
cd ..
```

Pour `vidocq-docs/` :

```bash
mkdir vidocq-docs && cd vidocq-docs
git init -b main
# .gitignore : node_modules/, build/, public/, .cache/, *.zip, NOTES.md, ui-bundle/build/
git add .
git commit -m "chore: bootstrap vidocq-docs (Antora + UI XIXᵉ + Chappe)

- Antora multi-component playbook (5 modules + home), bilingual FR/EN
- UI bundle: EB Garamond, palette parchemin/bordeaux, dark mode, language toggle
- Footer with dynamically extracted Chappe version
- Dockerfile multi-stage serving via Chappe
- Forgejo Actions: build + push + Portainer webhooks
- ADR-0001 (Antora), ADR-0002 (bilingual)"
git remote add origin ssh://git@forge.vidocq.dev:55122/vidocq/vidocq-docs.git
# PAS DE PUSH
```

## Compte rendu attendu

À la fin, donne-moi :

1. Arborescence finale des 6 repos touchés (uniquement les répertoires/fichiers ajoutés)
2. Pour chaque repo, le hash du commit local et la branche
3. Ce qui builde de bout en bout vs ce qui est marqué TODO
4. Le résultat de l'inspection de Chappe (méthode de packaging retenue, manques éventuels)
5. Découvertes intéressantes pendant l'inspection des modules (API absentes, versions, surprises)
6. Commandes pour tester localement :
   - `cd vidocq-docs/ui-bundle && npm install && npm run build && cd ..`
   - `npx antora antora-playbook-local.yml`
   - `docker build -t vidocq-docs:test .`
   - `docker run -p 8080:8080 vidocq-docs:test`
7. Liste ordonnée de ce que je dois faire avant de pousser
8. Issues à ouvrir côté `chappe` si tu as identifié des manques (formate-les en markdown prêt à coller)

Supprime `vidocq-docs/NOTES.md` une fois le compte rendu fait.

## Garde-fous

- **Aucun push, sur aucun repo.** Six repos = six commits locaux qui m'attendent.
- **Refus si état git sale.** Si un module a des changements non committés, arrête-toi et signale.
- **Refus si `docs/` préexiste** dans un module — signale et attends mes instructions.
- **Pas d'invention.** `[TODO]` plutôt qu'une signature fictive.
- **Pas d'IA-art.** Tout visuel décoratif est SVG vectoriel inline ou typographie.
- **Pas de Tailwind, pas de framework JS lourd.** CSS écrit à la main, vanilla JS minimal.
- **Pas de Google Fonts en CDN.** Auto-héberge en woff2 dans le UI bundle.
- **Pas de tracking, pas d'analytics.**
- **Pas de `npm audit fix --force` automatique** — signale, je décide.
- **Bilingue strict** : FR canonique, EN traduit, contenu complet dans les deux langues même si c'est un `[TODO]`. Pas de page qui n'existe que dans une langue.
- **Cohérence des liens xref** : tous les xref entre pages utilisent `<component>::page.adoc`. Le toggle de langue se charge de basculer le component.

Au boulot.
