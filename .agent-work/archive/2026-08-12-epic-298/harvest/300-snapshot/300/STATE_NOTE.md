# Crash-resume state note — 300

- **step:** execute · pending, blocked on an outstanding Admiral float (the design-it-twice convergence choice). Spine steps init/context/understand/plan are complete.
- **slug:** work-id 300 · branch `epic-298/300` · worktree `C:/Programs/constellation-skills-wt/298-300` · base commit `b69e6c8`
- **next command:** `cd C:/Programs/constellation-skills-wt/298-300 && py scripts/checklist_engine.py --file .agent-work/300/spine.json current` — then, once the Admiral's convergence ruling has landed, satisfy execute's p1 (reload the commander skill) and p2 (rewrite this note) and drive `.agent-work/300/execute.json` gate by gate via `scripts/run_crew.py`. Gate g1 is fully non-contingent and can start the moment the ruling arrives; gate g2 is the only gate the ruling can delete, and it is removed with the engine's `amend` verb, never a hand-edit.
- **pid:** none — foreground
- **expected artifact:** `.agent-work/verdict-300.md` (already written for the mid-mission return); on continuation, `IMPLEMENTER_RESULT`/`REVIEW_RESULT` per gate under `.agent-work/300/`

**Read before resuming, in this order:** `.agent-work/300/PROBLEM_STATEMENT.md`,
`.agent-work/300/MISSION_FRAME.md`, `.agent-work/300/DIT-COMPARISON.md`,
`.agent-work/300/PLAN_CRITIC_DISPOSITION.md`. Two shell facts that will bite otherwise: use
`python -m pytest`, never `py -m pytest` (the `py` shim's runtime has no pytest on this host), and
every command postcondition assumes cwd = the worktree root, because the engine does not pass `cwd=`
to command checks.

_Updated: 2026-08-01T06:20:00+00:00_
