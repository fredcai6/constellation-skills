# Crash-resume state note — issue-305

- **step:** execute · gate g1-implement (assembly seam: emit the context manifest from `start()`/`reopen()`)
- **slug:** issue-305 · branch `epic-298/305` · worktree `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/issue-305/crew/g1-implement-result.md` (IMPLEMENTER_RESULT), then `scripts/episode_capture.py` existing with `checklist_engine.start()` calling it

**Resume context a fresh agent needs and cannot get from `current` alone:**
Engine lease is `commander-305-e298`; pass `--session-id commander-305-e298` on every mutating
engine call against `spine.json`. The spine is at `.agent-work/issue-305/spine.json`, the gate
plan at `.agent-work/issue-305/execute.json`.

Read `PLAN_CRITIC_DISPOSITION.md` **before** `CONVERGENCE.md` — the disposition reverses the
convergence's seam choice and voids its negative control. Where they disagree the disposition wins.

**Three floats are OPEN with the Admiral** (team-lead): (1) whether adding a refusal counter to
the engine is in scope — `refusals` has no engine-state source; (2) the amended seam recommendation
(`start`/`reopen`, not the `dispatch` chokepoint); (3) whether #305 must make episodes *auto-create*
or only make the mechanical field group fall out mechanically. None blocks building; the plan is
authored so (1) changes one gate, not the shape.

_Updated: 2026-08-01T23:30:00Z_
