# MIGRATE_SPRING_2_VIDOCQ — playbook de migration (pour Claude)

> **But.** Ce document est lu par Claude Code **pendant la démo** pour migrer
> [`petstore-spring`](./petstore-spring) (Spring Boot 4 + Spring Data JPA + H2) vers **Vidocq**
> (Cassini REST + Mansart Data + Champollion JSON sur H2). Il donne les **dépendances exactes**, le
> **mapping idiome par idiome**, la **procédure pas-à-pas** et la **vérification**.
>
> **Le résultat attendu** existe déjà comme corrigé : `migrate-2-vidocq/petstore-vidocq`. À
> consulter en cas de doute — ne pas le recopier aveuglément pendant la démo, mais s'y référer.

---

## 0. Règle d'or (non négociable)

> **Le contrat HTTP ne change pas.** La suite Cucumber [`migrate-2-vidocq/acceptance`](./migrate-2-vidocq/acceptance)
> (13 scénarios) doit rester **verte** après migration. On ne modifie **jamais** un `.feature` pour
> faire passer le code : un scénario rouge = le code migré est faux.

Boucle : capturer la baseline verte (Spring) → migrer une brique → re-jouer le filet → vert.

---

## 1. Pré-requis

- **JDK 25** (Temurin) + **Maven** : `sdk env` à la racine du workspace.
- **Runtime Vidocq installé dans le M2 local** (fournit les artefacts `0.2.0` ci-dessous) :
  ```bash
  cd <workspace>/vidocq && ./mvnw -ntp -DskipTests install
  ```
- App source qui tourne pour la baseline :
  ```bash
  cd petstore-spring && mvn spring-boot:run     # :8080, REST sous /api, UI à la racine
  ```

---

## 2. Stack cible (briques Vidocq)

| Besoin | Brique | Extension runtime |
|--------|--------|-------------------|
| HTTP | **Chappe** | `chappe-core` |
| REST / JAX-RS 4.0 | **Cassini** | `vidocq-runtime-cassini-rest-extension` |
| Persistance (Jakarta Data 1.0) | **Mansart** | `vidocq-runtime-mansart-data-extension` |
| Pool JDBC | **Mansart Pool** | `vidocq-runtime-mansart-pool-extension` |
| Transactions | **Mansart Tx** | `vidocq-runtime-mansart-transactions-extension` |
| JSON-B / JSON-P | **Champollion** | `champollion-jsonb` (runtime) |
| Config | **Ravel** (MP Config) | `vidocq-runtime-ravel-config-extension` |
| CDI | **Vauban** | `vauban-indexer` (APT) |
| Driver H2 modularisé | — | `vidocq-runtime-h2-jpms-repackaged` |

Charte à respecter : **JPMS strict**, **zéro dépendance externe** (pas de Spring/Hibernate/Jackson),
**codegen statique APT** (jamais de réflexion runtime), **Virtual Threads**, **code/commentaires en
anglais**.

---

## 3. Dépendances Maven (POM cible)

> ⚠️ **Vidocq est un RUNTIME, pas un parent Maven.** Le projet migré **ne doit PAS** hériter de
> `vidocq-runtime-parent` : ce parent est le POM de **build interne** du runtime. En hériter traîne
> dans l'app sa machinerie privée — `license-maven-plugin:check` (qui exige `etc/license-header.txt`,
> absent de l'app → `mvn clean install` échoue), `checkpom`, le profil `dist`/jlink **actif par
> défaut**, et **couple la version de l'app** à celle du runtime. Le POM cible est donc **autonome**
> (pas de `<parent>`) : il a ses **propres** coordonnées/version et épingle les artefacts Vidocq comme
> de simples dépendances via la propriété `vidocq.version`.

Bloc à produire :

