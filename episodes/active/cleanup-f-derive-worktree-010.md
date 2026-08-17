<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-010 status=active -->

# episode: cleanup-f-derive-worktree-010

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 1
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework2-handoff.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-010.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Complete the g2 rework and return an IMPLEMENTER_RESULT, the artifact that is a crew's completion contract (tc5, raised at g2-implement).

### assertion:cleanup-f-derive-worktree-010.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A crew that finishes and verifies its work was expected to have that work counted as delivered.

### assertion:cleanup-f-derive-worktree-010.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The g2 rework-1 implementer finished and verified its work at 3196 passed / 5 skipped / 0 failed, then died in its final step before writing the result artifact. The implementation and every measurement survived on disk; the write-up did not.

### assertion:cleanup-f-derive-worktree-010.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A successor crew had to reconstruct the result from the dead crew's plan.json and evidence files, and the gate carried an extra round it had already earned.

### assertion:cleanup-f-derive-worktree-010.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The successor was handed the dead crew's evidence directory explicitly and told its work was already in the tree, so it inherited both halves rather than redoing the first.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-010.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The completion contract is a single artifact written last, so every crash before that write loses the whole write-up regardless of how much work survives. Evidence is already checkpointed as it goes; the result is not.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
