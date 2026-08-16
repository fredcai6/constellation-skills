<!-- episode-state: schema=1 id=cleanup-c-liveness-rail-002 status=active -->

# episode: cleanup-c-liveness-rail-002

## Mechanical
- run: cleanup-c-liveness-rail
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: none
- refusals: 11
- reopens: 0
- rework-count: 0
- failed-commands: 3
- artifact-ref: .agent-work/cleanup-c-liveness-rail/spine.json
- artifact-ref: .agent-work/cleanup-c-liveness-rail/execute.json

## Agent-supplied

### assertion:cleanup-c-liveness-rail-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive the top-level spine's execute step and the child execute.json's 8 gates through the engine, per the launch order's explicit instruction that arriving over the context HARD band is not a stop condition: attach a refresh-request, then start, then work.

### assertion:cleanup-c-liveness-rail-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The refresh-request-then-start sequence would be needed once, at the first gate entered while over the HARD band, after which context headroom concerns would not recur mechanically at every subsequent gate.

### assertion:cleanup-c-liveness-rail-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine refused a bare `start` with a HARD-band context message at every single gate boundary this run touched after the first (execute itself, g1-implement, g1-review, g1-integrate, g2-implement, g2-review, g2-integrate, g3-verify, reconcile, triage, review -- 11 refusals total), each requiring the identical attach-refresh-request-then-retry-start two-step before the gate would begin, even immediately after the prior gate had just closed cleanly with fresh evidence.

### assertion:cleanup-c-liveness-rail-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Each refusal cost one extra round-trip (an attach call, an incrementing why_ref value tracked by hand, then a retry) but never blocked progress -- the launch order's own guidance ('arriving over HARD is not a stop condition... then work') anticipated exactly this and made the correct action unambiguous every time. The cost was mechanical repetition, not uncertainty about what to do.

### assertion:cleanup-c-liveness-rail-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Followed the launch order's documented sequence literally at each refusal: attach a refresh-request against the active gate with an incrementing why_ref id, then retry start (and, at gates that also needed an artifact attach before advance, attach that too before the refresh-request would let start through). No deviation from the documented recipe was needed at any of the 11 occurrences.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
