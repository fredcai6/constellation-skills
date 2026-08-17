<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-011 status=active -->

# episode: cleanup-f-derive-worktree-011

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-rework2-result.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-011.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Re-run a delivered evidence script to confirm a gate's claim still reproduces (tc6, raised at g2-review).

### assertion:cleanup-f-derive-worktree-011.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: An evidence script delivered with a gate was expected to keep reproducing its result after the gate closed.

### assertion:cleanup-f-derive-worktree-011.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: check_no_refusal_added.py diffs the working tree against HEAD, so once the Commander commits the gate, working tree equals HEAD: its assertions pass vacuously while its exit code goes red. This lane commits as each gate closes -- the #617 mitigation -- so HEAD moves under delivered evidence by design.

### assertion:cleanup-f-derive-worktree-011.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A reviewer re-running the instrument reads a vacuous pass and a red exit for the same run, and cannot tell from the output which one describes the code.

### assertion:cleanup-f-derive-worktree-011.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Reviewers on this lane added working-tree arms with explicit guards and pinned a base commit rather than HEAD before believing any row.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-011.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: HEAD is a moving reference, so an instrument that pins one arm to it measures a different comparison after every commit. The mitigation that commits at each gate close is what makes the movement frequent.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
