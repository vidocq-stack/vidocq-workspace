---
name: log-bug
description: Append a new bug entry to the BUG.md of the current Vidocq sub-project. Use when the user reports a bug, when a TCK test fails with a real implementation bug (not a harness issue), or when a regression is discovered. Creates BUG.md if missing. Triggers on phrases like "log this bug", "track this bug", "BUG.md", "add to BUG.md".
---

# log-bug

Append a bug entry to `<sub-project>/BUG.md` following the Vidocq convention defined in the root `AGENTS.md`.

## When to invoke

- User says: "log this bug", "track this in BUG.md", "add a bug entry", "this is a regression".
- A TCK run failed with a real implementation bug (not Arquillian wiring, not missing artefacts).
- A reproducible incorrect behaviour was identified during a code review or debugging session.

## Procedure

1. **Identify the sub-project**: ask the user (or infer from the working directory / files being discussed) which of `chappe`, `vauban`, `champollion`, `foy`, `cassini`, `vidocq` owns the bug.

2. **Locate or create** `<sub-project>/BUG.md` at the sub-project root (next to its `pom.xml`).

3. **Generate a short ID**: `BUG-<YYYYMMDD>-<NN>` where `NN` is the next free number for that day in the file. If the file is new, start at `01`.

4. **Append a section** at the bottom of `BUG.md` with this structure:

   ```markdown
   ## BUG-YYYYMMDD-NN — <one-line symptom>

   - **Date** : YYYY-MM-DD
   - **Statut** : OPEN
   - **Module touché** : <module/package or class>
   - **Symptôme** : <observable behaviour, error message, failing test name>
   - **Reproduction minimale** :
     ```
     <commands or code that reproduces, ideally <10 lines>
     ```
   - **Hypothèse de cause** : <best current guess, or "à investiguer">
   - **Investigations** :
     - YYYY-MM-DD : <what was tried, what was learned>
   ```

5. **Create the file with a header** if it does not exist:

   ```markdown
   # BUG.md — <sub-project>

   Suivi des bugs reproductibles. Convention : voir `vidocq-workspace/AGENTS.md` (workspace root).

   Statuts : `OPEN` → `INVESTIGATING` → `FIXED` (commit hash) → `CLOSED`.

   ---
   ```

6. **Use absolute dates** — convert "today" / "yesterday" to YYYY-MM-DD using the date provided by the system.

7. **Do not commit** — only edit the file. Report the file path and the new bug ID to the user.

## Updating an existing bug

If the user references an existing BUG-id (e.g. "update BUG-20260504-01, I found the cause"):
- Find the section in `BUG.md`.
- Append a new bullet under `Investigations` with today's date.
- Update `Statut` if the user indicates progress (`INVESTIGATING`, `FIXED <hash>`, `CLOSED`).
- Never delete prior investigation entries — they are the audit trail.
