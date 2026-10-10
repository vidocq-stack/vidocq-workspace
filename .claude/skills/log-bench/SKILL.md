---
name: log-bench
description: Append a new benchmark run entry to the BENCH.md of the current Vidocq sub-project. Use whenever JMH/wrk/comparative-perf numbers are produced — even informally during a debugging session. Creates BENCH.md if missing. Triggers on phrases like "log this benchmark", "add to BENCH.md", "record these numbers", or after running a JMH/wrk/perf command.
---

# log-bench

Append a benchmark run to `<sub-project>/BENCH.md` following the Vidocq convention defined in the root `AGENTS.md`. **No perf number is allowed in a README or commit message without a corresponding BENCH.md entry.**

## When to invoke

- A JMH suite was just run (`mvn -pl *-bench package` followed by `java -jar target/benchmarks.jar`).
- `wrk`, `wrk2`, `bombardier`, `oha`, `hey`, or any HTTP load tool was just run against a Vidocq server.
- A comparative measurement was done vs Netty, Jetty, Parsson, Yasson, Jackson, Weld, etc.
- The user says: "log this bench", "record these numbers", "add to BENCH.md".

## Procedure

1. **Identify the sub-project**: which of `chappe`, `vauban`, `champollion`, `foy`, `cassini`, `vidocq` owns the benchmark.

2. **Locate or create** `<sub-project>/BENCH.md` at the sub-project root.

3. **Capture the environment** — ask the user only for what you cannot determine yourself:
   - JVM: `java -version` output (vendor + version + flags if non-default).
   - Hardware: CPU model + core count + RAM (from `system_profiler SPHardwareDataType` on macOS, `/proc/cpuinfo` on Linux).
   - OS: `uname -a`.
   - Git commit hash of the code under test (`git rev-parse --short HEAD` if the sub-project is a git repo).

4. **Append a section** at the bottom of `BENCH.md` with this structure:

   ```markdown
   ## BENCH-YYYYMMDD-NN — <short title: what was measured>

   - **Date** : YYYY-MM-DD
   - **Commit** : <short hash> (<branch>)
   - **JVM** : <vendor version, e.g. Temurin 25.0.0+36>
   - **Hardware** : <CPU> / <cores> cores / <RAM> GB RAM
   - **OS** : <uname output, condensed>
   - **Commande exacte** :
     ```bash
     <one-liner that reproduces>
     ```
   - **Résultats** :
     ```
     <raw output — keep it short, paste the summary table only>
     ```
   - **Comparaison vs run précédent** : <delta % vs BENCH-id, or "premier run">
   - **Notes** : <anything non-obvious — warmup behaviour, GC pauses, allocations>
   ```

5. **Create the file with a header** if it does not exist:

   ```markdown
   # BENCH.md — <sub-project>

   Historique des mesures de performance. Convention : voir `vidocq-workspace/AGENTS.md` (workspace root).

   Tout chiffre publié (README, commit, post) doit pointer vers une entrée ici.

   ---
   ```

6. **Compute the delta** vs the most recent matching benchmark (same title prefix or same command). State it as percentage. If first run, write "premier run".

7. **Do not commit** — only edit the file. Report the file path and the new BENCH-id to the user.
