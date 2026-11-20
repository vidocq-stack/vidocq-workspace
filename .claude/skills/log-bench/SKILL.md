---
name: log-bench
description: Append a new benchmark run entry to the BENCH.md of the current Vidocq component (a component folder of the monorepo, or a repository outside it). Use whenever JMH/wrk/comparative-perf numbers are produced — even informally during a debugging session. Creates BENCH.md if missing. Triggers on phrases like "log this benchmark", "add to BENCH.md", "record these numbers", or after running a JMH/wrk/perf command.
---

# log-bench

Append a benchmark run to the `BENCH.md` of the component under test, following the Vidocq convention defined in the workspace `AGENTS.md`. **No perf number is allowed in a README or commit message without a corresponding BENCH.md entry.**

## When to invoke

- A JMH suite was just run (`mvn -pl *-bench package` followed by `java -jar target/benchmarks.jar`).
- `wrk`, `wrk2`, `bombardier`, `oha`, `hey`, or any HTTP load tool was just run against a Vidocq server.
- A comparative measurement was done vs Netty, Jetty, Parsson, Yasson, Jackson, Weld, etc.
- The user says: "log this bench", "record these numbers", "add to BENCH.md".

## Procedure

1. **Identify the component** that owns the benchmark.
   - In the monorepo (`vidocq/main/` or a worktree `vidocq/<branch>/`), its folder is listed in `components.json` (e.g. `vidocq-components/vidocq-components-transport/chappe`, `vidocq-runtime`). A large component may keep a `BENCH.md` per sub-module folder (e.g. `mansart/mansart-pool/`): use the one closest to the code.
   - Outside the monorepo (`erasmus`, `tassis`, `verne`, `vidocq-benchmarks`, a VCU repository), the repository root.

2. **Locate or create** `BENCH.md` in that folder.

3. **Capture the environment** — ask the user only for what you cannot determine yourself:
   - JVM: `java -version` output (vendor + version + flags if non-default).
   - Hardware: CPU model + core count + RAM (from `system_profiler SPHardwareDataType` on macOS, `/proc/cpuinfo` on Linux).
   - OS: `uname -a`.
   - Git commit hash of the code under test (`git rev-parse --short HEAD` in the checkout under test).

4. **Append a section** at the bottom of `BENCH.md` with this structure:

   ```markdown
   ## BENCH-YYYYMMDD-NN — <short title: what was measured>

   - **Date**: YYYY-MM-DD
   - **Commit**: <short hash> (<branch>)
   - **JVM**: <vendor version, e.g. Temurin 25.0.0+36>
   - **Hardware**: <CPU> / <cores> cores / <RAM> GB RAM
   - **OS**: <uname output, condensed>
   - **Command**:
     ```bash
     <one-liner that reproduces>
     ```
   - **Results**:
     ```
     <raw output — keep it short, paste the summary table only>
     ```
   - **Delta vs the previous run**: <delta % vs BENCH-id, or "first run">
   - **Notes**: <anything non-obvious — warmup behaviour, GC pauses, allocations>
   ```

5. **Create the file with a header** if it does not exist:

   ```markdown
   # BENCH.md — <component>

   Performance measurements. Convention: see `AGENTS.md` of the Vidocq workspace.

   Every published figure (README, commit, post) must point to an entry here.

   ---
   ```

6. **Compute the delta** vs the most recent matching benchmark (same title prefix or same command). State it as percentage. If first run, write "first run".

7. **Do not commit** — only edit the file. Report the file path and the new BENCH-id to the user.
