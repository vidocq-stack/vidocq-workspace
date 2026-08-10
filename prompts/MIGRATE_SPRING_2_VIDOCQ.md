# MIGRATE_SPRING_2_VIDOCQ — migration playbook (for Claude)

> **Purpose.** This document is read by Claude Code **during the demo** to migrate
> [`petstore-spring`](./petstore-spring) (Spring Boot 4 + Spring Data JPA + H2) to **Vidocq**
> (Cassini REST + Mansart Data + Champollion JSON on H2). It gives the **exact dependencies**, the
> **idiom-by-idiom mapping**, the **step-by-step procedure** and the **verification**.
>
> **The expected result** already exists as a worked answer: `migrate-2-vidocq/petstore-vidocq`.
> Consult it when in doubt — do not copy it blindly during the demo, but refer to it.

---

## 0. Golden rule (non-negotiable)

> **The HTTP contract does not change.** The Cucumber suite
> [`migrate-2-vidocq/acceptance`](./migrate-2-vidocq/acceptance) (13 scenarios) must stay **green**
> after the migration. **Never** modify a `.feature` to make the code pass: a red scenario means the
> migrated code is wrong.

Loop: capture the green baseline (Spring) → migrate one brick → replay the safety net → green.

---

## 1. Prerequisites

- **JDK 25** (Temurin) + **Maven**: `sdk env` at the workspace root.
- **Vidocq runtime installed in the local M2** (provides the `0.2.0` artefacts below):
  ```bash
  cd <workspace>/vidocq && ./mvnw -ntp -DskipTests install
  ```
- The source app running, for the baseline:
  ```bash
  cd petstore-spring && mvn spring-boot:run     # :8080, REST under /api, UI at the root
  ```

---

## 2. Target stack (Vidocq bricks)

| Need | Brick | Runtime extension |
|--------|--------|-------------------|
| HTTP | **Chappe** | `chappe-core` |
| REST / JAX-RS 4.0 | **Cassini** | `vidocq-runtime-cassini-rest-extension` |
| Persistence (Jakarta Data 1.0) | **Mansart** | `vidocq-runtime-mansart-data-extension` |
| JDBC pool | **Mansart Pool** | `vidocq-runtime-mansart-pool-extension` |
| Transactions | **Mansart Tx** | `vidocq-runtime-mansart-transactions-extension` |
| JSON-B / JSON-P | **Champollion** | `champollion-jsonb` (runtime) |
| Config | **Ravel** (MP Config) | `vidocq-runtime-ravel-config-extension` |
| CDI | **Vauban** | `vauban-indexer` (APT) |
| Modularised H2 driver | — | `vidocq-runtime-h2-jpms-repackaged` |

Charter to respect: **strict Java Modules**, **zero external dependency** (no Spring/Hibernate/Jackson),
**static APT codegen** (never runtime reflection), **Virtual Threads**, **code/comments in English**.

---

## 3. Maven dependencies (target POM)

> ⚠️ **Vidocq is a RUNTIME, not a Maven parent.** The migrated project **must NOT** inherit from
> `vidocq-runtime-parent`: that parent is the runtime's **internal build** POM. Inheriting from it
> drags its private machinery into the app — `license-maven-plugin:check` (which requires
> `etc/license-header.txt`, absent from the app → `mvn clean install` fails), `checkpom`, the
> `dist`/jlink profile **active by default** — and **couples the app's version** to the runtime's.
> The target POM is therefore **standalone** (no `<parent>`): it has its **own** coordinates/version
> and pins the Vidocq artefacts as plain dependencies through the `vidocq.version` property.

Block to produce:

