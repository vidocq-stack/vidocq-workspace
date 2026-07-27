# PROVENANCE-AUDIT — differential code-similarity audit

**Status**: evidence report · **Run date**: 2026-07-27 · **Scope**: every Vidocq brick, production code only
**Companion documents**: `AI-POLICY.md` (governance stance), `AI-AUTHORSHIP-STATUS.md` (authorship evidence)

> This is an engineering evidence report, **not legal advice**.

## 1. The question

Vidocq is developed AI-assisted (see `AI-POLICY.md`). That raises a concrete, testable question,
independent of any authorship debate:

> Does Vidocq's source code reproduce code from existing implementations of the same specifications?

`AI-POLICY.md` §5 answers it only by process ("human review of every diff"), which a third party
cannot verify. This audit answers it by **measurement** instead, and is reproducible from §6.

It deliberately does **not** address titularity or licence compatibility — different questions,
handled elsewhere.

## 2. Method

Token-level clone detection with **PMD CPD 7.26.0**, resolved entirely from Maven Central (see
`provenance-audit/pom.xml`), so no binary from outside Central is involved.

Each Vidocq brick is scanned **together with the reference implementation of the same
specification**, and only clones spanning **both corpora** are retained — clones internal to either
corpus are irrelevant here and are discarded.

Three passes, because they catch different things:

| Pass | Tool | Threshold | Catches |
|---|---|---|---|
| **1 — Strict** | PMD CPD, defaults | 50 tokens | verbatim copy-paste |
| **2 — Token-structural** | PMD CPD, `--ignore-identifiers --ignore-literals` | 100 tokens | code copied **then renamed** |
| **3 — Program-structural** | JPlag 6.3.0 (Greedy String Tiling) | 9 tokens | code **restructured**: statements reordered, control flow rewritten, methods split |

Passes 1 and 2 slide a window over a raw token stream. Pass 3 parses both corpora into a
language-aware token stream and matches them with Greedy String Tiling, which survives the
transformations that hide a copy from CPD.

Scope: `src/main/java` only — the code actually distributed. Build output (`target/`), git worktrees
(`.claude/`) and TCK caches (`.tck-cache/`) are excluded.

### Reference corpus — 24 source jars, 12,491 files

| Vidocq brick | Compared against |
|---|---|
| vauban (CDI 4.1) | Weld 5.1.2 / 6.0.3 / 7.0.0.Beta2 |
| champollion (JSON-P/JSON-B) | Parsson 1.1.9, Yasson 3.0.4 |
| cassini (Jakarta REST 4.0) | Jersey 3.1.9 / 5.0.0-M1 |
| foy (Servlet 6.1) | Tomcat 10.1.34 / 11.0.24, Jetty 12.0.16 |
| chappe (HTTP/1.1+H2) | Netty 4.1.115 / 5.0.0.Alpha2 (codec-http, codec-http2) |
| ravel (MP Config) | SmallRye Config 3.18.1 |
| knock (MP Health) | SmallRye Health 4.3.0 |
| dirac (MP Metrics) | SmallRye Metrics 5.1.0 |
| heisenberg (MP Fault Tolerance) | SmallRye Fault Tolerance 7.0.0-RC1 |
| grimm (MP OpenAPI) | SmallRye OpenAPI 4.4.0-alpha1 |
| cervantes (MP JWT) | SmallRye JWT 5.0.0-RC2 |
| cyrano (MP Rest Client) | RESTEasy MicroProfile Rest Client 3.0.1 |
| mansart (Jakarta Data / Persistence) | Hibernate ORM 8.0.0.Beta1 |

Both current stable and latest releases were pulled where they differ, since widely distributed
stable versions are the more representative baseline. Each jar is unpacked into its **own**
sub-directory: successive versions of one implementation share their class paths, so unpacking them
together would let the last one silently overwrite the others and shrink the corpus to a single
version.

## 3. Results

| Brick | Files | Strict (50t) | Structural (100t) |
|---|---:|---:|---:|
| vauban | 213 | 3 | 0 |
| champollion | 112 | 5 | 2 |
| cassini | 119 | 1 | 0 |
| foy | 50 | 0 | 0 |
| chappe | 122 | 1 | 0 |
| ravel | 33 | 0 | 0 |
| knock | 20 | 1 | 0 |
| dirac | 30 | 0 | 2 |
| heisenberg | 41 | 0 | 0 |
| grimm | 75 | 0 | 0 |
| cervantes | 41 | 0 | 0 |
| cyrano | 47 | 0 | 0 |
| mansart | 134 | 0 | 2 |
| **Total** | **1,037** | **11** | **6** |

