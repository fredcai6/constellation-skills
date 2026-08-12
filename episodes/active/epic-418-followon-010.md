<!-- episode-state: schema=1 id=epic-418-followon-010 status=active -->

# episode: epic-418-followon-010

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

### assertion:epic-418-followon-010.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Commit staged work and launch the next dispatch detached in a single shell command, then read the resulting HEAD.

### assertion:epic-418-followon-010.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: git add && git commit && nohup ... & would run the first two synchronously and background only the dispatch.

### assertion:epic-418-followon-010.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: & binds looser than &&, so the entire chain was backgrounded. The following git log read a stale HEAD and reported the commit missing, though the work landed correctly moments later.

### assertion:epic-418-followon-010.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A false 'the commit did not land' reading, and the investigation it triggered, on work that was in fact fine.

### assertion:epic-418-followon-010.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Group the synchronous half explicitly, or run the commit and the detached launch as separate commands; never read state from the same chain that backgrounds itself.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