```xml
<groupId>com.example</groupId>
<artifactId>petstore-vidocq</artifactId>
<version>1.0.0-SNAPSHOT</version>          <!-- the APP's version, independent of the runtime -->
<packaging>jar</packaging>

<properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>25</maven.compiler.release>
    <maven.compiler.plugin.version>3.13.0</maven.compiler.plugin.version>

    <!-- Single coordinate for all io.vidocq.* artefacts (runtime, extensions,
         chappe, mansart, champollion, vauban). -->
    <vidocq.version>0.2.0</vidocq.version>

    <!-- Jakarta spec APIs -->
    <jakarta.ws.rs.version>4.0.0</jakarta.ws.rs.version>
    <jakarta.persistence.version>3.2.0</jakarta.persistence.version>

    <!-- Main-module coordinates — read by vidocq:dev and the dist profile -->
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

    <!-- Persistence: Mansart pool + data + transactions + H2 dialect -->
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

    <!-- Modularised H2 driver (named module com.h2database) — required for jlink/jpackage -->
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

    <!-- Jakarta APIs (compile only) -->
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

    <!-- JSON-B / JSON-P through Champollion -->
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

**Versions**: every `io.vidocq.*` shares `${vidocq.version}` = `0.2.0` (the version of the runtime
installed in the M2); the **app's** version is independent (`1.0.0-SNAPSHOT`).

> 💡 **No consumer BOM (yet).** Today the runtime publishes **only** its build parent — there is no
> `vidocq-runtime-bom` (to import with `scope=import`) and no "starter" parent for applications. A
> consuming app must therefore declare this POM by hand and repeat `${vidocq.version}` on every
> dependency. **Suggested runtime improvement**: publish an `io.vidocq.runtime:vidocq-runtime-bom`
> (dependencyManagement only, no plugins/profiles/license) for apps to import, removing the version
> repetition without reintroducing the build parent's coupling.

### Annotation processors (static codegen) — MANDATORY

Standalone POM: **nothing is inherited**, so **all** codegen bundles are declared explicitly —
including `vidocq-runtime-core-codegen` (the Vauban indexer that generates `_VaubanComponents`, the
CDI bean index). This is pitfall #1 of going standalone: with a parent it was inherited through
`combine.children="append"`; without a parent, **forgetting it breaks bean discovery**. We can
therefore drop `combine.children` (there is nothing left to merge):

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
    <!-- Indexes the CDI beans + Vidocq packaging -->
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

> Native packaging (jlink/jpackage/docker) lives in an **opt-in** `dist` profile (NOT
> `activeByDefault`): `mvn clean install` produces a plain jar, and `mvn -Pdist package` builds the
> jlink image when needed. The `-P'!dist'` workaround is no longer necessary.

---

## 4. Target `module-info.java` (Java Modules)

```java
module com.example.petstore {
    requires java.logging;
    requires static java.compiler;            // @Generated (SOURCE retention) on the APT classes

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
    requires io.vidocq.cassini.api;           // cassini APT output ($$CassiniAdapter)
    requires io.vidocq.runtime.extensions.jakartaee.web.mansart.pool;
    requires io.vidocq.runtime.extensions.jakartaee.web.mansart.data;
    requires io.vidocq.runtime.extensions.jakartaee.web.mansart.transactions;
    requires io.vidocq.runtime.extensions.microprofile.ravel;
    requires io.vidocq.chappe.api;
    requires io.vidocq.vauban.core;
    requires io.vidocq.mansart.data.core;

    opens com.example.petstore;               // JAX-RS + Mansart reflect over resources/entities
    opens com.example.petstore.model;         // JSON-B (Champollion) reflects over the DTO records
}
```

---

## 5. Target `src/main/resources/vidocq.properties`

```properties
# Chappe listener
vidocq.chappe.listener.default.host=0.0.0.0
vidocq.chappe.listener.default.port=8080

# REST mounted under /api (Cassini)
vidocq.http.mount.api.path=/api
vidocq.http.mount.api.type=restful

# Static UI at the root (optional, from src/main/resources/static/)
vidocq.http.mount.ui.path=/
vidocq.http.mount.ui.type=static
vidocq.http.mount.ui.classpath=static
vidocq.http.mount.ui.cache-in-memory=true

# Mansart pool — H2 in-memory
vidocq.pool.url=jdbc:h2:mem:petstore;DB_CLOSE_DELAY=-1
vidocq.pool.username=sa
vidocq.pool.maxSize=8
vidocq.pool.acquireTimeout=PT5S
```

---

## 6. Spring → Vidocq mapping table

| Spring | Vidocq | Notes |
|--------|--------|-------|
| `@SpringBootApplication` + `SpringApplication.run` | `PetstoreApp` class → `Vidocq.main(args)` | bootstrap through the extension ServiceLoader |
| `application.yml` + `WebConfig` (`/api` prefix) | `vidocq.properties` (mount `/api`) | a single REST mount |
| `@RestController` `@RequestMapping("/pets")` | `@ApplicationScoped @Path("/pets")` | one `@Path` per resource |
| `@GetMapping/@PostMapping/@PutMapping/@DeleteMapping` | `@GET/@POST/@PUT/@DELETE` (+ `@Path("/{id}")`) | `@Produces/@Consumes(APPLICATION_JSON)` |
| `@PathVariable` / `@RequestParam` / `@RequestBody` | `@PathParam` / `@QueryParam` / body parameter | — |
| `ResponseEntity.ok/status(CREATED)/notFound/noContent` | `Response.ok/status(...).entity(...).build()` | keep **exactly** 200/201/204/404 |
| `produces=TEXT_PLAIN` (count) | `@Produces(TEXT_PLAIN)` returning a `long` | — |
| `@Service` | `@ApplicationScoped` | Vauban bean |
| `org.springframework…@Transactional` | `jakarta.transaction.Transactional` | on the write methods |
| `JpaRepository<T,Id>` | `@Repository interface … extends BasicRepository<T,Id>` | implementation **generated by the Mansart APT** |
| `findByStatus`, `findByName` | the same derived methods on the interface | `findAll()` returns a `Stream` |
| `@Entity` + `@ManyToOne`/`@ManyToMany`/`@JoinTable` | **flat** `@Entity` (bare FKs) + a **junction entity** | **Mansart has no associations** → relations recomposed in the service |
| Jackson (automatic) | **Champollion JSON-B** | DTO = `record`; `opens …model` |
| Boot autoconfiguration | SPI extensions + `module-info.java` | `requires` the extension modules |
| `ddl-auto` / `data.sql` | `SchemaInitializer` `@Observes @Initialized(ApplicationScoped.class)` | demo only; Flyway otherwise |

---

## 7. Step-by-step procedure (dependency order)

> Skills available in `migrate-2-vidocq/.claude/skills/`: `/migrate-entity`,
> `/migrate-repository`, `/migrate-rest-resource`, `/run-acceptance`.

1. **Baseline** — start `petstore-spring`, run `/run-acceptance` (`-Dpetstore.baseUrl=http://localhost:8080`) → **13/13 green**. That is the frozen contract.
2. **Skeleton** — create the target module: `pom.xml` (§3), `module-info.java` (§4), `vidocq.properties` (§5), the `PetstoreApp` class (`Vidocq.main`).
3. **Entities** (`/migrate-entity`) — `Pet`, `Category`, `Tag` as **flat** entities:
   - `@ManyToOne Category` → a `Long categoryId` field (`@Column(name="category_id")`);
   - `@ManyToMany Set<Tag>` (+ `@JoinTable`) → a **junction entity** `PetTag(petId, tagId)`;
   - `SchemaInitializer`: create the 4 flat tables + seed (Dog/Cat; friendly/trained/playful; Rex/Whiskers/Buddy).
