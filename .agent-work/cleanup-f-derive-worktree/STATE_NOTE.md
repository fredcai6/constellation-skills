# Crash-resume state note — cleanup-f-derive-worktree

- **step:** execute · `execute.json` gate `g2-integrate` is **BLOCKED**, bubbled to the Admiral. g1 closed and committed; g3/g4/g5 not started.
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree` · HEAD `b8557ff4` (base was `e36e630b`)
- **next command:** `py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/execute.json current`
- **pid:** none — foreground; no crew is running
- **expected artifact:** `.agent-work/cleanup-f-derive-worktree/FLOAT_TO_ADMIRAL.md` — the three rulings this run is waiting on

**Read first on resume:** `FLOAT_TO_ADMIRAL.md`, then `LAUNCH_ORDER.md`,
`PROBLEM_STATEMENT.md`, `MISSION_FRAME.md`, `UNTAKEN_ROADS.md`, and the cold
critic at `crew-handoffs/plan-plan-critic-result.md`.

**Three Admiral rulings are outstanding.** Do not resume g2, g4 or g5 without
them. **g3 (the Stop hook stops using the worktree for ownership) depends on none
of them and is runnable now** — its handoff is not yet written; the gate plan
imperative in `execute.json` carries the full task.

_Updated: 2026-08-16T18:05:00+00:00_
