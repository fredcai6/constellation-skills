<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-008 status=active -->

# episode: cleanup-f-derive-worktree-008

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

### assertion:cleanup-f-derive-worktree-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author gate checks that go red on an empty diff, as a cold critic asked for (tc3, raised at g1-review).

### assertion:cleanup-f-derive-worktree-008.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: scripts/validate_spine.py's falsifiable-zero-collected rule was expected to describe pytest's real behaviour when a -k selector collects nothing.

### assertion:cleanup-f-derive-worktree-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The rule reports a `pytest -k` check that collects zero tests as one that 'can never fail'. Measured at e36e630b: pytest exits 5 on no-tests-collected and 4 on a missing file, so such a check does fail.

### assertion:cleanup-f-derive-worktree-008.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The rule discourages exactly the red-on-an-empty-diff gate checks the review process asks for. This lane used one anyway -- the g3 selector exits 5 on the pre-gate arm and collects 23 passed after -- which is how the inversion was measured.

### assertion:cleanup-f-derive-worktree-008.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The lane measured pytest's exit codes directly rather than accepting the validator's characterization.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
