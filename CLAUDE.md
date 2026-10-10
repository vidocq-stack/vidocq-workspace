@AGENTS.md

<!--
  AGENTS.md is the single source of agent instructions for the Vidocq workspace.
  Edit the shared rules there; keep this file to the Claude Code specific tooling below.
-->

## Claude Code agents and skills available in this workspace

Defined in `.claude/agents/` and `.claude/skills/` — use proactively when the context is suitable:

- Agents: `java-modules-guardian` (`module-info.java` audit), `classfile-codegen` (Class-File API + APT), `tck-runner` (official Jakarta TCK runners), `virtual-threads-reviewer` (concurrency review), `dependency-gatekeeper` (zero-dep `pom.xml` review).
- Skills: `/log-bug` (adds an entry to `<repo>/BUG.md`), `/log-bench` (adds an entry to `<repo>/BENCH.md`).
