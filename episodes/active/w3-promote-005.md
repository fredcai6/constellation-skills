<!-- episode-state: schema=1 id=w3-promote-005 status=active -->

# episode: w3-promote-005

## Mechanical
- run: w3-promote
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: ctx-w3-promote-plan
- refusals: 1
- reopens: 2
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w3-promote/execute.json

## Agent-supplied

### assertion:w3-promote-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Complete this bounded issue across a long-running session, handing off cleanly at REFRESH REQUESTED boundaries rather than pushing through context pressure.

### assertion:w3-promote-005.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The launch order stated this wave the Admiral IS watching for REFRESH REQUESTED: markers and will relaunch, contrasted explicitly against wave 2, which raised 8 refresh-requests and had 0 answered.

### assertion:w3-promote-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: 2 refresh-requests were raised this run (plan gate why_ref w-3, execute gate why_ref w-4), and 2 relaunches actually occurred -- this session is attempt-3. Both refresh-requests were answered, matching the launch order's stated fix exactly.

### assertion:w3-promote-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: total_rework stayed 0 across both the top-level commander spine and execute.json's own 20 gates despite 2 mid-run relaunches -- each relaunched attempt picked up cleanly from the prior attempt's own DIGEST/STATE_NOTE.md without re-deriving or redoing any closed gate's work.

### assertion:w3-promote-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none needed -- the mechanism worked as designed this wave.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
