<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-014 status=active -->

# episode: cleanup-f-derive-worktree-014

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json

## Agent-supplied

### assertion:cleanup-f-derive-worktree-014.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Repair every claim falsified by g2's deletion of origin_worktree_refusal (tc9, raised at g2-implement).

### assertion:cleanup-f-derive-worktree-014.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The two claim families the rework-3 sweep hunted -- the derive family and the ownership-guard family -- were expected to cover the falsified prose.

### assertion:cleanup-f-derive-worktree-014.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: tests/test_worktree_derivation.py's symlink docstring still reasons about the deleted predicate: 'A realpath here would also make origin_worktree_refusal impure while its purity test stayed green.' It belongs to neither hunted family, and it is the same class of residue g2 fenced to g3 in the two spine_rail files.

### assertion:cleanup-f-derive-worktree-014.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A reader of that docstring is told to reason about a symbol that no longer exists.

### assertion:cleanup-f-derive-worktree-014.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Recorded for routing to g3 or to #610's wave rather than repaired inside g2's scope.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-014.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A sweep scoped to named claim families finds members of those families. Residue that mentions a deleted symbol without asserting either family's claim falls outside the scope by construction.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