```xml
<groupId>com.example</groupId>
<artifactId>petstore-vidocq</artifactId>
<version>1.0.0-SNAPSHOT</version>          <!-- version de l'APP, indépendante du runtime -->
<packaging>jar</packaging>

<properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>25</maven.compiler.release>
    <maven.compiler.plugin.version>3.13.0</maven.compiler.plugin.version>

    <!-- Coordonnée unique de tous les artefacts io.vidocq.* (runtime, extensions,
         chappe, mansart, champollion, vauban). -->
    <vidocq.version>0.2.0</vidocq.version>

    <!-- APIs de specs Jakarta -->
    <jakarta.ws.rs.version>4.0.0</jakarta.ws.rs.version>
    <jakarta.persistence.version>3.2.0</jakarta.persistence.version>

    <!-- Coordonnées du main-module — lues par vidocq:dev et le profil dist -->
    <vidocq.mainModule>com.example.petstore</vidocq.mainModule>
    <vidocq.mainClass>com.example.petstore.PetstoreApp</vidocq.mainClass>
</properties>

<dependencies>
    <dependency>
        <groupId>io.vidocq.runtime</groupId>
        <artifactId>vidocq-runtime-core</artifactId>
        <version>${vidocq.version}</version>
    </dependency>

    <!-- REST (Cassini) + Config (Ravel) -->
    <dependency>
        <groupId>io.vidocq.runtime.extensions.jakartaee.core</groupId>
        <artifactId>vidocq-runtime-cassini-rest-extension</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
    <dependency>
        <groupId>io.vidocq.runtime.extensions.microprofile</groupId>
        <artifactId>vidocq-runtime-ravel-config-extension</artifactId>
        <version>${vidocq.version}</version>
    </dependency>

    <!-- Persistance : Mansart pool + data + transactions + dialecte H2 -->
    <dependency>
        <groupId>io.vidocq.runtime.extensions.jakartaee.web</groupId>
        <artifactId>vidocq-runtime-mansart-pool-extension</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
    <dependency>
        <groupId>io.vidocq.runtime.extensions.jakartaee.web</groupId>
        <artifactId>vidocq-runtime-mansart-data-extension</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
    <dependency>
        <groupId>io.vidocq.runtime.extensions.jakartaee.web</groupId>
        <artifactId>vidocq-runtime-mansart-transactions-extension</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
    <dependency>
        <groupId>io.vidocq.mansart</groupId>
        <artifactId>mansart-data-dialect-h2</artifactId>
        <version>${vidocq.version}</version>
        <scope>runtime</scope>
    </dependency>

    <!-- Driver H2 modularisé (named module com.h2database) — requis pour jlink/jpackage -->
    <dependency>
        <groupId>io.vidocq.runtime.extensions.jpms.repackaged</groupId>
        <artifactId>vidocq-runtime-h2-jpms-repackaged</artifactId>
        <version>${vidocq.version}</version>
        <scope>runtime</scope>
    </dependency>

    <!-- Transport -->
    <dependency>
        <groupId>io.vidocq.chappe</groupId>
        <artifactId>chappe-api</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
    <dependency>
        <groupId>io.vidocq.chappe</groupId>
        <artifactId>chappe-core</artifactId>
        <version>${vidocq.version}</version>
    </dependency>

    <!-- APIs Jakarta (compile only) -->
    <dependency>
        <groupId>jakarta.ws.rs</groupId>
        <artifactId>jakarta.ws.rs-api</artifactId>
        <version>${jakarta.ws.rs.version}</version>
    </dependency>
    <dependency>
        <groupId>jakarta.persistence</groupId>
        <artifactId>jakarta.persistence-api</artifactId>
        <version>${jakarta.persistence.version}</version>
    </dependency>

    <!-- JSON-B / JSON-P via Champollion -->
    <dependency>
        <groupId>io.vidocq.champollion</groupId>
        <artifactId>champollion-api</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
    <dependency>
        <groupId>io.vidocq.champollion</groupId>
        <artifactId>champollion-jsonb</artifactId>
        <version>${vidocq.version}</version>
        <scope>runtime</scope>
    </dependency>

    <!-- CDI indexer (Vauban) -->
    <dependency>
        <groupId>io.vidocq.vauban</groupId>
        <artifactId>vauban-indexer</artifactId>
        <version>${vidocq.version}</version>
    </dependency>
</dependencies>
```

**Versions** : tous les `io.vidocq.*` partagent `${vidocq.version}` = `0.2.0` (la version du
runtime installé dans le M2) ; la version de l'**app** est indépendante (`1.0.0-SNAPSHOT`).

