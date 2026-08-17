<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-002 status=active -->

# episode: cleanup-f-derive-worktree-002

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-f-derive-worktree/REPLAN_INPUT.json
- artifact-ref: .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework4-result.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Verify each crew's before/after claim by re-running the differential harness the crew itself returned, rather than taking the returned numbers on trust.

### assertion:cleanup-f-derive-worktree-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A harness that printed a clean before/after table when its author ran it would print the same table when re-run, so re-running it would be a cheap independent confirmation.

### assertion:cleanup-f-derive-worktree-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Every instrument built on this gate developed a shelf-life defect, in both directions. The implementer's differential pinned its BEFORE arm with `git rev-parse HEAD`, so once the gate was committed it compared the change against itself and printed 26 confirming rows -- that was finding B1, caught only because a reviewer already held a contradicting number. Two reviewer harnesses pinned SUPERSEDED commits, so re-running them unmodified showed already-fixed defects as still live. The Commander also cited a sha it had itself amended away minutes earlier.

### assertion:cleanup-f-derive-worktree-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One false-confirming instrument shipped a defect into review, two false-red instruments each cost a re-measurement and a working-tree arm with guards, and one amended-sha citation cost a reviewer a verification of an empty diff before it could start work.

### assertion:cleanup-f-derive-worktree-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The fifth reviewer built its own instrument before running the crew's, and made every arm print a sha256 and a byte length with a guard asserting all three differed; its clean return was believable for that reason. After the amended-sha incident the Commander cited strings to grep for rather than line numbers or shas, and the later handoffs on this lane carried no stale citation.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
