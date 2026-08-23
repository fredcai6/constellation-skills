<!-- episode-state: schema=1 id=w3-promote-006 status=active -->

# episode: w3-promote-006

## Mechanical
- run: w3-promote
- project: constellation-skills
- role: commander
- spine-step: g9-integrate
- context-manifest-ref: ctx-w3-promote-g9
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: map/INDEX.md

## Agent-supplied

### assertion:w3-promote-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run the full suite after the final commit per g9's own imperative, which assumed a pre-commit hook mechanizes map/INDEX.md freshness.

### assertion:w3-promote-006.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: map/INDEX.md would already be current at commit time, since g9's own gate imperative states "a pre-commit hook now mechanizes this."

### assertion:w3-promote-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: python3 -m pytest -q failed one test after the g9 gate-progression-closeout commit: MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build, entity count drifted 778->790 in tests.test_checklist_engine from this wave's own new red-proof test classes. Checked the actual git hooks directory (`git rev-parse --git-common-dir`/hooks/pre-commit): only a `.sample` file exists, no active hook is installed in this worktree. The staleness was caught by the pytest suite's own freshness assertion, not by any hook.

### assertion:w3-promote-006.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One extra rebuild-and-commit cycle (python3 -m scripts.code_map build --root ., then commit) before the suite could be confirmed green. No rework_count increment since this was within the same gate, before advance.

### assertion:w3-promote-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Ran the full suite explicitly after every commit rather than trusting the hook claim; would recommend a future Commander in this worktree do the same rather than assume the hook fires.

## Diagnosis (optional)

### assertion:w3-promote-006.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Either the hook was never installed in this specific worktree (worktrees do not automatically inherit hooks installed via a setup step run only in the primary checkout), or the gate imperative's claim was written aspirationally/for a different environment and never actually reconciled against this repo's real hook state.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