> 💡 **Pas de BOM consommateur (encore).** Le runtime ne publie aujourd'hui **que** son parent de
> build — il n'existe pas de `vidocq-runtime-bom` (à importer en `scope=import`) ni de parent
> « starter » pour applications. Une app consommatrice doit donc déclarer ce POM à la main et répéter
> `${vidocq.version}` sur chaque dépendance. **Amélioration runtime suggérée** : publier un
> `io.vidocq.runtime:vidocq-runtime-bom` (dependencyManagement seul, sans plugins/profils/license)
> que les apps importeraient, supprimant la répétition des versions sans réintroduire le couplage du
> parent de build.

### Annotation processors (codegen statique) — OBLIGATOIRE

POM autonome : **rien n'est hérité**, donc on déclare **tous** les bundles codegen explicitement —
y compris `vidocq-runtime-core-codegen` (l'indexeur Vauban qui génère `_VaubanComponents`, l'index
des beans CDI). C'est le piège n°1 du passage en autonome : avec un parent il était hérité via
`combine.children="append"` ; sans parent, **l'oublier casse la découverte des beans**. On peut donc
laisser tomber `combine.children` (plus rien à fusionner) :

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>${maven.compiler.plugin.version}</version>
      <configuration>
        <release>${maven.compiler.release}</release>
        <annotationProcessorPaths>
          <path>
            <groupId>io.vidocq.runtime</groupId>
            <artifactId>vidocq-runtime-core-codegen</artifactId>
            <version>${vidocq.version}</version><type>pom</type>
          </path>
          <path>
            <groupId>io.vidocq.runtime.extensions.jakartaee.core</groupId>
            <artifactId>vidocq-runtime-cassini-rest-extension-codegen</artifactId>
            <version>${vidocq.version}</version><type>pom</type>
          </path>
          <path>
            <groupId>io.vidocq.runtime.extensions.jakartaee.web</groupId>
            <artifactId>vidocq-runtime-mansart-data-extension-codegen</artifactId>
            <version>${vidocq.version}</version><type>pom</type>
          </path>
          <path>
            <groupId>io.vidocq.runtime.extensions.jakartaee.web</groupId>
            <artifactId>vidocq-runtime-mansart-transactions-extension-codegen</artifactId>
            <version>${vidocq.version}</version><type>pom</type>
          </path>
        </annotationProcessorPaths>
      </configuration>
    </plugin>
    <!-- Indexe les beans CDI + packaging Vidocq -->
    <plugin>
      <groupId>io.vidocq.runtime</groupId>
      <artifactId>vidocq-runtime-maven-plugin</artifactId>
      <version>${vidocq.version}</version>
      <executions>
        <execution><id>generate</id><goals><goal>generate</goal></goals></execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

> Le packaging natif (jlink/jpackage/docker) vit dans un profil `dist` **opt-in** (PAS
> `activeByDefault`) : `mvn clean install` produit un jar simple, et `mvn -Pdist package` construit
> l'image jlink quand on en a besoin. Plus besoin du contournement `-P'!dist'`.

---

## 4. `module-info.java` cible (JPMS)

```java
module com.example.petstore {
    requires java.logging;
    requires static java.compiler;            // @Generated (SOURCE retention) des classes APT

    requires jakarta.cdi;
    requires jakarta.inject;
    requires jakarta.ws.rs;
    requires jakarta.json.bind;
    requires jakarta.persistence;
    requires jakarta.data;
    requires jakarta.transaction;

    requires io.vidocq.runtime.core;
    requires io.vidocq.runtime.spi;
    requires io.vidocq.runtime.extensions.jakartaee.core.cassini;
    requires io.vidocq.cassini.api;           // sortie APT cassini ($$CassiniAdapter)
    requires io.vidocq.runtime.extensions.jakartaee.web.mansart.pool;
    requires io.vidocq.runtime.extensions.jakartaee.web.mansart.data;
    requires io.vidocq.runtime.extensions.jakartaee.web.mansart.transactions;
    requires io.vidocq.runtime.extensions.microprofile.ravel;
    requires io.vidocq.chappe.api;
    requires io.vidocq.vauban.core;
    requires io.vidocq.mansart.data.core;

    opens com.example.petstore;               // JAX-RS + Mansart réfléchissent sur resources/entités
    opens com.example.petstore.model;         // JSON-B (Champollion) réfléchit sur les DTO records
}
```