4. **Repositories** (`/migrate-repository`) — `@Transactional @Repository extends BasicRepository<…>` interfaces: `PetRepository` (`findByStatus`), `CategoryRepository`/`TagRepository` (`findByName`), `PetTagRepository` (`findByPetId`). Wire up the APT (§3).
5. **Service + resources** (`/migrate-rest-resource`) — an `@ApplicationScoped` `PetService` that **reassembles** the relations (resolve/create category & tags by name, manage the junction table, map `Pet`→`PetView`); JAX-RS resources `PetResource`/`CategoryResource`/`TagResource` exposing the **same** contract. `record` DTOs `PetInput`/`PetView`/`{id,name}` in `…model`.
6. **Compile** (APT included):
   ```bash
   cd <target-module> && mvn -DskipTests package        # or: mvn clean install
   ```
7. **Re-prove** — start the app (`mvn vidocq:dev`, `:8080`, mount `/api`), replay `/run-acceptance` → **13/13 green**.

---

## 8. Pitfalls to know (otherwise it breaks in production / on the module path)

- **Java Modules `opens`**: without `opens com.example.petstore;` (resources + entities) and
  `opens …model;` (JSON-B DTOs), everything works on the classpath but **breaks on the module path**
  (JAX-RS/Mansart/JSON-B reflection).
- **`@Inject Instance<DataSource>`**: the `DataSource` is provided by `mansart-pool` **at runtime**,
  invisible to the compile-time CDI index. Injecting it **directly** makes the Vauban APT reject the
  bean → go through `Instance<DataSource>` (cf. `SchemaInitializer`).
- **No Mansart associations**: never attempt `@ManyToOne/@ManyToMany` on the Mansart side. Everything
  is done flat + assembled in the service (delete-then-reinsert of the junction on `update`).
- **Business semantics to preserve** (otherwise Cucumber goes red): default status `available` when
  empty; category/tags **resolved or created** by name; `update` resynchronises the tags; exact
  201/204/404.
- **Seed IDENTITY**: after inserting explicit ids, `ALTER TABLE … ALTER COLUMN id RESTART WITH n` so
  that the next `POST` does not collide.
- **Never write `…RepositoryImpl` by hand**: the Mansart APT generates it.
- **Do not inherit from `vidocq-runtime-parent`** (cf. §3): **standalone** POM. Inheriting from it
  breaks `mvn clean install` (license-check on the absent `etc/license-header.txt`) and couples the
  app's version to the runtime. Corollary: without a parent, **declare `vidocq-runtime-core-codegen`
  explicitly** in `annotationProcessorPaths` (otherwise `_VaubanComponents` is not generated → CDI
  beans cannot be found).

---

## 9. Final verification (definition of done)

```bash
# build (APT codegen + plugin) — dist is opt-in, no need for -P'!dist'
cd <target-module> && mvn clean install                         # BUILD SUCCESS (plain jar)

# run
mvn vidocq:dev                                                  # http://localhost:8080/

# non-regression: the SAME suite as the baseline
cd ../acceptance && mvn test -Dpetstore.baseUrl=http://localhost:8080
# expected: 13 Scenarios (13 passed) — 54 Steps (54 passed)
```

Control `curl`s:
```bash
curl http://localhost:8080/api/pets
curl 'http://localhost:8080/api/pets?status=available'
curl -X POST -H 'content-type: application/json' \
     -d '{"name":"Rex","category":"Dog","status":"available","price":120.0,"tags":["friendly","trained"]}' \
     http://localhost:8080/api/pets
curl http://localhost:8080/api/pets/count
```

✅ **Done** when the build passes, the app answers on `/api`, and the Cucumber suite is **green**,
exactly as it was against the Spring app.
