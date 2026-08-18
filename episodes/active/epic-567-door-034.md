<!-- episode-state: schema=1 id=epic-567-door-034 status=active -->

# episode: epic-567-door-034

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 1
- reopens: 0
- rework-count: 2
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/spine.json

## Agent-supplied

### assertion:epic-567-door-034.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Beginning the closeout gate after the last lane merged, with the run's context nearly spent.

### assertion:epic-567-door-034.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A gate whose remaining work is bounded -- episodes, a summary, acceptance -- can be started at whatever context is left.

### assertion:epic-567-door-034.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine refused the start outright: context at 18% is at/over the hard limit, so this is not the moment to BEGIN work here. It named the exact recovery call with a concrete why_ref rather than a placeholder, logged the refusal to a trip ledger and a permanent trip history, and left the DIGEST as the handoff a fresh agent would read. After the session was compacted the advisory cleared on its own and the same start succeeded.

### assertion:epic-567-door-034.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: None to the run. The refusal held the gate closed for one exchange.

### assertion:epic-567-door-034.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Compaction rather than the refresh handshake, at the human's instruction. The engine reads context from a gauge file the hook rewrites, so a compacted session presents fresh and the same call is permitted.

## Diagnosis (optional)

### assertion:epic-567-door-034.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: This is a hard refusal on begin, distinct from the soft-band advisory the Stop hook overrides -- the engine blocks starting new work at low context but never blocks closing the gate already open.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
