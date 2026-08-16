<!-- episode-state: schema=1 id=cleanup-e-crew-tooling-005 status=active -->

# episode: cleanup-e-crew-tooling-005

## Mechanical
- run: cleanup-e-crew-tooling
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0

## Agent-supplied

### assertion:cleanup-e-crew-tooling-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Advanced g2-integrate, whose command postcondition re-runs the full test suite (roughly 2 minutes).

### assertion:cleanup-e-crew-tooling-005.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Expected the advance call to complete synchronously within the tool's default timeout, as every prior advance in this run had.

### assertion:cleanup-e-crew-tooling-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The harness auto-backgrounded the advance call after its 120-second default timeout, since the wrapped full-suite command took about 125 seconds. This matched crew-dispatch.md's documented warning almost exactly ("the full suite ... takes on the order of two minutes, which is enough to trigger it"), including for a direct engine advance call, not only a crew dispatch.

### assertion:cleanup-e-crew-tooling-005.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: No lost work: the backgrounded command was polled to completion in a foreground until-loop against its own output file rather than ending the turn to wait for a notification, per crew-dispatch.md's explicit recipe, and it completed successfully (g2-integrate -> complete) about 20 seconds after being backgrounded.

### assertion:cleanup-e-crew-tooling-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Polled the backgrounded command's output file with a foreground until-loop (grep for a completion marker, sleep 5) rather than relying on a background-task notification to resume the turn.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
