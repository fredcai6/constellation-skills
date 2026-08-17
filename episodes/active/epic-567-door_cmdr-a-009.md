<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-009 status=active -->

# episode: epic-567-door_cmdr-a-009

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
- artifact-ref: scripts/run_crew.py
- artifact-ref: tests/test_crew_launcher.py

## Agent-supplied

### assertion:epic-567-door_cmdr-a-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Fence the two implementer crews by file so they could run in parallel without colliding.

### assertion:epic-567-door_cmdr-a-009.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The fences would cover every file the change needed to touch.

### assertion:epic-567-door_cmdr-a-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Neither fence included scripts/run_crew.py, so neither crew owned CREW_ALLOWED_TOOLS -- a hardcoded tuple passed to --allowedTools on every crew dispatch. Without an entry for the new tool, a dispatched crew is silently denied it, and an ExternalBackend crew's door is unbound by construction, so that tool is its only route to its own plan file.

### assertion:epic-567-door_cmdr-a-009.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The feature would have shipped inert for the exact population the issue exists for. The drift-guard test caught it; the comment directly above the tuple describes the same failure from the last time it happened.

### assertion:epic-567-door_cmdr-a-009.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Added the grant entry and moved the count control from 11 to 12, both outside my stated file ownership, and flagged the probable collision with another lane rather than resolving it silently.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-009.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: I applied the wiring-grep rule to the crews' new symbols and not to the grant that decides whether anyone can reach the tool.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
