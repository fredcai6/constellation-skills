<!-- episode-state: schema=1 id=epic-567-door-012 status=active -->

# episode: epic-567-door-012

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

### assertion:epic-567-door-012.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A count of the CLI-fallback occurrences remaining in two files, handed to a lane as its residual scope.

### assertion:epic-567-door-012.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Four occurrences, from a grep.

### assertion:epic-567-door-012.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The guard found six. The grep was literal and the guard is case-insensitive and hyphen-tolerant, so it caught 'CLI-fallback' inside a negation -- 'There is no CLI-fallback table below this one' -- and an invocation buried in prose. A third count, from the lane's earlier pass, said ten addresses. Three counts of the same two files, and only the mechanism was right.

### assertion:epic-567-door-012.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: None; the lane used the guard rather than the handed count.

### assertion:epic-567-door-012.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: None needed. The episode records that a measurement carried in an agent's head lost to the same measurement carried in a mechanism, on this epic's own final task.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
