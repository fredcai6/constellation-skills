<!-- episode-state: schema=1 id=epic-567-door-024 status=active -->

# episode: epic-567-door-024

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 1
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-024.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A crew needing a check waived that it is forbidden to waive itself, escalating to its parent as the engine instructs.

### assertion:epic-567-door-024.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The parent would waive it.

### assertion:epic-567-door-024.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The parent could not: the engine refuses an action on a checklist an active session owns, and the two routes its refusal names are both defects this epic filed -- passing the child's session id is impersonation, and a forced claim erases actor attribution. The working sequence is release, parent claims, parent waives, parent releases, child reclaims, and it is written down nowhere. Two lanes hit it in one wave.

### assertion:epic-567-door-024.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Two round trips between parent and child, and a recovery that existed only in the messages the two exchanged.

### assertion:epic-567-door-024.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The handshake was performed by hand both times and staged as a candidate on the second occurrence, with the recurrence stated, because one occurrence reads as bad luck and two in a wave is a mechanism.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
