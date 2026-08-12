<!-- episode-state: schema=1 id=epic-559_c3-lifecycle-005 status=active -->

# episode: epic-559_c3-lifecycle-005

## Mechanical
- run: epic-559/c3-lifecycle
- project: constellation-skills
- role: commander
- spine-step: g3-integrate
- context-manifest-ref: LAUNCH_ORDER-C3@293b7721
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c3-lifecycle/crew-handoffs/g3-reviewer-result.md

## Agent-supplied

### assertion:epic-559_c3-lifecycle-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Verify, before accepting g3, that spine_open's dispatch path never references SPINE, SESSION or run_engine -- the property that makes 'it does not presuppose a bound spine' a checked fact rather than a claim.

### assertion:epic-559_c3-lifecycle-005.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Expected an AST scan for those names inside the function to answer the question directly.

### assertion:epic-559_c3-lifecycle-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: My first scan reported call_lifecycle_tool referencing both run_engine and SESSION. Both hits were in the function's DOCSTRING, which explains why those names are absent from the code. The check ran correctly and the value it reported was wrong -- the same absence-and-ubiquity shape the wave's review standard names, in my own hands rather than a crew's.

### assertion:epic-559_c3-lifecycle-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One wasted verification round, and it nearly produced a spurious BLOCK against a correct implementation.

### assertion:epic-559_c3-lifecycle-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Re-ran the scan against the function body with the docstring stripped, over the specific _spine_open node rather than the dispatcher, then separately falsified the crew's own pin by injecting a SESSION reference and watching it go red.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
