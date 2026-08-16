# Triage Recommendation: `CREW_SCRATCH_DIR` is reserved but never consumed by dispatched crews

## Classification
`feature`

## Source checklist/artifact
- `execute.json` `triage_candidates[1]`, surfaced in this run's plan-gate mission frame and both g2 crew results as an honest, explicitly-not-solved gap.

## Structural anchor
`scripts/run_crew.py:890-968` (`crew_env`/`_crew_door_env`, where `CREW_SCRATCH_DIR` is set)

## Cartographer mismatch class
none

## Desired behavior
- **Desired:** a dispatched implementer/reviewer crew reads `CREW_SCRATCH_DIR` from its own environment and writes its evidence/finding files there, so #525's namespacing actually prevents the real-world collision it was filed over (a reviewer's `r0`-`r6` finding-files landing somewhere generic).
- **Today instead:** `run_crew.py` reserves and exposes `CREW_SCRATCH_DIR` in the CLI-backend child's environment (this run's #525 fix), but no dispatched crew's own skill (e.g. `skills/reviewer/SKILL.md`, `skills/implementer/SKILL.md`) reads or writes to it — a crew still picks its own scratch location by whatever convention its skill prose currently names, unchanged by this run.
- **Type:** `measured` — `grep -rn "CREW_SCRATCH_DIR" skills/` (repo-wide, outside `scripts/run_crew.py` and `tests/`) returns no hits as of this run's integration.
- **Rev:** `cleanup/e-crew-tooling` at the commit this run integrated, base `e36e630b`.

## Possible fix
Edit the reviewer/implementer skill prose to read `$CREW_SCRATCH_DIR` when set and default finding-file names/locations there instead of a repo-relative convention. This touches `skills/reviewer/SKILL.md` and/or `skills/implementer/SKILL.md`, both explicitly outside this run's File Ownership (`scripts/run_crew.py`, `scripts/recover_crews.py`, `tests/test_crew_launcher.py`, and new test files only).

## Recommended priority
`medium`

**Reason:** Without this half, #525's fix only prevents the launcher-level collision (two dispatches racing the same directory reservation) — it does not yet close the loop on the originally-measured failure mode (a reviewer's own generic-named finding files landing in a shared location). The collision-avoidance mechanism is in place and tested; the consumption side is the remaining half of the actual user-facing fix.

## Related artifacts
- `.agent-work/cleanup-e-crew-tooling/MISSION_FRAME.md` (Decision Anchors & Decision Pressure section, "consumption gap")
- `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g2-implementer-result.md`

## Disposition
`recommend-and-defer`

**Detail:** Requires editing files outside this run's File Ownership scope (skill prose, not `scripts/run_crew.py`/`recover_crews.py`/tests) — explicitly excluded by this run's launch order. Filing/scoping a follow-up issue is also outside this delegated run's clear issue-creation authority; recommending rather than filing or fixing.

## Issue creation authority
`ask user`
