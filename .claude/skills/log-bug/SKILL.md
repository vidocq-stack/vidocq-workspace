---
name: log-bug
description: Append a new bug entry to the BUG.md of the current Vidocq component (a component folder of the monorepo, or a repository outside it). Use when the user reports a bug, when a TCK test fails with a real implementation bug (not a harness issue), or when a regression is discovered. Creates BUG.md if missing. Triggers on phrases like "log this bug", "track this bug", "BUG.md", "add to BUG.md".
---

# log-bug

Append a bug entry to the `BUG.md` of the component that owns the bug, following the Vidocq convention defined in the workspace `AGENTS.md`.

## When to invoke

- User says: "log this bug", "track this in BUG.md", "add a bug entry", "this is a regression".
- A TCK run failed with a real implementation bug (not Arquillian wiring, not missing artefacts).
- A reproducible incorrect behaviour was identified during a code review or debugging session.

## Procedure

1. **Identify the component**: ask the user (or infer from the working directory / files being discussed) which component owns the bug.
   - In the monorepo (`vidocq/main/` or a worktree `vidocq/<branch>/`), the component's folder is listed in `components.json` (e.g. `vidocq-components/vidocq-components-microprofile/ravel`, `vidocq-runtime`). A large component may keep a `BUG.md` per sub-module folder (e.g. `mansart/mansart-transactions/`): use the one closest to the code.
   - Outside the monorepo (`erasmus`, `tassis`, `verne`, a VCU repository), the repository root.

2. **Locate or create** `BUG.md` in that folder (next to its `pom.xml`).

3. **Generate a short ID**: `BUG-<YYYYMMDD>-<NN>` where `NN` is the next free number for that day. A bug id is unique across the monorepo and the repositories around it: check the other `BUG.md` files (and the open branches) for that day before picking a number. If none is used, start at `01`.

4. **Append a section** to `BUG.md` with this structure:

   ```markdown
   ## BUG-YYYYMMDD-NN — <one-line symptom>

   - **Date**: YYYY-MM-DD
   - **Status**: OPEN
   - **Module**: <module/package or class>
   - **Symptom**: <observable behaviour, error message, failing test name>
   - **Minimal reproduction**:
     ```
     <commands or code that reproduces, ideally <10 lines>
     ```
   - **Suspected cause**: <best current guess, or "to investigate">
   - **Investigations**:
     - YYYY-MM-DD: <what was tried, what was learned>
   ```

5. **Create the file with a header** if it does not exist:

   ```markdown
   # BUG.md — <component>

   Reproducible bugs. Convention: see `AGENTS.md` of the Vidocq workspace.

   Statuses: `OPEN` → `INVESTIGATING` → `FIXED` (commit hash) → `CLOSED`.

   ---
   ```

6. **Use absolute dates** — convert "today" / "yesterday" to YYYY-MM-DD using the date provided by the system.

7. **Do not commit** — only edit the file. Report the file path and the new bug ID to the user.

## Updating an existing bug

If the user references an existing BUG-id (e.g. "update BUG-20260504-01, I found the cause"):
- Find the section in `BUG.md`.
- Append a new bullet under `Investigations` with today's date.
- Update `Status` if the user indicates progress (`INVESTIGATING`, `FIXED <hash>`, `CLOSED`).
- Never delete prior investigation entries — they are the audit trail.