---

## 5. `src/main/resources/vidocq.properties` cible

```properties
# Listener Chappe
vidocq.chappe.listener.default.host=0.0.0.0
vidocq.chappe.listener.default.port=8080

# REST monté sous /api (Cassini)
vidocq.http.mount.api.path=/api
vidocq.http.mount.api.type=restful

# UI statique à la racine (optionnel, depuis src/main/resources/static/)
vidocq.http.mount.ui.path=/
vidocq.http.mount.ui.type=static
vidocq.http.mount.ui.classpath=static
vidocq.http.mount.ui.cache-in-memory=true

# Pool Mansart — H2 in-memory
vidocq.pool.url=jdbc:h2:mem:petstore;DB_CLOSE_DELAY=-1
vidocq.pool.username=sa
vidocq.pool.maxSize=8
vidocq.pool.acquireTimeout=PT5S
```

---

## 6. Table de mapping Spring → Vidocq

| Spring | Vidocq | Notes |
|--------|--------|-------|
| `@SpringBootApplication` + `SpringApplication.run` | classe `PetstoreApp` → `Vidocq.main(args)` | bootstrap par ServiceLoader d'extensions |
| `application.yml` + `WebConfig` (préfixe `/api`) | `vidocq.properties` (mount `/api`) | un seul mount REST |
| `@RestController` `@RequestMapping("/pets")` | `@ApplicationScoped @Path("/pets")` | un `@Path` par resource |
| `@GetMapping/@PostMapping/@PutMapping/@DeleteMapping` | `@GET/@POST/@PUT/@DELETE` (+ `@Path("/{id}")`) | `@Produces/@Consumes(APPLICATION_JSON)` |
| `@PathVariable` / `@RequestParam` / `@RequestBody` | `@PathParam` / `@QueryParam` / paramètre corps | — |
| `ResponseEntity.ok/status(CREATED)/notFound/noContent` | `Response.ok/status(...).entity(...).build()` | conserver **exactement** 200/201/204/404 |
| `produces=TEXT_PLAIN` (count) | `@Produces(TEXT_PLAIN)` renvoyant `long` | — |
| `@Service` | `@ApplicationScoped` | bean Vauban |
| `org.springframework…@Transactional` | `jakarta.transaction.Transactional` | sur les méthodes d'écriture |
| `JpaRepository<T,Id>` | `@Repository interface … extends BasicRepository<T,Id>` | impl **générée par APT** Mansart |
| `findByStatus`, `findByName` | mêmes méthodes dérivées sur l'interface | `findAll()` renvoie un `Stream` |
| `@Entity` + `@ManyToOne`/`@ManyToMany`/`@JoinTable` | `@Entity` **plates** (FK nues) + **entité de jonction** | **Mansart n'a pas d'associations** → relations recomposées dans le service |
| Jackson (auto) | **Champollion JSON-B** | DTO = `record` ; `opens …model` |
| autoconfig Boot | extensions SPI + `module-info.java` | `requires` les modules d'extension |
| `ddl-auto` / `data.sql` | `SchemaInitializer` `@Observes @Initialized(ApplicationScoped.class)` | démo only ; Flyway sinon |

---

## 7. Procédure pas-à-pas (ordre des dépendances)

> Skills disponibles dans `migrate-2-vidocq/.claude/skills/` : `/migrate-entity`,
> `/migrate-repository`, `/migrate-rest-resource`, `/run-acceptance`.

1. **Baseline** — démarrer `petstore-spring`, exécuter `/run-acceptance` (`-Dpetstore.baseUrl=http://localhost:8080`) → **13/13 verts**. C'est le contrat figé.
2. **Squelette** — créer le module cible : `pom.xml` (§3), `module-info.java` (§4), `vidocq.properties` (§5), classe `PetstoreApp` (`Vidocq.main`).
3. **Entités** (`/migrate-entity`) — `Pet`, `Category`, `Tag` en entités **plates** :
   - `@ManyToOne Category` → champ `Long categoryId` (`@Column(name="category_id")`) ;
   - `@ManyToMany Set<Tag>` (+ `@JoinTable`) → **entité de jonction** `PetTag(petId, tagId)` ;
   - `SchemaInitializer` : créer les 4 tables plates + seed (Dog/Cat ; friendly/trained/playful ; Rex/Whiskers/Buddy).
