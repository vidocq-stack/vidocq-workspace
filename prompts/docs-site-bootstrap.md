# Prompt for Claude Code — Bootstrapping `vidocq-docs` (v2)



You are going to create a documentation system for the Vidocq suite. You are in a directory that contains the clones of the suite's projects. You will:

1. **Create a new sibling sub-directory** `vidocq-docs/` hosting the Antora playbook, the UI bundle, the Dockerfile and the CI.
2. **Modify the existing repos** `vidocq/`, `vauban/`, `cassini/`, `champollion/`, `chappe/` to add a `docs/` directory containing each module's bilingual documentation.

**No push at the end**, on any repo. I will review and push myself.

## Project context

The Vidocq suite is a set of Jakarta EE / MicroProfile runtimes whose names pay tribute to French figures of the late 18th / early 19th century:

- **Vidocq** — MicroProfile server runtime (Eugène-François Vidocq, founder of the Sûreté Nationale, 1812)
- **Vauban** — build-time CDI 4.1 container (Sébastien Le Prestre de Vauban, Louis XIV's military engineer)
- **Cassini** — REST/JAX-RS (the Cassini dynasty of cartographers, first topographic map of France)
- **Champollion** — JSON-B / JSON-P (Jean-François Champollion, decipherer of the hieroglyphs)
- **Chappe** — HTTP server, which will serve this site (Claude Chappe, optical telegraph, 1794)

Visual identity: **Empire / Restoration period, sober, literate, technical**. No crude pastiche.

## Step 0 — Pre-flight

Before any modification, check the state of each repo:

```bash
for repo in vidocq vauban cassini champollion chappe; do
  echo "=== $repo ==="
  cd "$repo" && git status --short && git branch --show-current && cd ..
done
```

**Refuse to continue** if a repo has uncommitted modifications, and report them to me. I want to be able to pick up cleanly after your pass.

For each repo, note:
- the default branch (`main` or `master`)
- whether a `docs/` directory already exists — if so, **stop and report**, we will discuss it first
- the commit conventions observed (presence of a `.gitmessage`, format of the latest commits)

## Step 1 — Inspecting the modules

For each of the 5 modules:

1. the root `pom.xml` and that of each sub-module (groupId, artifactId, version, modules)
2. `README*` if present
3. the `src/main/java` tree — public packages, proprietary annotations, SPI, `module-info.java`
4. the `*-examples`, `*-it`, `*-tck`, `*-bom` modules if any
5. integration tests that show real usage

Note everything in `vidocq-docs/NOTES.md` (to be deleted at the end of the task). You **must** base the documentation content on what you actually find. If a point is unclear, add a `[NOTE]` or `[TODO]` admonition rather than inventing.

For **Chappe in particular**, identify:
- how to run Chappe in "static server" mode (CLI, properties, config file)
- the presence of a Dockerfile, an official image, or packaging instructions
- the expected format for the document root, the rewrite rules, the cache headers
- the current version (will be used in the footer)

That is what will drive the final `Dockerfile`.

## Step 2 — Per-module documentation (inside each repo)

For each module, in its repo:

```bash
cd <module>
git checkout -b docs/initial-bootstrap   # adapt if the branch already exists
mkdir -p docs/en/modules/ROOT/pages docs/fr/modules/ROOT/pages
```

Target structure in each module repo:

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

Minimal `antora.yml` (example for Vauban):

```yaml
# docs/en/antora.yml
name: vauban
title: Vauban
version: ~                       # versionless as long as we are on 0.x
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

### Bilingual convention

- **French is the canonical version** (consistent with the project's identity). Write in FR first, then translate to EN.
- **No mixing of languages** within a single page.
- Code examples, API names and FQNs are **identical** in both languages — only the surrounding text changes.
- Page titles are translated (e.g. `Démarrage rapide` / `Getting started`), but the Asciidoc IDs (`[#getting-started]`) stay in English so links remain stable.
- The `nav.adoc` navigation is translated, but the order of the entries and the xref targets are identical.

### Expected content per page

**`index.adoc`** (high quality, in both languages)

- Title + drop cap
- One positioning sentence ("Vauban is a CDI 4.1 container that resolves injection at compile time…")
- A "Pourquoi ?" / "Why?" section — 2-3 paragraphs max, the manifesto, the historical link with the figure
- An "En bref" / "At a glance" section — 4-5 factual bullets
- A link to `getting-started.adoc`

**`getting-started.adoc`** (high quality, in both languages)

- Prerequisites (Java 25, Maven 4)
- Minimal Maven snippet (GAV coordinates read from the module's pom)
- A "Hello world" using an example **actually present** in `*-examples` or `src/test/java`. If nothing fits, an explicit `[TODO]`.
- Build and run

**`concepts.adoc`**, **`reference.adoc`**, **`migration.adoc`** (skeleton + first content where obvious)

- List the concepts/annotations/SPI spotted in step 1
- A `[TODO]` admonition for whatever is not yet stabilised
- For `migration.adoc`: Vauban ← Quarkus ArC/Weld, Cassini ← RESTEasy/Jersey, Champollion ← Yasson/Jackson, etc. `[TODO]` if it is too early.

### Commit in each module repo

```bash
git add docs/
git commit -m "docs: bootstrap bilingual documentation (en/fr)

Adds Antora component structure under docs/ with English and French
versions. Initial scaffolding for index, getting-started, concepts,
reference and migration pages. Detailed content TODO where APIs are
not yet stable.

Refs: vidocq-docs#1"
# NO PUSH
cd ..
```

## Step 3 — The `vidocq-docs/` repo

Create the sibling directory:

```
vidocq-docs/
├── antora-playbook.yml                 # production (remote Git sources)
├── antora-playbook-local.yml           # local dev (../vidocq, ../vauban…)
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
├── chappe-config.yml                   # Chappe config for serving the site
├── .forgejo/workflows/build.yml
├── .gitignore
├── .editorconfig
├── README.adoc
├── LICENSE
└── docs/adr/
    ├── 0001-antora-multi-component.md
    └── 0002-bilingual-fr-en.md
```

### Local playbook

`antora-playbook-local.yml`:

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

### Production playbook

`antora-playbook.yml`: identical but with `url: ssh://git@forge.vidocq.dev:55122/vidocq/<module>.git` and `branches: [main]` (or `master`, depending on the default branch detected in step 0). Semantic `v*` tags will be added to the branches once we have our first releases.

### Home page

`content/home-fr/modules/ROOT/pages/index.adoc`:

- The suite's manifesto: why a new runtime, the sovereignty bet, the historical inspiration
- A grid of cards to each component (xref link to `<module>::index.adoc` or `<module>-fr::index.adoc` depending on the language)
- A mention of the status (early, snapshot, no API stability guarantee)
- Quick links: GitHub mirror, forge.vidocq.dev, Matrix/Discord

`content/home-en/modules/ROOT/pages/index.adoc`: the English version.

## Step 4 — 19th-century UI bundle

### Typography (self-hosted in the bundle, **no** Google Fonts over CDN)

- Body: **EB Garamond** (Renaissance serif)
- Headings: **Cormorant Garamond** or **Playfair Display**
- Mono: **JetBrains Mono** or **IBM Plex Mono**
- latin + latin-ext subset (covers FR and EN), woff2 only
- Ligatures + old-style figures enabled: `font-feature-settings: "liga", "onum"`
- Small caps for section titles
- Chapter numbering in Roman numerals in the nav (`roman` helper)

### Palette

```css
--ink:        #1a1410;
--paper:      #faf6ed;
--paper-warm: #f4ecd8;
--cream:      #ede4cc;
--burgundy:   #7a1e1e;
--ochre:      #a07020;
--rule:       #c9b896;

/* dark mode = ink on amber parchment, not a dark IDE */
--dark-ink:    #e8dcc4;
--dark-paper:  #1a1410;
--dark-cream:  #2a201a;
```

Links in burgundy, finely underlined (`text-decoration-thickness: 1px; text-underline-offset: 0.2em`).

### Layout

- `max-width: 38rem` on the content (≈70 characters)
- `line-height: 1.7`
- Generous margins
- A slim serif side navigation
- Minimal header: monogram + title + version selector + component selector + **FR/EN toggle**
- Persistent light/dark toggle (localStorage)

### Language toggle

In the header, an `FR | EN` toggle. Logic:

- Each page knows its component (`vauban` or `vauban-fr`).
- The toggle computes the counterpart URL: if you are on `/vauban/page.html`, the toggle points to `/vauban-fr/page.html`, and vice versa. Same rule for `home` ↔ `home-fr`.
- If the counterpart page does not exist (404), fall back to the target component's `index`.
- The preferred language is persisted in localStorage and applied to the next navigation.
- The `<html lang="...">` attribute is set from the component's `lang` Asciidoc attribute.

Implemented in vanilla JS, ~30 lines max.

### Graphic elements (inline SVG only)

- An interlaced **V monogram** in SVG (~300 bytes of path), in the style of a sober royal cypher
- Ornate **decorative rules** (`<hr class="ornament">`), dot-dash-lozenge-dash-dot motif, monochrome ochre
- **Drop caps** on the first paragraph of each component's `index.adoc`, via the CSS `::first-letter`
- **Admonitions styled as seals**:
  - `CAUTION` / `WARNING`: burgundy seal + 3px burgundy left border
  - `NOTE`: thin ochre rule
  - `TIP`: 8-pointed ochre star
  - `IMPORTANT`: double burgundy rule
- **Footer**: the two articulated arms of the Chappe telegraph as simplified SVG (one mast + two strokes)

### Handlebars layouts

- `default.hbs`, `home.hbs`
- Partials: `head.hbs`, `header.hbs`, `nav.hbs`, `footer.hbs`, `toolbar.hbs`, `pagination.hbs`, `language-toggle.hbs`

### Handlebars helpers

- `roman`: number → Roman numerals
- `chappeVersion`: reads `data/versions.json`
- `i18n`: returns a string translated according to the current language (chrome labels: "Sur cette page", "Éditer", "Version", "Langue"…)

### Building the bundle

A `gulpfile.js` that:

1. Compiles `src/css/*.css` (PostCSS + autoprefixer + cssnano) → `build/ui/css/site.css`
2. Bundles `src/js/*.js` → `build/ui/js/site.js` (plain concatenation, no Webpack)
3. Copies layouts/partials/helpers/img/data + woff2 fonts → `build/ui/`
4. Zips `build/ui/` → `build/ui-bundle.zip`

`package.json`: `npm run build` → `node ../scripts/fetch-chappe-version.js && gulp bundle`. Target weight: **CSS + JS + fonts < 200 KB gzipped in total**.

## Step 5 — Chappe's version in the footer

Footer as displayed:

```
Propulsé par Chappe X.Y.Z[-SNAPSHOT]* · Documentation Vidocq · Apache 2.0 · MMXXVI
```

English version:

```
Powered by Chappe X.Y.Z[-SNAPSHOT]* · Vidocq Documentation · Apache 2.0 · MMXXVI
```

If the version contains `-SNAPSHOT`, add an ochre asterisk `*` with a translated `title`. Current year in Roman numerals through the `roman` helper.

`scripts/fetch-chappe-version.js`:

1. **Local**: read `../chappe/pom.xml`, extract the first root `<version>`.
2. **CI**: if `../chappe/pom.xml` is absent, `curl https://forge.vidocq.dev/vidocq/chappe/raw/branch/main/pom.xml`.
3. Write `ui-bundle/src/data/versions.json`:

   ```json
   {
     "chappe": "0.1.0-SNAPSHOT",
     "isSnapshot": true,
     "buildDate": "2026-05-07T..."
   }
   ```

Called before every build.

## Step 6 — Serving the site with Chappe

First, **inspect the `chappe` repo** to determine:

1. The canonical packaging method (fat jar, GraalVM native image, `.tar.gz` distribution, pre-published Docker image?)
2. The CLI or configuration file for serving a static directory
3. The format of the cache headers, gzip, fallback
4. The default listening port
5. How to add a conditional header such as `X-Robots-Tag: noindex`

If a Dockerfile **already** exists in `chappe/`, or an image published on `forge.vidocq.dev/vidocq/chappe`, **use it as the base**. Otherwise, build Chappe from source in the multi-stage.

Target `Dockerfile` (to be adapted to what you find):

```dockerfile
# ------------------------------------------------------------------
# Stage 1 — Building the Antora site
# ------------------------------------------------------------------
FROM node:lts-alpine AS site-builder
WORKDIR /build
COPY ui-bundle/package*.json ui-bundle/
RUN cd ui-bundle && npm ci
COPY . .
RUN cd ui-bundle && npm run build
RUN npx antora antora-playbook.yml

# ------------------------------------------------------------------
# Stage 2 — Building Chappe (if there is no published image)
# ------------------------------------------------------------------
# OR: FROM forge.vidocq.dev/vidocq/chappe:0.1.0-SNAPSHOT AS chappe-runtime
# (depending on what you find in the chappe repo)
FROM eclipse-temurin:25-jdk-alpine AS chappe-builder
# ... to be completed from the inspection of chappe ...

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

Also create `chappe-config.yml` at the root of the `vidocq-docs` repo with the correct directives (cache, gzip, fallback, robots) according to what Chappe expects.

**Dogfooding**: if Chappe does not yet have the required directives (fine-grained cache headers, configurable fallback, conditional `X-Robots-Tag`…), list them in `NOTES.md` under an `## Issues à ouvrir sur chappe` section, formatted as ready-to-paste markdown. I will create the issues myself. It is an excellent driver for finishing Chappe.

For `noindex` on staging: pass `STAGING=true` to Chappe. If the exact mechanism is unclear, propose a convention (env variable, config key, injected header).

## Step 7 — Forgejo workflow

`.forgejo/workflows/build.yml`:

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

Adapt the exact Forgejo Actions syntax if you know of local particularities.

## Step 8 — Documenting the docs project itself

`README.adoc`:

- Presentation
- Prerequisites (Node LTS, Antora 3.x, access to the sibling clones for the local build)
- `npm run build:local` (UI + local playbook)
- How to add a new component (create `docs/en/` and `docs/fr/` in the new repo, add a source to the playbook)
- How to contribute to an existing module's docs (PR on the module's repo, not here)
- Note: this repo contains **only** the playbook, the UI and the orchestration. The content lives in each module repo.

`docs/adr/0001-antora-multi-component.md` (MADR): Antora vs MkDocs/Docusaurus/Hugo, multi-repo docs, rationale.

`docs/adr/0002-bilingual-fr-en.md` (MADR): parallel `<module>` and `<module>-fr` components, FR canonical, EN translated, alternatives rejected (experimental Antora i18n, one fork per language, `fr.docs.vidocq.dev` sub-domains).

## Step 9 — Git, across 6 repos

For each module repo (`vidocq`, `vauban`, `cassini`, `champollion`, `chappe`):

```bash
cd <module>
git checkout -b docs/initial-bootstrap
git add docs/
git commit -m "docs: bootstrap bilingual documentation (en/fr)"
# NO PUSH
cd ..
```

For `vidocq-docs/`:

```bash
mkdir vidocq-docs && cd vidocq-docs
git init -b main
# .gitignore: node_modules/, build/, public/, .cache/, *.zip, NOTES.md, ui-bundle/build/
git add .
git commit -m "chore: bootstrap vidocq-docs (Antora + 19th-century UI + Chappe)

- Antora multi-component playbook (5 modules + home), bilingual FR/EN
- UI bundle: EB Garamond, parchment/burgundy palette, dark mode, language toggle
- Footer with dynamically extracted Chappe version
- Dockerfile multi-stage serving via Chappe
- Forgejo Actions: build + push + Portainer webhooks
- ADR-0001 (Antora), ADR-0002 (bilingual)"
git remote add origin ssh://git@forge.vidocq.dev:55122/vidocq/vidocq-docs.git
# NO PUSH
```

## Expected report

At the end, give me:

1. The final tree of the 6 repos touched (only the directories/files added)
2. For each repo, the local commit hash and the branch
3. What builds end to end vs what is marked TODO
4. The result of the Chappe inspection (packaging method chosen, any gaps)
5. Interesting discoveries during the module inspection (missing APIs, versions, surprises)
6. Commands to test locally:
   - `cd vidocq-docs/ui-bundle && npm install && npm run build && cd ..`
   - `npx antora antora-playbook-local.yml`
   - `docker build -t vidocq-docs:test .`
   - `docker run -p 8080:8080 vidocq-docs:test`
7. An ordered list of what I must do before pushing
8. Issues to open on the `chappe` side if you identified gaps (format them as ready-to-paste markdown)

Delete `vidocq-docs/NOTES.md` once the report is done.

## Guardrails

- **No push, on any repo.** Six repos = six local commits waiting for me.
- **Refuse if the git state is dirty.** If a module has uncommitted changes, stop and report.
- **Refuse if `docs/` already exists** in a module — report and wait for my instructions.
- **No invention.** `[TODO]` rather than a fictitious signature.
- **No AI art.** Every decorative visual is inline vector SVG or typography.
- **No Tailwind, no heavy JS framework.** Hand-written CSS, minimal vanilla JS.
- **No Google Fonts over CDN.** Self-host as woff2 in the UI bundle.
- **No tracking, no analytics.**
- **No automatic `npm audit fix --force`** — report it, I decide.
- **Strictly bilingual**: FR canonical, EN translated, complete content in both languages even if it is a `[TODO]`. No page that exists in only one language.
- **Consistent xref links**: every xref between pages uses `<component>::page.adoc`. The language toggle takes care of switching the component.

Get to work.
