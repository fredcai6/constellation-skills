<!-- episode-state: schema=1 id=epic-567-door_cmdr-c-001 status=active -->

# episode: epic-567-door_cmdr-c-001

## Mechanical
- run: epic-567-door/cmdr-c
- project: constellation-skills
- role: commander
- spine-step: understand
- context-manifest-ref: .agent-work/epic-567-door/cmdr-c/MISSION_FRAME.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-c/crew-handoffs/g1-implementer-result.md
- artifact-ref: .agent-work/epic-567-door/cmdr-c/crew-handoffs/g1-reviewer-result.md
- artifact-ref: .agent-work/epic-567-door/cmdr-c/REPLAN_INPUT.json

## Agent-supplied

### assertion:epic-567-door_cmdr-c-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Make the engine's RAIL banner and HARD refusal actionable to a cold agent (#442), and state that the Stop hook outranks the context-trip advisory (#595), per LAUNCH_ORDER_C, editing scripts/hooks/spine_rail.py as the sole-owned file.

### assertion:epic-567-door_cmdr-c-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The launch order's own File Ownership section said this lane was sole writer of 'the rail/refusal/advisory strings wherever they are authored,' which read as though both issues' target text was reachable from within the lane's scope, modulo the Fence section's separate warning that this was 'a genuine possibility.'

### assertion:epic-567-door_cmdr-c-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: grep-confirmed at base commit 600de020: the RAIL banner text (_RAIL_STRINGS, scripts/checklist_engine.py:310-326, explicitly marked FROZEN/verbatim -- a measurement precondition for #145), the HARD refusal's attach-refresh-request remedy string (_refresh_attach_hint, same file, line 1532-1543), and the context-trip SOFT advisory's own wording (_trip_advisory, line 1858-1861) are ALL authored in scripts/checklist_engine.py, fenced to a concurrent lane (Lane A, #559) this wave. scripts/hooks/spine_rail.py, this lane's sole-owned file, contains only the Stop hook's SPINE MID-FLIGHT refusal text -- the one piece of either issue's target text actually in reach.

### assertion:epic-567-door_cmdr-c-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Zero surface existed inside the sole-owned file for #442's stated acceptance criterion (a cold agent acting correctly on the actual RAIL banner/HARD refusal text) -- that half of the mission could not be attempted, only floated, no matter how the run was planned. The mission frame had to be written around a scope reduction discovered mid-run rather than at dispatch, and the cold-agent measurement the pre-ruling anticipated for #442 had nothing to measure (no rewrite existed to test).

### assertion:epic-567-door_cmdr-c-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Scoped the plan to the one deliverable actually in reach (Stop-hook precedence text in spine_rail.py + the same precedence stated in skills/commander/references/crew-dispatch.md, which the pre-ruling separately named as in-scope shipped doctrine), delivered it through a full implement/review/fresh-process-validate cycle, and recorded the fenced-out half as two triage candidates (tc2, tc3) plus a blocks_current_wave_exit discrepancy in REPLAN_INPUT.json for the Admiral to sequence once the fence lifts.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-c-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A launch order's File Ownership grant ('X and the Y strings wherever they are authored') and its Fence section (naming two specific files as off-limits) can describe the SAME piece of work in mutually narrowing terms, and only reading the actual source (not just the two doctrine sections) reveals how much the fence actually removes from the grant.

### assertion:epic-567-door_cmdr-c-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: When a launch order names a Fence as 'a genuine possibility, expect it and ask early,' treat that as a strong signal to grep the target strings' actual file location during understand/context, before writing the mission frame or the gate plan, rather than after planning reveals the collision.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
