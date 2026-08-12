<!-- episode-state: schema=1 id=epic-418-followon-018 status=active -->

# episode: epic-418-followon-018

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-018.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Ship close_work so a closing advance archives the work area spine-last, which was wave 7's deliverable.

### assertion:epic-418-followon-018.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: close_work had a passing test suite and five approvals, so its first real invocation would archive the work area.

### assertion:epic-418-followon-018.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Its first real use failed. close_work excluded the literal name spine.json when deciding what to move, so a spine file under any other name was moved before the rest of the work area, and gitignored entries in the work area were not handled.

### assertion:epic-418-followon-018.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The wave-7 deliverable did not survive contact with its own first use, and the repair had to be dispatched against a branch that was already merged into main.

### assertion:epic-418-followon-018.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: R0 derived the excluded name from Path(spine_path).name rather than the literal, and _undo_moved restored the partial move so a failed close leaves the work area as it found it.

## Diagnosis (optional)

### assertion:epic-418-followon-018.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Every test for close_work passed a spine named spine.json, so the literal and the derived name were indistinguishable in the whole test set.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
