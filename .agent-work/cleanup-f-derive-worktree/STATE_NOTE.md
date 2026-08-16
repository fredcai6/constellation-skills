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
them. **g3 depends on none of them, but the engine will not start it while
`g2-integrate` is blocked** — a gated plan works in order, and `skip` would be a
lie (it means overtaken-by-events). Its handoff is written and ready at
`crew-handoffs/g3-implementer-handoff.md`. Either resolve Ruling 1 and g3 follows,
or `amend` the plan to move g3 ahead of g2.

_Updated: 2026-08-16T18:05:00+00:00_
