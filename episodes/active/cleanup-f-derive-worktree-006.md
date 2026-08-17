<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-006 status=active -->

# episode: cleanup-f-derive-worktree-006

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

### assertion:cleanup-f-derive-worktree-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Orient through the code map before opening source, per the commander's own map-first imperative (tc1, raised at g1-review).

### assertion:cleanup-f-derive-worktree-006.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A repo whose map/INDEX.md is tracked and freshness-tested was expected to carry a usable map, and a full rebuild was expected to restore anything missing.

### assertion:cleanup-f-derive-worktree-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: map/ids.jsonl is 0 bytes and the per-module map/<module>/INDEX.md files are absent. A full `py -m scripts.code_map build --root .` does not create them: re-running left the tree byte-identical. The freshness test compares only the root index, so no check notices the absence.

### assertion:cleanup-f-derive-worktree-006.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: This is the mechanical cause of every Commander run in this repo orienting DEGRADED-UNPARSEABLE, and it does not self-heal across runs.

### assertion:cleanup-f-derive-worktree-006.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Each run declares the degraded reading with --substitute/--unmapped/--escalation and proceeds from repo doctrine instead of a map.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-006.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The freshness test's scope and the build's output scope disagree: the test pins the one file the build reliably produces, so the parts the build does not produce are outside anything that could report them missing.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
