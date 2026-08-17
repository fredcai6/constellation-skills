<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-009 status=active -->

# episode: cleanup-f-derive-worktree-009

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 2
- failed-commands: 0
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/execute.json

## Agent-supplied

### assertion:cleanup-f-derive-worktree-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Keep three prose copies of the leaseless-widening claim in agreement across scripts/checklist_engine.py's module header, tests/test_spine_origin_isolation.py's module docstring, and docs/CHECKLIST_SCHEMA.md (tc4, raised at g2-implement).

### assertion:cleanup-f-derive-worktree-009.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Three copies of one claim were expected to be held together by something in the repo.

### assertion:cleanup-f-derive-worktree-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: No mechanical guard in the repo covers them. The drift check that keeps them honest lives under .agent-work/, is written fresh by whichever crew needs it, and was hand-updated twice on this lane -- catching real drift both times.

### assertion:cleanup-f-derive-worktree-009.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The rework-1 implementer raised it and was told a mechanical check was not required; the rework-2 implementer re-raised it with the second data point. A guard that lives in a crew's scratch directory dies with the crew that wrote it.

### assertion:cleanup-f-derive-worktree-009.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Each crew rewrote the drift check under .agent-work/ and ran it before closing its gate.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-009.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A check whose home is the run's own work area is scoped to the run, so its survival depends on a successor choosing to rewrite it rather than on anything the repo enforces.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
