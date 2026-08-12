<!-- episode-state: schema=1 id=epic-418-followon-006 status=active -->

# episode: epic-418-followon-006

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Hold a rework dispatch until the previous crew in that worktree was confirmed dead, since two crews must never share a worktree.

### assertion:epic-418-followon-006.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A pgrep on the crew's command pattern would go quiet once the crew exited, releasing the hold.

### assertion:epic-418-followon-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The pgrep pattern matched the Admiral's own watcher shells, which contained the pattern as an argument. The check could never go false while the watcher ran, so the hold could never release.

### assertion:epic-418-followon-006.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A dispatch was held for hours on a liveness check that was structurally incapable of clearing, and it cleared only when the watcher PIDs were killed by hand.

### assertion:epic-418-followon-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: A liveness check must exclude the checker. Match on the child process rather than a string that the watching command itself carries, and ask whether the check can ever return false before trusting it to gate anything.

## Diagnosis (optional)

### assertion:epic-418-followon-006.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: This is the epic's own 'a check that cannot fail' defect in the Admiral's operating loop rather than in a spine: a gate whose condition is unsatisfiable by construction reads identically to one that is simply not satisfied yet.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
