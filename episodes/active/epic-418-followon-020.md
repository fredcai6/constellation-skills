<!-- episode-state: schema=1 id=epic-418-followon-020 status=active -->

# episode: epic-418-followon-020

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/launch-orders/LAUNCH_ORDER-R0-lifecycle-repair.md

## Agent-supplied

### assertion:epic-418-followon-020.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Have the R0 repair crew reproduce each defect before fixing it, since a guard nobody has watched fail is not a guard.

### assertion:epic-418-followon-020.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The crew reproduces, then fixes, then shows the guard refusing the original defect.

### assertion:epic-418-followon-020.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: R0 wrote the fix for the portable-test defect before it had reproduced the failure, then said so in its own result document rather than presenting the work as ordered.

### assertion:epic-418-followon-020.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: None that was measurable: the Admiral independently reproduced both defects by mutating the repaired source and watching the tests refuse the mutation, and both guards fired. The disclosure is what made the independent check targeted rather than general.

### assertion:epic-418-followon-020.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Verified the guards by mutating real source in a foreign checkout rather than by reading the crew's report, and merged on that measurement.

## Diagnosis (optional)

### assertion:epic-418-followon-020.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The launch order named the reproduce-first standard in prose and the spine's gates did not check it, so the ordering rested on the crew's discipline and the crew's honesty caught what the gate did not.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
