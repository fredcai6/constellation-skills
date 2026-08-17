<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-006 status=active -->

# episode: epic-567-door_cmdr-a-006

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-implement-implementer-result.md

## Agent-supplied

### assertion:epic-567-door_cmdr-a-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Have the implementer prove the narrowed containment root is tested.

### assertion:epic-567-door_cmdr-a-006.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The existing door test suite would discriminate the narrow root from the wide one.

### assertion:epic-567-door_cmdr-a-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The crew mutation-tested its own work and reported that swapping the wide root back in left the WHOLE SUITE GREEN, because every fixture bound a door in a primary checkout -- where --show-toplevel and --git-common-dir return the same path. They diverge only inside a linked worktree.

### assertion:epic-567-door_cmdr-a-006.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The security fix would have shipped untested with 116 door tests passing. The defect was a missing topology, not a missing test, which is harder to notice because the tests look thorough.

### assertion:epic-567-door_cmdr-a-006.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The crew added a linked-worktree fixture with a non-vacuity control; all three root mutations then went red. I re-ran the mutation independently and reproduced 7 failures.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-006.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Every pre-existing fixture constructed a primary checkout, the one topology in which the two root derivations are indistinguishable.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
