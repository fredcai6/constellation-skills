<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-015 status=active -->

# episode: cleanup-f-derive-worktree-015

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
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/ADMIRAL_RULING-3.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-015.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Find every prose site falsified by g2, across the whole repo rather than the files the order named (tc10, raised at g2-review).

### assertion:cleanup-f-derive-worktree-015.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Two claim families were expected to be the whole of the falsified prose.

### assertion:cleanup-f-derive-worktree-015.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A third family is live in two unfenced files: prose asserting the engine still reads its ambient cwd and still enforces the origin.worktree comparison. tests/test_explorer_templates.py cites the 2026-08-15 worktree-identity ruling as live authority; tests/test_mcp_door_engine_cwd.py opens by describing the comparison as current. The g2 rework-3 reviewer measured these false rather than inferring it: driving a spine whose origin.worktree is /totally/elsewhere from a foreign cwd, both `claim` and `start` return rc=0.

### assertion:cleanup-f-derive-worktree-015.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Two test files documented behaviour the same lane had removed three commits earlier, and one of them cited a superseded ruling as live authority.

### assertion:cleanup-f-derive-worktree-015.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: ADMIRAL_RULING-3 kept the repair in this lane's reconcile on the rule that the change which falsifies a claim owns the repair, and reconcile then found six sites where the order had named three.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-015.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Scoping a prose repair by file list bounds the search by where someone already looked. The claim family is the real unit, and grepping it rather than the file list is what found the other three.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