The 17 occurrences cover **11 distinct Vidocq files**: vauban's 3 strict hits are one and the same
fragment matched against Weld 5, 6 and 7, and champollion's `JsonArray` accessors are re-detected by
the structural pass.

**Sanity check.** A zero-finding run proves nothing if the harness is silently broken — which is
exactly what happened on the first attempt here: CPD 7 emits a *namespaced* XML report, the parser
matched no elements, and the run reported a spurious clean sweep across all 13 pairs. Every run
therefore also reports the total clone count across both corpora: **8,703** (strict) and **14,559**
(structural). The detector demonstrably fires; the cross-corpus hits are what survived out of those.

### Pass 3 — program-structural similarity, with calibration

A JPlag percentage means nothing in the absolute: two arbitrary Java projects already share a
structural floor, simply for being Java. The run therefore includes two controls that bound the
scale — a **negative** one (two unrelated projects: what "no relationship" looks like) and a
**positive** one (two releases of the same project: what real shared lineage looks like).

| | Similarity | Longest shared fragment |
|---|---:|---:|
| **Positive control** — Weld 5.1.2 ↔ Weld 6.0.3 (*same codebase*) | **96.94 %** | **1,878 tokens** |
| **Negative control** — Weld ↔ Hibernate (*unrelated*) | **28.26 %** | **195 tokens** |
| champollion ↔ Parsson/Yasson | 25.31 % | 52 tokens |
| grimm ↔ SmallRye OpenAPI | 19.20 % | 62 tokens |
| dirac ↔ SmallRye Metrics | 18.60 % | 48 tokens |
| heisenberg ↔ SmallRye FT | 14.67 % | 26 tokens |
| vauban ↔ Weld | 14.36 % | 42 tokens |
| cassini ↔ Jersey | 13.64 % | 48 tokens |
| knock ↔ SmallRye Health | 13.36 % | 16 tokens |
| cervantes ↔ SmallRye JWT | 12.80 % | 26 tokens |
| chappe ↔ Netty | 12.51 % | 59 tokens |
| ravel ↔ SmallRye Config | 12.06 % | 41 tokens |
| foy ↔ Tomcat/Jetty | 3.74 % | 41 tokens |
| mansart ↔ Hibernate | 3.05 % | 49 tokens |
| cyrano ↔ RESTEasy MP Rest Client | 1.45 % | 15 tokens |

**Every brick scores below the negative control.** Each one resembles the reference implementation
of its own specification *less* than two entirely unrelated Java projects resemble each other. The
longest fragment any brick shares with its reference is 62 tokens — under the 195 of the negative
control, and two orders of magnitude below the 1,878 of the positive one.

## 4. Analysis of every hit

Every hit was read in full. All of them fall into three categories, none of which is reproduced code.

**a. Interface implementations mandated by the specification**
The specification fixes the method names, signatures and semantics; the body has no meaningful
degree of freedom.

- `vauban` — `InjectionPoint` accessors (`getQualifiers`, `getBean`, `getMember`, `getAnnotated`,
  `isDelegate`), each returning a field. 25 lines, 60 tokens.
- `champollion` — `JsonArray` typed accessors (`getString(int)`, `getInt(int)` and their
  `defaultValue` overloads, whose fallback behaviour is dictated by the spec) and `JsonParser`
  decorators that are pure delegation (`return delegate.getX()`). `JsonNumber.intValue()` is
  *defined* by the spec as `bigDecimalValue().intValue()`.
- `cassini` — a no-op JAX-RS `Configuration` (`return false`, `List.of()`, `Map.of()`).
- `knock` — the MP Health builder (`up()` → `status = UP; return this`).
- `dirac` — `MetricRegistry` accessors (`getGauges/getCounters/getHistograms/getTimers` plus their
  `MetricFilter` overloads), with the only sensible implementation `getX() → getX(ALL)`. Note that
  dirac splits these into `rawView`/`typedView`, a distinction absent from SmallRye — evidence of
  independent implementation rather than copying.

