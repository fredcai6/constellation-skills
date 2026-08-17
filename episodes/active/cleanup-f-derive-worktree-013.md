<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-013 status=active -->

# episode: cleanup-f-derive-worktree-013

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 3
- failed-commands: 0
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework3-handoff.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-013.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Sweep the repo for every stale copy of a claim, using the greps the lane's own doctrine prescribes (tc8, raised at g2-implement).

### assertion:cleanup-f-derive-worktree-013.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A grep for a claim's sentence was expected to find every place that sentence appears.

### assertion:cleanup-f-derive-worktree-013.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A claim that wraps across two comment lines is invisible to every line-oriented grep in this lane's doctrine. It hid the g2 reviewer's B1 from three passes. Any handoff saying 'grep for this sentence' is wrong by default in a repo whose prose lives in wrapped comments.

### assertion:cleanup-f-derive-worktree-013.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Three implementer passes on g2 keyed on a symbol name because the defect lived in a wrapped claim no line-oriented search could reach.

### assertion:cleanup-f-derive-worktree-013.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The rework-3 implementer wrote sweep_claims.py, about eight lines that strip comment markers and flatten before matching. It lives in that crew's scratch directory.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-013.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Line-oriented search and wrapped prose are structurally mismatched: the unit the tool matches is smaller than the unit the claim occupies, so the claim is unreachable rather than merely hard to find.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
