<!-- episode-state: schema=1 id=egaw-red-without-git-001 status=active -->

# episode: egaw-red-without-git-001

## Mechanical
- run: egaw-red-without-git
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/egaw-red-without-git/execute.json
- refusals: 2
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/egaw-red-without-git/crew-handoffs/g1-implement-implementer-result.md
- artifact-ref: .agent-work/egaw-red-without-git/crew-handoffs/g1-review-reviewer-result.md

## Agent-supplied

### assertion:egaw-red-without-git-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Removed the RED test's git dependency (a hardcoded-SHA git show) per LAUNCH_ORDER.md, while preserving the property it exists to prove: that the write-time guard PR #592 added is what causes the rejection, not merely present.

### assertion:egaw-red-without-git-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Neutralizing the guard seam (_reject_instruction_shaped) to a no-op on the current writer, then restoring it, would let the same delta and the same writer entry point demonstrate attribution without touching git.

### assertion:egaw-red-without-git-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The rewrite matched the launch order's approach (a) exactly. An independent reviewer traced the guard function to its three real call sites in the writer and confirmed the monkeypatch genuinely intercepted them rather than passing vacuously. The full suite matched the pre-change baseline exactly: 3040 passed, 6 skipped, 1146 subtests, 0 failed.

### assertion:egaw-red-without-git-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One implementer dispatch and one reviewer dispatch, each single-pass with no rework; two full clean-env suite runs at roughly two minutes each.

### assertion:egaw-red-without-git-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
