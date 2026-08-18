<!-- episode-state: schema=1 id=epic-567-door-003 status=active -->

# episode: epic-567-door-003

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A regrowth guard for #559, whose stated deliverable was the guard rather than the deletion.

### assertion:epic-567-door-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A guard authored after the sweep, red-proofed by reintroducing a clause.

### assertion:epic-567-door-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Lane D1 authored the guard BEFORE sweeping, against the still-dirty tree, so its failing state was produced by the real corpus rather than by a fixture its own author wrote to match. It also asserts its own walk reaches at least 60 files, so it cannot silently scan nothing, and it roots that walk at the overlay directory rather than at .agent-work/ so run artifacts that quote the clause are excluded structurally rather than by an exception list.

### assertion:epic-567-door-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: None; the guard is stronger than the launch order specified in three independent ways.

### assertion:epic-567-door-003.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: None needed. The guard-first ordering was the lane's own design choice, not an instruction.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
