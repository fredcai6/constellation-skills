<!-- episode-state: schema=1 id=b433-render-directives-002 status=active -->

# episode: b433-render-directives-002

## Mechanical
- run: b433-render-directives
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/b433-render-directives/spine.json
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/b433-render-directives/gauge.json
- artifact-ref: .agent-work/b433-render-directives/STATE_NOTE.md

## Agent-supplied

### assertion:b433-render-directives-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Take over issue #433 as a third, fresh Commander dispatch after two predecessors handed off on context-governor HARD trips, and drive the existing spine to completion.

### assertion:b433-render-directives-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A fresh dispatch with an effectively empty context would read below the governor's soft band and be free to advance the spine.

### assertion:b433-render-directives-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine reported CONTEXT 18% at or over the hard band and refused every `advance`, because `gauge.json` still held the second dispatch's reading (fill 0.184143, observed_at fixed) and nothing refreshed it: the gauge writer PostToolUse hook is not wired into this worktree's .claude/settings.json.

### assertion:b433-render-directives-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Roughly thirty minutes of the dispatch were spent working around a reading that described a different agent, and the block persisted until the record aged past gauge_reader's 30-minute staleness window rather than clearing on any action taken.

### assertion:b433-render-directives-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Do the gate work that needs no `advance` (edits, suite runs, evidence capture) while the inherited record ages out, then advance normally; hand-writing a gauge record or filing a refresh-request for an exhaustion not being experienced were both available and both rejected as false.

## Diagnosis (optional)

### assertion:b433-render-directives-002.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The gauge record carries no identity of the session that wrote it, so a reader cannot tell an inherited reading from a live one, and staleness is the only mechanism that eventually distinguishes them.

### assertion:b433-render-directives-002.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: Either bind the record to its writing session so a successor's reader discounts it, or expose a sanctioned engine verb that invalidates an inherited reading without hand-editing the file.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
