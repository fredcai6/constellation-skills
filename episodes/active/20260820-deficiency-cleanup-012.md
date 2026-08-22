<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-012 status=active -->

# episode: 20260820-deficiency-cleanup-012

## Mechanical
- run: 20260820-deficiency-cleanup
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/20260820-deficiency-cleanup/lane-evidence

## Agent-supplied

### assertion:20260820-deficiency-cleanup-012.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Sweep the epic's seven worktrees as routine cleanup after merge.

### assertion:20260820-deficiency-cleanup-012.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Removing a merged worktree discards a working copy whose commits are already preserved on a branch.

### assertion:20260820-deficiency-cleanup-012.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Crew evidence for two lanes existed only as untracked files inside those /tmp worktrees -- handoffs, both reviewer results, engine surveys, journals and Fowler passes, including the entire record for the batch the human was being asked to merge. git worktree remove would have deleted all of it silently and unrecoverably.

### assertion:20260820-deficiency-cleanup-012.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The audit trail for the change under decision would have been destroyed by the tidy-up step that followed the decision.

### assertion:20260820-deficiency-cleanup-012.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: 1.6M of lane evidence was copied into the epic work area and committed before any worktree was removed. A stale bytecode cache came with that copy and was caught immediately afterward by the repository's own provenance guard, which named the foreign source path rather than letting an inherited cache surface later as an unrelated error.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
