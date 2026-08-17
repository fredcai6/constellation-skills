<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-004 status=active -->

# episode: epic-567-door_cmdr-a-004

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-a/MISSION_FRAME.md
- artifact-ref: .agent-work/epic-567-door/cmdr-a/map-orientation.json

## Agent-supplied

### assertion:epic-567-door_cmdr-a-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a mission frame from the mandated template and satisfy the plan step's verify-frame gate.

### assertion:epic-567-door_cmdr-a-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A frame following templates/MISSION_FRAME.template.md would pass verify-frame.

### assertion:epic-567-door_cmdr-a-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It refused with FRAME-REFUSED, exit 10, problems: 15 -- one per anchor. Under a degraded map, frame_verdict appends a problem for every token matching struct|capability|event|constraint|assumption|claim|decision, unconditionally. The template requires graded decision: anchors, so following it guarantees refusal. Measured the inverse: a five-line frame with zero anchors citing one pinned substitute returns FRAME-OK, exit 0.

### assertion:epic-567-door_cmdr-a-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The gate prefers the emptier artifact. An author who does not notice learns, correctly from the feedback, to stop writing constraint and decision anchors.

### assertion:epic-567-door_cmdr-a-004.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Kept the 15-anchor frame, took the recorded waiver the imperative sanctions, and substituted a check at the same rigor level: every symbol:line anchor must appear on that line of a real source file. That substituted check immediately caught two stale line numbers.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: map/ids.jsonl is tracked and 0 bytes, so every run in this repo orients DEGRADED and reaches this branch.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
