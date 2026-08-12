<!-- episode-state: schema=1 id=epic-418-followon-commander-424-005 status=active -->

# episode: epic-418-followon-commander-424-005

## Mechanical
- run: epic-418-followon-commander-424
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/commander-424/MEASUREMENT.md
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/commander-424/evidence/g4-dc5/dc6-mcp
- artifact-ref: .agent-work/epic-418-followon/commander-424/evidence/g4-dc5/dc6b-mcp

## Agent-supplied

### assertion:epic-418-followon-commander-424-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Measure DC6: whether the Context Governor's threshold instruction arrives through an MCP tool result and is acted on.

### assertion:epic-418-followon-commander-424-005.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Seeding a gauge.json past the hard band in the spine's directory, then dispatching a cold agent through the door, would put the threshold instruction into the agent's tool results.

### assertion:epic-418-followon-commander-424-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first arm produced zero tool results carrying the instruction, and the agent drove the spine straight to done. Read as behaviour alone this looked exactly like a measured negative -- the instruction arrived and was ignored. The server's own call log showed something else: 'CONTEXT GAUGE DECLINED: the reading at this path (90% on claude-opus-4-8) was sampled 17s BEFORE session dc6-mcp-sid claimed this checklist, so it is NOT this session's reading'. The gauge was seeded before the claim, the engine correctly declined it, and no threshold instruction was ever emitted. Nothing about DC6 had been measured.

### assertion:epic-418-followon-commander-424-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One wasted arm, and a near-miss on reporting an UNMEASURED condition as a measured negative -- which would have recorded a defect in the door that the evidence did not support. The re-run, writing the gauge after the claim, produced the instruction in 2 of 33 tool results and an agent that acted on it, so the two runs differ in verdict entirely because of fixture ordering.

### assertion:epic-418-followon-commander-424-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: A second arm claimed the lease first, then wrote the gauge, then dispatched. The failed arm was kept in the evidence directory and reported in MEASUREMENT.md as UNMEASURED rather than deleted or quietly re-run.

## Diagnosis (optional)

### assertion:epic-418-followon-commander-424-005.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The staleness guard's failure mode is indistinguishable from the behaviour under test when observed from the agent's side: both produce a run with no threshold instruction and an agent that keeps working. The distinguishing evidence exists and is explicit, but it lives in the server call log rather than in the agent's record, so it is only seen if the null result is investigated rather than accepted.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
