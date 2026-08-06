# Crash-resume state note — issue-419-governor-identity

- **step:** execute · entering gate e0-context, then g1-implement
- **slug:** issue-419-governor-identity · branch `epic-418/a-419-governor-identity` · worktree `C:/Programs/constellation-skills-wt/epic418-a-419`
- **next command:** `cd C:/Programs/constellation-skills-wt/epic418-a-419 && py scripts/checklist_engine.py --file .agent-work/issue-419-governor-identity/execute.json current`
- **pid:** none — foreground; crews dispatch via `run_crew.py --dispatch external` as synchronous Agent-tool subagents
- **expected artifact:** `.agent-work/issue-419-governor-identity/RETURN.md` at the worktree root plus `RETURN.md`; per-gate artifacts under `.agent-work/issue-419-governor-identity/`

Resume notes for a fresh Commander: the engine lease is
`commander-issue-419-governor-identity` — re-claim with the same id (idempotent). The spine is
`.agent-work/issue-419-governor-identity/spine.json`, the frozen gate plan is `execute.json` beside it.
Read `PROBLEM_STATEMENT.md` (the probe result that froze the design branch), `MISSION_FRAME.md`, and
`CRITIC_TRIAGE.md` (20 dispositioned critic findings) before touching anything. The test runner is
`python -m pytest`, never `py -m unittest`.

_Updated: 2026-08-05T23:55:00Z_
