<!-- episode-state: schema=1 id=epic-418-redux-004 status=active -->

# episode: epic-418-redux-004

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
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-418-redux/closeout/harvest_probe.sh

## Agent-supplied

### assertion:epic-418-redux-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Prepare the closeout harvest so that a worktree is never swept while it still holds something durable, after finding that the harvest step reports 'nothing to collect' identically whether a worktree is empty or the doctrine is looking for a retired filename.

### assertion:epic-418-redux-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A probe written specifically to remove that ambiguity would distinguish an empty worktree from a worktree whose content it could not see.

### assertion:epic-418-redux-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Version 1 tested whether a file existed and reported PRESENT for every worktree ever created, because that file is tracked and arrives with any checkout. Version 2 replaced it with two git channels and was blind to gitignored paths, found only when a worktree showed 379 files on disk against 371 on main while both channels reported clean. Version 3 added a third channel.

### assertion:epic-418-redux-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Each revision narrowed the blindness without eliminating it, and each version read as correct to its author at the time of writing. The v1 defect was visible only because seven worktrees returned byte-identical findings, one of them provisioned forty minutes earlier with nothing in it.

### assertion:epic-418-redux-004.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The v3 script reports ignored paths and explicitly declines to judge them, on the grounds that it cannot distinguish a disposable transient from a real local artifact and its reader can. Its own prior defects are recorded in a comment block at the top rather than only in the fix.

## Diagnosis (optional)

### assertion:epic-418-redux-004.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The author of a countermeasure understands the defect it targets, and that understanding is what makes the countermeasure hard to read cold. This was the second occurrence in the same run; the first was a pre-staged fixture that reproduced the shape error it was built to prevent.

### assertion:epic-418-redux-004.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: Both defects surfaced when the tool was run against a case that should have made it fail, and neither surfaced from re-reading it. The cheapest such case in both instances was already present in the environment.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
