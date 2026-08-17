<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-016 status=active -->

# episode: cleanup-f-derive-worktree-016

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
- artifact-ref: .agent-work/archive/2026-08-17-cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-rework3-result.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-016.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run the full suite as a reviewer, from a crew working under .agent-work/ (tc11, raised at g2-review).

### assertion:cleanup-f-derive-worktree-016.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A green suite was expected to mean the change under review is green.

### assertion:cleanup-f-derive-worktree-016.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: tests/test_containment_repo_agent_work_untouched_by_the_chain snapshots the live .agent-work/ by size and mtime, so it fails for any agent running the suite while working under .agent-work/ -- which is where every crew's survey, plan, evidence and scratch lives.

### assertion:cleanup-f-derive-worktree-016.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: It cost the g2 rework-3 reviewer a full 128-second run and a false '1 failed' that looked exactly like a regression.

### assertion:cleanup-f-derive-worktree-016.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The reviewer measured on a quiet tree, the same remedy the documented CREW_SCRATCH_DIR caveat prescribes for its own class.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-016.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The test's subject is the same directory the agent running it works in, so the act of measuring changes what is measured. The test could exclude the current crew's work-id subtree and keep its guarantee.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
