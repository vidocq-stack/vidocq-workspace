# Reports

Each report summarises what was merged on `origin/main` of every repository of the ecosystem
over a window: a release, a fortnight, or a campaign around one topic. Together they are the
history of the project, newest first, between the release notes (per brick) and the commit logs.

## Naming

`YYYY-MM-DD-to-YYYY-MM-DD[-topic].md` — the first and last day of the window, and a short topic
when the window is a campaign rather than a period.

## What a report holds

- **In one paragraph**: what the window was about, for someone who reads nothing else.
- **Activity in numbers**: commits (`git log --no-merges origin/main`), lines, repositories,
  with Mermaid charts.
- One section per theme, not per pull request: the problem, the fix, how it was verified, and
  what the user sees; every fix links its pull request (full Codefloe URL) and its `BUG.md` entry.
- Performance figures point to their `BENCH.md` entry, SonarQube figures to `OPTIMS.md`.
- **Still open / next**.

## History

| Window | Report | In one line |
|---|---|---|
| 2026-10-30 → 2026-10-31 | [The tutorial replay](2026-10-30-to-2026-10-31-tutorial-replay.md) | The tutorial session's ≈ 50 findings fixed so the CLI and the Maven plugin carry every build-time constraint; Vauban's build-time discovery and generated interceptor invokers; SNAPSHOTs on `maven.vidocq.dev`. |
| 2026-10-15 → 2026-10-29 | [Two weeks of Vidocq](2026-10-15-to-2026-10-29.md) | Vidocq 0.4.0-RC1, the SonarQube zero-issue campaign, the CI rework with PR trains, the request-path performance pass, the developer-experience push, and Bodoni. |
