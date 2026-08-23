<!-- episode-state: schema=1 id=w3-promote-007 status=active -->

# episode: w3-promote-007

## Mechanical
- run: w3-promote
- project: constellation-skills
- role: commander
- spine-step: g7-review
- context-manifest-ref: ctx-w3-promote-g7-review
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0

## Agent-supplied

### assertion:w3-promote-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch an independent reviewer crew (constellation-crew subagent) to verify each implementer gate's work, expecting it to drive the engine (claim a lease, use spine_status/spine_advance) per the constellation-reviewer skill's primary instructions.

### assertion:w3-promote-007.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A dispatched reviewer crew would either drive its own bound spine through the MCP door, or hit a clearly-documented no-spine-bound fallback rarely enough not to be worth separate attention.

### assertion:w3-promote-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Every in-harness crew dispatched this wave (g5's and g7's reviewer, at minimum) reported it could not reach the checklist engine's MCP door -- its own SPINE_SESSION env resolves to the dispatching Commander's own bound spine, not a spine of the crew's own. Each crew correctly fell back to a hand-tracked survey per the constellation-reviewer skill's own documented fallback for "no spine bound," and this never blocked a gate.

### assertion:w3-promote-007.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Zero blocking impact this run -- every fallback worked and produced a real, independently-verified REVIEW_RESULT. But it fired identically at every crew dispatch this wave, suggesting it is the STANDARD path for this dispatch shape, not an edge case.

### assertion:w3-promote-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: None needed -- the skill's own documented fallback handled it cleanly every time.

## Diagnosis (optional)

### assertion:w3-promote-007.d1
- kind: suspected-cause
- strength: weak
- lifecycle-standing: active
- statement: An in-harness subagent dispatched from a live Commander session shares its dispatcher's harness session id by design (to prevent it from driving a spine it does not own), which structurally means it can never resolve to its own bound spine under the current dispatch shape -- this may be the intended, permanent shape rather than a gap, but nobody has confirmed that explicitly.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
