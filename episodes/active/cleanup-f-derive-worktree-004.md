<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-004 status=active -->

# episode: cleanup-f-derive-worktree-004

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: reconcile
- context-manifest-ref: .agent-work/cleanup-f-derive-worktree/spine.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-f-derive-worktree/TRIAGE_RECOMMENDATIONS.md
- artifact-ref: .agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-3.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Repair the stale prose this lane's own changes falsified: three repairs in four files, named by the launch order and by ADMIRAL_RULING-3.

### assertion:cleanup-f-derive-worktree-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The named files were expected to be the whole set, since two independent readers -- the Admiral and a reviewer -- had each gone looking for the stale claims and had produced that list.

### assertion:cleanup-f-derive-worktree-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Grepping the CLAIM rather than opening the named files found six sites of one family across five files. Three were not on any list: `scripts/init_work_area.py`'s instantiate_spine docstring, `tests/test_worktree_derivation.py`'s symlink docstring, and the copy in `tests/test_spine_rail.py` that was only findable by a fragment because the claim wrapped across two comment lines.

### assertion:cleanup-f-derive-worktree-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Cheap here -- three extra prose edits in one gate -- but the same defect cost the earlier g2 gate three implementer passes, because every check anyone wrote keyed on a symbol while the defect lived in a claim wrapped across comment lines.

### assertion:cleanup-f-derive-worktree-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The sweep was scoped by the claim rather than by the file list: a grep for a fragment short enough to survive line wrapping found all six sites, three of which no list had named, and all six were repaired in one gate.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
