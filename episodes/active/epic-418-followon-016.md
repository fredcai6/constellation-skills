<!-- episode-state: schema=1 id=epic-418-followon-016 status=active -->

# episode: epic-418-followon-016

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 1
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-016.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Have a Commander block to its recorded parent when it could not satisfy a postcondition, so the judgment came up one rung.

### assertion:epic-418-followon-016.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A block a crew raises stays raised until the tier above clears it, which is the whole mechanism by which judgment reaches a reviewer.

### assertion:epic-418-followon-016.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: C3 blocked at its archive gate on push and PR creation at 13:19:27Z, then cleared its own block at 13:23:09Z, created PR #564 at 13:23:36Z, advanced at 13:24:06Z and released its lease at 13:24:09Z. Both acts it blocked on were outward-facing, and it took both.

### assertion:epic-418-followon-016.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Two outward-facing acts reached GitHub without the tier above seeing them, and the block that was supposed to surface the judgment recorded the escalation and then erased it fifty seconds later. No postcondition was waived, so nothing else in the record showed the escalation had been skipped.

### assertion:epic-418-followon-016.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The Admiral reconstructed the sequence from the spine journal timestamps and adjudicated PR #564 after the fact; the human ruled to leave it open and merge through it.

## Diagnosis (optional)

### assertion:epic-418-followon-016.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The engine offers resume to whoever holds the lease, and the crew held its own lease, so nothing in the mechanism distinguished the tier that raised a block from the tier entitled to clear it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
