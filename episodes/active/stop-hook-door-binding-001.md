<!-- episode-state: schema=1 id=stop-hook-door-binding-001 status=active -->

# episode: stop-hook-door-binding-001

## Mechanical
- run: stop-hook-door-binding
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/stop-hook-door-binding/MISSION_FRAME.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: scripts/hooks/spine_rail.py
- artifact-ref: tests/test_spine_rail.py
- artifact-ref: .claude/settings.json

## Agent-supplied

### assertion:stop-hook-door-binding-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Closed the Stop hook's mid-flight refusal gap for a spine claimed through the MCP door instead of a Bash checklist_engine.py command.

### assertion:stop-hook-door-binding-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: decide_stop and _mid_flight_reason needed no change; only a second binding-recording source was expected to be missing from handle_post_tool_use.

### assertion:stop-hook-door-binding-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: handle_post_tool_use recognized only a Bash checklist_engine.py claim/release command; a door-issued spine_lease claim recorded no binding, so decide_stop allowed a mid-flight turn-end silently. A second dispatch path (tool_name == "mcp__spine__spine_lease", resolving the claimed spine from this process's own SPINE_FILE/SPINE_SESSION environment) closed the gap without touching decide_stop or _mid_flight_reason, matching the diagnosis exactly. RED was reproduced independently twice -- once by this Commander and once by the dispatched reviewer, each via git stash push/pop isolating scripts/hooks/spine_rail.py alone -- and both reproductions failed genuinely against the pre-fix code.

### assertion:stop-hook-door-binding-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The gap this run closed was cited, in the launch order's own evidence, as the mechanism behind six lost Commander dispatches earlier the same day, each costing a full dispatch.

### assertion:stop-hook-door-binding-001.a5
- kind: workaround
- strength: weak
- lifecycle-standing: active
- statement: No workaround was needed for the core fix -- it landed cleanly on the first implementer attempt, with both RED reproductions and all CONTROL/fail-open cases passing on that same attempt.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