4. **Repositories** (`/migrate-repository`) — interfaces `@Transactional @Repository extends BasicRepository<…>` : `PetRepository` (`findByStatus`), `CategoryRepository`/`TagRepository` (`findByName`), `PetTagRepository` (`findByPetId`). Brancher l'APT (§3).
5. **Service + resources** (`/migrate-rest-resource`) — `PetService` `@ApplicationScoped` qui **réassemble** les relations (résoudre/créer catégorie & tags par nom, gérer la table de jonction, mapper `Pet`→`PetView`) ; resources JAX-RS `PetResource`/`CategoryResource`/`TagResource` exposant le **même** contrat. DTO `record` `PetInput`/`PetView`/`{id,name}` dans `…model`.
6. **Compiler** (APT inclus) :
   ```bash
   cd <module-cible> && mvn -DskipTests package        # ou: mvn clean install
   ```
7. **Re-prouver** — démarrer l'app (`mvn vidocq:dev`, `:8080`, mount `/api`), relancer `/run-acceptance` → **13/13 verts**.

---

## 8. Pièges à connaître (sinon ça casse en prod / module-path)

- **`opens` JPMS** : sans `opens com.example.petstore;` (resources + entités) et `opens …model;`
  (DTO JSON-B), tout marche en classpath mais **casse en module-path** (réflexion JAX-RS/Mansart/JSON-B).
- **`@Inject Instance<DataSource>`** : le `DataSource` est fourni par `mansart-pool` **à runtime**,
  invisible de l'index CDI compile-time. L'injecter **directement** fait rejeter le bean par l'APT
  Vauban → passer par `Instance<DataSource>` (cf. `SchemaInitializer`).
- **Pas d'associations Mansart** : ne jamais tenter `@ManyToOne/@ManyToMany` côté Mansart. Tout se
  fait à plat + assemblage dans le service (delete-then-reinsert de la jonction au `update`).
- **Sémantique métier à préserver** (sinon Cucumber rouge) : statut par défaut `available` si vide ;
  catégorie/tags **résolus ou créés** par nom ; `update` resynchronise les tags ; 201/204/404 exacts.
- **Seed IDENTITY** : après inserts d'ids explicites, `ALTER TABLE … ALTER COLUMN id RESTART WITH n`
  pour que le prochain `POST` ne collisionne pas.
- **Ne jamais écrire `…RepositoryImpl` à la main** : c'est l'APT Mansart qui le génère.
- **Ne pas hériter de `vidocq-runtime-parent`** (cf. §3) : POM **autonome**. En hériter casse
  `mvn clean install` (license-check sur `etc/license-header.txt` absent) et couple la version de
  l'app au runtime. Corollaire : sans parent, **déclarer `vidocq-runtime-core-codegen` explicitement**
  dans `annotationProcessorPaths` (sinon `_VaubanComponents` n'est pas généré → beans CDI introuvables).

---

## 9. Vérification finale (definition of done)

```bash
# build (codegen APT + plugin) — dist est opt-in, pas besoin de -P'!dist'
cd <module-cible> && mvn clean install                          # BUILD SUCCESS (jar simple)

# run
mvn vidocq:dev                                                  # http://localhost:8080/

# non-régression : MÊME suite que la baseline
cd ../acceptance && mvn test -Dpetstore.baseUrl=http://localhost:8080
# attendu : 13 Scenarios (13 passed) — 54 Steps (54 passed)
```

`curl` de contrôle :
```bash
curl http://localhost:8080/api/pets
curl 'http://localhost:8080/api/pets?status=available'
curl -X POST -H 'content-type: application/json' \
     -d '{"name":"Rex","category":"Dog","status":"available","price":120.0,"tags":["friendly","trained"]}' \
     http://localhost:8080/api/pets
curl http://localhost:8080/api/pets/count
```

✅ **Terminé** quand le build passe, l'app répond sur `/api`, et la suite Cucumber est **verte**,
exactement comme contre l'app Spring.
