<!-- episode-state: schema=1 id=tc6-doctrine-001 status=active -->

# episode: tc6-doctrine-001

## Mechanical
- run: tc6-doctrine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/tc6-doctrine/execute.json
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/tc6-doctrine/RUN_SUMMARY.md
- artifact-ref: docs/CHECKLIST_SCHEMA.md
- artifact-ref: skills/admiral/templates/LAUNCH_ORDER.template.md

## Agent-supplied

### assertion:tc6-doctrine-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Reconcile three doctrine surfaces (docs/CHECKLIST_SCHEMA.md, the Commander launch-order template, and skills/workbench/references/checklist-engine.md) against what the engine actually does at main 0646d61b, per launch order admiral-post-568, verifying every claim against the live code before writing rather than trusting the order's own paraphrase.

### assertion:tc6-doctrine-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The launch order named docs/CHECKLIST_SCHEMA.md's containment/Path.cwd() passage as actively stale after PR #588, asked for a defended judgment call on whether the launch-order template's first-step verify_worktree_isolation.py instruction was now redundant, and flagged skills/workbench/references/checklist-engine.md as a possibly-nonexistent third surface needing re-measurement rather than an assumed edit.

### assertion:tc6-doctrine-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: All three claims held on inspection. scripts/checklist_engine.py:102-179 and :3411-3444 shipped exactly the equality/git-toplevel/fail-closed shape the 2026-08-15 worktree-identity ruling described. skills/workbench/references/checklist-engine.md carried no isolation claim at all -- only a --worktree lease-claim CLI flag -- so the third surface was an honest null. A docs/+skills/ sweep (grep -rn -E 'is_relative_to|[Cc]ontainment|Path\.cwd\(\)|verify_worktree_isolation\.py' docs/ skills/ --include=*.md) returned 51 hits, none needing correction beyond the two passages already fixed. The full clean-env suite matched the launch order's stated worktree-checkout baseline exactly: 3028 passed, 6 skipped, 1136 subtests.

### assertion:tc6-doctrine-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Ran end to end through init, context, understand, plan, execute (four gates), reconcile, triage, and review, entirely in one context with no crew dispatch since every gate was a reasoning gate over prose. The full suite run alone took 123.83s of the total wall-clock.

### assertion:tc6-doctrine-001.a5
- kind: workaround
- strength: weak
- lifecycle-standing: active
- statement: None needed for the doctrine reconciliation itself; both judgment calls (Task 2's redundant-or-distinct question, Task 3's honest null) resolved from direct code inspection rather than requiring escalation.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
