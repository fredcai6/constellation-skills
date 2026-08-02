# Triage Recommendation: `Regenerate gold details.json so entity_count lands in committed artifacts (#383 follow-through)`

## Classification
`stale generated map` (stale generated artifact)

## Source checklist/artifact
- review finding (g1-review, #383 run); `.agent-work/issue-383-entity-count/execute.json` triage_candidates tc2

## Structural anchor
`none` / reports/evo/*.details.json (generated artifacts)

## Cartographer mismatch class
`none`

## Problem
#383 fixes the reporter so it now EMITS a positive-int entity_count, proven by unit tests and an
end-to-end code trace. But the committed `reports/evo/*.details.json` artifacts were generated before
the fix and still show entity_count=None. They are stale derived outputs.

## Current truth
- The behavior is fixed and tested (commit 85f4a7d).
- Committed gold/details artifacts predate the fix; regenerating them requires a full gold cycle (slow;
  the Admiral's standing order explicitly allowed a unit-level dof demonstration to avoid this).

## Desired/future concern
On the next gold cycle run, confirm `event_level_metrics[].entity_count` is a positive int in the
freshly written details.json (and the calibration artifact's beta is now free to be non-zero where the
dof signal warrants). This is the artifact-level confirmation of the #383 behavior fix.

## Evidence
- reports/evo/gold_cycle_260603_173742_2018thru2024.details.json: 288/288 scored events entity_count=None (pre-fix)
- Doctrine (ORCHESTRATOR_CONTEXT): "Generated artifacts are derived; edit sources/configuration or regenerate rather than manually editing run outputs."

## Impact
Until a gold cycle is re-run, the canonical committed details.json under-represents the fix. No live
prediction path is affected (the calibration is re-fit at gold-cycle time, not from committed details).

## Suggested scope
- On the next scheduled/triggered gold cycle, verify entity_count is populated in the new details.json
  and capture that the calibration dof term now has the opportunity to engage on real data.

## Non-goals
- Do not hand-edit committed details.json.
- Do not trigger a full gold cycle solely for this (expensive); fold into the next planned run.

## Acceptance criteria
- [ ] Next gold cycle's details.json shows positive-int entity_count for scored events
- [ ] (optional) note whether any module's fitted beta becomes non-zero given the now-varying dof

## Recommended priority
`low`

**Reason:** Behavior is fixed and tested; this is artifact hygiene that the next routine gold run resolves
for free. Not worth a dedicated expensive run.

## Related artifacts
- #383 (this run), commit 85f4a7d
- reports/evo/*.details.json

## Issue creation authority
`ask user`
