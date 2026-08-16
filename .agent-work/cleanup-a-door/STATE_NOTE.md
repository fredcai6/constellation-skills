# Crash-resume state note — cleanup-a-door

- **step:** execute · gate g1-implement (#604 telemetry-never-fatal)
- **slug:** cleanup-a-door, branch `cleanup/a-door`, worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door`
- **next command:** `cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door && py scripts/checklist_engine.py --file .agent-work/cleanup-a-door/execute.json current`
- **pid:** none — foreground; crews dispatch via `scripts/run_crew.py`, whose own PID is recorded per entry in `.agent-work/cleanup-a-door/crew-runs.json`
- **expected artifact:** `.agent-work/cleanup-a-door/crew-handoffs/g1-implementer-result.md`

Spine lease: `commander-cleanup-a-door` on `.agent-work/cleanup-a-door/spine.json`.
Resume by re-claiming the same session id (idempotent) — no `--force` needed for a
routine relaunch as of #601.

_Updated: 2026-08-16T12:45:00+00:00_
