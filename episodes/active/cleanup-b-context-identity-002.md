<!-- episode-state: schema=1 id=cleanup-b-context-identity-002 status=active -->

# episode: cleanup-b-context-identity-002

## Mechanical
- run: cleanup-b-context-identity
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-b-context-identity/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-handoff.md

## Agent-supplied

### assertion:cleanup-b-context-identity-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Merge main into the branch as the launch order required, then dispatch the reviewer with the already-written g1-reviewer-handoff.md exactly as the launch order instructed.

### assertion:cleanup-b-context-identity-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A handoff written one leg earlier would still describe the tree the reviewer was about to inspect.

### assertion:cleanup-b-context-identity-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The merge invalidated two of its instructions: its diff range git diff a69bbac4 would have handed the reviewer lane C's and lane D's changes mixed in with the one under review, and its stated main baseline of 3057 was three commits stale while LAUNCH_ORDER-3's own 3089 was also superseded.

### assertion:cleanup-b-context-identity-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Dispatching literally as instructed would have produced a review of the wrong diff against the wrong baseline, which the reviewer could not have detected from inside its own handoff.

### assertion:cleanup-b-context-identity-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The handoff was corrected before dispatch to scope the diff to the single commit 3bc87e93 and to carry a gate-time re-measured baseline, and the reviewer's Workflow Feedback afterwards named that correction as the thing that saved it from reviewing lanes C and D as this lane's work.

## Diagnosis (optional)

### assertion:cleanup-b-context-identity-002.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A handoff naming a merge base rather than the commit under review goes stale the moment the branch takes a merge, while a handoff naming the commit does not.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
