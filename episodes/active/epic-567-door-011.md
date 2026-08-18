<!-- episode-state: schema=1 id=epic-567-door-011 status=active -->

# episode: epic-567-door-011

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

### assertion:epic-567-door-011.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A file-ownership table fencing five concurrent lanes off each other's files.

### assertion:epic-567-door-011.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: One writer per file, with the fence drawn from each lane's mission.

### assertion:epic-567-door-011.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Three fences were wrong in the same way. episodes/ was assigned to one lane while the Commander spine mandates episode capture from every lane, and the store has no shared index to collide on. tests/data/store_mentions.approved.txt was granted to one lane while another was already required to edit it. And the .agent-work/templates/ overlay was assigned to nobody, while the guard one lane was building rglobs exactly that directory -- so that lane's guard would have failed on its own branch over files no lane owned.

### assertion:epic-567-door-011.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The third would have blocked the epic's headline deliverable. The first caused a delivering lane's correct behaviour to be flagged as a possible violation until it was checked.

### assertion:epic-567-door-011.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Each was granted on discovery. The ownership table was built from the lanes' missions rather than measured against the guard's reach and the tree's actual state.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
