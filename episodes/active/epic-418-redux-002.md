<!-- episode-state: schema=1 id=epic-418-redux-002 status=active -->

# episode: epic-418-redux-002

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: origin-run:epic-418-redux
- artifact-ref: .agent-work/epic-418-redux/launch-orders/LO-w5-c1-gates.md
- artifact-ref: .agent-work/epic-418-redux/closeout/RETROSPECTIVE_SOURCE.md

## Agent-supplied

### assertion:epic-418-redux-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch five crews for a wave, each into its own provisioned worktree, each told to read its completed launch order before any other action.

### assertion:epic-418-redux-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Each crew would find its launch order at the path its dispatch prompt named, since the worktree, the branch and the order had each been verified to exist.

### assertion:epic-418-redux-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The worktrees were cut from one commit and the launch orders were committed afterwards, so no worktree contained its own order and every dispatch prompt named a path resolving to nothing -- five out of five. The first Commander reported it unprompted within its first minute, having recovered by reading the order from the main checkout.

### assertion:epic-418-redux-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Three preconditions were checked and all three passed -- worktree exists, branch exists at the intended base, order exists and is complete. Nothing checked the binding between them, so the composite claim 'this crew can read this order at this address' was never asserted by anyone. The three green lights were identical in the working world and the broken one.

### assertion:epic-418-redux-002.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The four remaining crews were sent the absolute main-checkout path by direct message before any of them reached the missing file, and the first crew needed no correction because it had already resolved the address itself.

## Diagnosis (optional)

### assertion:epic-418-redux-002.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Each artifact was verified in isolation against itself. A composite invariant spanning two artifacts had no reader holding both halves at once, and the author of the address is never that reader.

### assertion:epic-418-redux-002.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The same shape was under active repair one tier down in the same wave -- a crew handoff addressed to an agent name that has since moved -- which suggests the defect is about addressing across a time gap rather than about either tier's particular mechanism.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
