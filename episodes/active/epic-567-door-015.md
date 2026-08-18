<!-- episode-state: schema=1 id=epic-567-door-015 status=active -->

# episode: epic-567-door-015

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

### assertion:epic-567-door-015.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Five Commanders dispatched into isolated worktrees, each to drive its own spine through the door end to end.

### assertion:epic-567-door-015.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A door bound to each lane's own spine, since the epic had just shipped spine_bind.

### assertion:epic-567-door-015.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: spine_bind refuses a sibling worktree deliberately, and its refusal recommends the CLI -- which read as proof the CLI was still load-bearing for dispatched crews, and was escalated to the human as a material exception. It was the wrong conclusion. A door launched from the lane's own worktree with SPINE_FILE set anchors to that worktree and binds that lane's spine, so the dispatched-crew case is answered by launch rather than by bind.

### assertion:epic-567-door-015.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: An hour of the human's attention was spent on an exception that did not exist, and the escalation briefly put the epic's central claim in doubt.

### assertion:epic-567-door-015.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: All five lanes were launched through run_crew --backend cli --spine, each with its own bound door, verified per process before the wave proceeded. The refusal text was correct advice for an already-wrongly-anchored door and said nothing about how lanes are launched.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
