<!-- episode-state: schema=1 id=epic-567-door-026 status=active -->

# episode: epic-567-door-026

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 1
- reopens: 1
- rework-count: 2
- failed-commands: 1
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: scripts/run_crew.py
- artifact-ref: tests/test_role_tier_coverage.py

## Agent-supplied

### assertion:epic-567-door-026.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: The epic's closing dispatch, sent under the role name every delegated Commander in this epic had already been dispatched under.

### assertion:epic-567-door-026.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The role tier table merged one wave earlier would resolve a model for it, since the table was proved against a live crew before merge.

### assertion:epic-567-door-026.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The dispatch was refused by that table: no model tier declared for role 'commander-delegated' under harness 'claude' -- refusing rather than guessing. Live doctrine names 7 role terms (reviewer 84, commander 74, implementer 42, critic 29, admiral 22, cartographer 8, commander-delegated 7) and the table declared the first six. The omitted key was the one 10 registry entries in this epic used.

### assertion:epic-567-door-026.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One full gate cycle: a lane opened, worktreed, dispatched, gated and merged solely to declare one key and guard its provenance. The epic's own deliverable blocked the epic.

### assertion:epic-567-door-026.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: None taken at the refusal point. The lane declared the key at the human's ruled tier and added a guard that scans doctrine for the property the table depends on.

## Diagnosis (optional)

### assertion:epic-567-door-026.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The refusal is the design working -- failing closed on an undeclared role rather than guessing a tier, pinned by tests/test_crew_launcher.py:1123. What was wrong was the provenance of the key set: it enumerated the roles its author expected the corpus to use, and the proof-of-life covered one key rather than the set.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
