<!-- episode-state: schema=1 id=epic-567-door_cmdr-b-004 status=active -->

# episode: epic-567-door_cmdr-b-004

## Mechanical
- run: epic-567-door/cmdr-b
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-b/AMEND_G2.json
- refusals: 1
- reopens: 1
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-b/execute.json

## Agent-supplied

### assertion:epic-567-door_cmdr-b-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: After the spine was already driven to terminal archive and RETURN.md sent, the Admiral live-messaged a post-return diagnosis of 6 regressions and instructed rework on a specific 3-group breakdown, including a command to regenerate map/INDEX.md (group 3).

### assertion:epic-567-door_cmdr-b-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The Admiral's diagnosis, once received, would be the final, stable instruction to implement against for the remainder of this rework.

### assertion:epic-567-door_cmdr-b-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Group 3 (map/INDEX.md regen) was regenerated locally exactly as first instructed, then the Admiral sent a SECOND, correcting message before the rework's g2-integrate gate closed: withdraw group 3 entirely, because a sibling lane (lane C) hit the identical generated-file staleness and independently regenerating it in two parallel PRs guarantees a merge conflict on the committed artifact -- open issue #544's predicted failure mode, now observed twice in the same wave. The correction arrived mid-flight, after the local regen had already been done and the g2-integrate gate's own postcondition text had already been authored to require it (bundled into one pytest command alongside the 4 in-scope files).

### assertion:epic-567-door_cmdr-b-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The already-regenerated map/INDEX.md had to be reverted (git checkout) before continuing, and g2-integrate's postcondition c1 -- authored to check test_code_map.py's freshness test as part of a compound command -- could no longer pass as written, since leaving that one test red was now the CORRECT and required outcome. The gate was already in-progress (not pending), so the engine's own amend/rescope path (which requires pending status) was not usable; the fix was to run the correct 4-file verification manually and waive c1's stale check-text with an explicit reason, rather than editing the postcondition in place.

### assertion:epic-567-door_cmdr-b-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Waived g2-integrate.c1 (authority admiral, reason citing the Admiral's correction and pasting the real, correct command's green output) instead of trying to force a status transition the engine does not offer for an in-progress gate. Recorded the reasoning explicitly in the waive reason and in RETURN.md, and separately recorded the #544 double-collision itself as REPLAN_INPUT.json discrepancy D2 -- evidence for the Admiral's own epic-level tracking, not something this lane files or fixes.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