**b. Normative constants**
- `chappe` — `Http2ErrorCode`. Both names and numeric values are fixed by **RFC 7540 §7**
  (`NO_ERROR=0x0`, `PROTOCOL_ERROR=0x1`, …). Any conforming implementation is identical here.

**c. Structural artefacts of the aggressive pass**
- `mansart` — `Book.java`, a sample entity (getters/setters) from the `mansart-data-tests` fixture
  module, matched against Hibernate's *generated* JAXB binding classes. With identifiers and
  literals ignored, all POJO accessors collapse onto the same token shape. A known limitation of the
  structural pass, not a finding — and not production code either.
- `champollion` — the same `JsonArray` accessors as (a), re-detected.

**Nothing in the 15 hits is an algorithm, a parsing routine, a state machine, a data structure or a
piece of business logic.** The parts where an implementation actually makes choices — Chappe's HTTP
parsing and flow control, Champollion's number parser, Vauban's bean resolution and proxy codegen,
Cassini's dispatch, Heisenberg's policy engines — show **no cross-corpus similarity at all**, at
either threshold.

## 5. Limits of this audit

Stated explicitly, because they bound what the result above may be used to claim.

1. **These tools detect similarity, not reimplementation.** Pass 3 covers restructured copies, which
   passes 1–2 cannot see, but code written from an *understanding* of an algorithm — genuinely
   re-expressed — remains invisible to all three. A clean report is strong evidence of no copying,
   not proof of independent creation.
2. **The corpus is finite.** Thirteen specification families and their principal implementations.
   Code could resemble a project not in the corpus, or non-Java, or material outside published
   artefacts (articles, forums, textbooks).
3. **Sources only.** Reference implementations without a published `-sources.jar` are absent.
4. **Thresholds are choices.** 50 and 100 tokens are conventional for plagiarism work; a shorter
   fragment copied verbatim would fall under them.
5. **Says nothing about titularity or licence compatibility.** Different questions.
6. **Pass 3 needs its staged sources in pure ASCII.** JPlag picks a single charset per submission
   (`FileUtils.detectCharsetFromMultiple`) and settles on windows-1252 when a mostly-ASCII tree
   holds a few UTF-8 files, which makes javac fail and silently discards the entire submission.
   Staged files are therefore rewritten with non-ASCII characters escaped as `\uXXXX`, exactly as
   `native2ascii` did: semantically identical source, unchanged tokens. Deleting those bytes instead
   — the first attempt here — corrupts the code (it turned a character literal into an empty one).

## 6. Reproducing this audit

```bash
# 1. resolve the CPD command line from Maven Central
cd provenance-audit && mvn -q dependency:build-classpath -Dmdep.outputFile=cp.txt

# 2. download the reference source jars and unpack them per family
bash provenance-audit/fetch-corpus.sh

# 3. passes 1 and 2 — CPD (per-brick table, XML + cross-corpus extracts)
TOKENS=50  MODE=strict bash provenance-audit/scan.sh
TOKENS=100 MODE=loose  bash provenance-audit/scan.sh

# 4. pass 3 — JPlag, including both calibration controls
MIN_TOKENS=9 bash provenance-audit/jplag.sh
```

Reports land in `provenance-audit/reports-<mode>-<tokens>/`: `<brick>.xml` (full CPD output) and
`<brick>.cross.txt` (cross-corpus clones only). Pass 3 writes `reports-jplag-<n>/summary.txt`.

## 7. Conclusion

Across 1,037 distributed production source files scanned against 12,491 files from the reference
implementations of the same specifications, by three methods of increasing tolerance to disguise,
**no reproduced code was found**.

- Passes 1–2 return 17 cross-corpus clones over 11 distinct files, all specification-mandated
  interface boilerplate, RFC-normative constants, or artefacts of the aggressive pass.
- Pass 3, which sees through renaming and restructuring, places **every brick below the negative
  control**: each resembles the reference implementation of its own specification less than two
  unrelated Java projects resemble each other. The longest fragment shared with a reference is 62
  tokens, against 1,878 for two releases of one codebase.

Put the other way round: the places where an implementation genuinely makes choices show no
similarity to the reference implementations, at any threshold, by any of the three methods — under
the limits stated in §5.

This is the verifiable counterpart to `AI-POLICY.md` §5, which until now rested solely on
non-auditable process.
