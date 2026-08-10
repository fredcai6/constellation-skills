<!-- episode-state: schema=1 id=epic-418-followon-commander-424-006 status=active -->

# episode: epic-418-followon-commander-424-006

## Mechanical
- run: epic-418-followon-commander-424
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/commander-424/execute.json
- refusals: 2
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/commander-424/execute.json
- artifact-ref: .agent-work/epic-418-followon/commander-424/STATE_NOTE.md

## Agent-supplied

### assertion:epic-418-followon-commander-424-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Execute a launch order that reordered the gates to g3 first, so that a gate blocked pending DC3's evidence could be resolved on that evidence rather than on argument.

### assertion:epic-418-followon-commander-424-006.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine would allow the later gate to be worked while the blocked gate waited, or allow the pending tail to be reordered ahead of it.

### assertion:epic-418-followon-commander-424-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Neither. A blocked gate holds the active slot: 'REFUSED: g3-implement is not the active gate; start g1-integrate first'. And amend refuses to move a non-pending gate, so the blocked gate could not be reordered either. The engine's only exits from block are resume, which needs the blocker cleared, and skip, which means overtaken by events. There is no legal ordering that reaches evidence sitting at a later gate.

### assertion:epic-418-followon-commander-424-006.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The repair's stated gate order could not be expressed in the engine directly. The plan defect the predecessor had already named -- a claim at one gate with its evidence at a later one -- turned out to be not merely awkward but unrepresentable once the earlier gate blocked.

### assertion:epic-418-followon-commander-424-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The g3 implementer ran as the named blocker-clearing evidence for the blocked gate rather than as its own gate, since the blocker's own text pointed at exactly that measurement. Once the blocked gate closed on that evidence, an amend reordered the pending tail so the engine record matched the executed order, with the launch order cited as authority. The g3 gates were then driven normally against the already-returned artifact.

## Diagnosis (optional)

### assertion:epic-418-followon-commander-424-006.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The engine models a block as a state of the active gate rather than as a dependency between gates, so it has no way to express 'still needed, evidence pending elsewhere'. Whether that is a gap or a deliberate refusal to make a mis-cut plan comfortable is genuinely unclear -- a gate that cannot close on its own evidence is arguably the real defect.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
