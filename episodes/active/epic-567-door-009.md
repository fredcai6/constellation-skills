<!-- episode-state: schema=1 id=epic-567-door-009 status=active -->

# episode: epic-567-door-009

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

### assertion:epic-567-door-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A watcher over five dispatched lanes, reporting progress, delivery and death.

### assertion:epic-567-door-009.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A liveness check distinguishing a live crew from a dead one.

### assertion:epic-567-door-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The check used grep over /proc/*/environ and treated a nonzero exit as 'process gone'. Only 139 of 625 entries were readable, so grep exited 2 -- an error, not a no-match -- and it reported all five lanes dead one second after a separate poll had shown all five alive and advancing. The check returned the same answer whether a lane was dead or merely unreadable.

### assertion:epic-567-door-009.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Zero, by luck of timing: a contradicting poll was one second old. The sanctioned response to 'died with no artifact' is to relaunch, which would have put a second Commander into each of five live worktrees.

### assertion:epic-567-door-009.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Replaced with the method already proven at launch -- pgrep plus a readable /proc entry -- and given a third state, so 'cannot determine' never reports death. Red-proofed against both failure modes before being trusted.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
