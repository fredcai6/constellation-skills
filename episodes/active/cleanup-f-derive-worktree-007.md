<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-007 status=active -->

# episode: cleanup-f-derive-worktree-007

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

### assertion:cleanup-f-derive-worktree-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Follow the launch order's cited precedent for an inlined lexical path-normalize idiom (tc2, raised at g1-review).

### assertion:cleanup-f-derive-worktree-007.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A precedent cited by file and line in the launch order and MISSION_FRAME was expected to demonstrate the idiom it was cited for.

### assertion:cleanup-f-derive-worktree-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: scripts/agent_work_root.py:56 is `os.path.normcase(os.path.realpath(path))` -- it uses the exact call the lane's measured constraint forbids. agent_work_root.py normalizes with realpath while spine_rail._same_path normalizes lexically, and nothing in the repo records which is intended where.

### assertion:cleanup-f-derive-worktree-007.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The frame was corrected during this run before any code followed the wrong precedent, so the cost was one correction rather than a rework.

### assertion:cleanup-f-derive-worktree-007.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The lane read the cited line before copying its idiom, which is what surfaced the contradiction.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-007.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Two normalize strategies coexist with no recorded rule for which applies where, so any citation between them can be wrong without anything contradicting it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
