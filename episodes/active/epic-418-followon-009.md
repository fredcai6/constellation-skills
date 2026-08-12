<!-- episode-state: schema=1 id=epic-418-followon-009 status=active -->

# episode: epic-418-followon-009

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Harvest each commander worktree's CONSTELLATION_FEEDBACK.md before git worktree remove destroys it, as closeout doctrine requires.

### assertion:epic-418-followon-009.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Some worktrees would carry an untracked feedback export that removal would lose.

### assertion:epic-418-followon-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The file is tracked in this repo, so it appears in every checkout by construction. Across all 21 worktrees it was present, identical and unmodified, with no untracked copy anywhere under any of them. Every crew wrote its feedback into a committed result artifact instead.

### assertion:epic-418-followon-009.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The harvest requirement is why 22 worktrees stood at once, held against a rescue that had nothing to rescue; the disk and the merge-conflict surface of map/INDEX.md across those branches were the real cost.

### assertion:epic-418-followon-009.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: A close that archives the whole work area it created does not need to guess what to rescue, and is correct whether or not anything was exported.

## Diagnosis (optional)

### assertion:epic-418-followon-009.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The step was written when the export was untracked, and survived the change that tracked it because nothing re-measured whether it still guarded anything.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
