<!-- episode-state: schema=1 id=epic-567-door-001 status=active -->

# episode: epic-567-door-001

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

### assertion:epic-567-door-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Resumption of epic 567 by a fresh Admiral, whose first act was binding the epic's existing spine through the MCP door rather than through the CLI.

### assertion:epic-567-door-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The prior session's handoff predicted this would work, because .mcp.json launches the door from the repo and a fresh process therefore gets the spine_bind verb with no install sync.

### assertion:epic-567-door-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: spine_bind returned SPINE_SESSION constellation/epic-567-door with already_bound false on the first call, and the whole epic ran to completion through the door with no CLI invocation by the Admiral. The verb was first used, in anger, by the role it had blocked one session earlier -- that Admiral's spine_status had returned REFUSED, no spine is bound to this door.

### assertion:epic-567-door-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Zero cost; it removed the blocker the epic existed behind. It is also the epic's own definition-of-done clause satisfied by the run performing it.

### assertion:epic-567-door-001.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: None needed.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
