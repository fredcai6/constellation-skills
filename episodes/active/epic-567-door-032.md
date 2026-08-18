<!-- episode-state: schema=1 id=epic-567-door-032 status=active -->

# episode: epic-567-door-032

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 6
- reopens: 0
- rework-count: 2
- failed-commands: 6
- artifact-ref: .agent-work/epic-567-door/transitions/w4/REPLAN_INPUT.json
- artifact-ref: .agent-work/epic-567-door/transitions/w4/REPLAN_RESULT.json

## Agent-supplied

### assertion:epic-567-door-032.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Authoring the wave-4 replan transition packet that closes the epic's last wave boundary with decision=stop.

### assertion:epic-567-door-032.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Copying the previous boundary's INPUT and updating it would produce a valid packet, since the templates are the same two files at every boundary.

### assertion:epic-567-door-032.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The verifier refused six times in sequence, each on a different rule: completed_outcomes entries must be objects; completed and open ids must exactly partition the current-wave issue ids, twice; result.current_wave.issues must be nonempty even when the decision is to stop; a discrepancy classification forces a specific disposition action; material_changes entries must be objects. The two partition failures came from copying the previous INPUT, whose current_plan.current_wave still held the wave before it.

### assertion:epic-567-door-032.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Six verifier round-trips to author one packet, all at the boundary where the epic had nothing left to launch.

### assertion:epic-567-door-032.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Chain the previous boundary's RESULT current_wave into the next boundary's INPUT current_plan.current_wave, rather than carrying the previous INPUT forward. The verifier enforces this and neither template states it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
