<!-- episode-state: schema=1 id=w3-door-001 status=active -->

# episode: w3-door-001

## Mechanical
- run: w3-door
- project: constellation-skills
- role: commander
- spine-step: g1-integrate
- context-manifest-ref: none -- commander run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w3-door/RESULT.md

## Agent-supplied

### assertion:w3-door-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Verify the full suite is green at the shipped revision (LAUNCH_ORDER Return Shape #3) before closing g1-integrate's c1, per decision:dont-break-your-siblings and the requirement to re-run after the final commit rather than trust an uncommitted pass.

### assertion:w3-door-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: LAUNCH_ORDER's Return Shape describes map/INDEX.md freshness as mechanized by a pre-commit hook, framed as something a lane reports on rather than something it may have to finish by hand.

### assertion:w3-door-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: python3 -m pytest -q at the implementer/reviewer's shipped commit (e1180197) failed tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build -- tests/test_crew_launcher.py's tracked entity count had grown by 1 for the new resume()-path test, but map/INDEX.md was not regenerated. .git/hooks/pre-commit does not exist in this worktree. Both the implementer and reviewer had already flagged this exact staleness (tc1) as an expected, out-of-scope failure per the handoff's own Close Criteria, rather than a hook misfiring silently.

### assertion:w3-door-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: g1-integrate's c1 (full suite passes at the shipped revision) could not close without a second, separate commit; the run required an extra rebuild-and-commit step the Return Shape's phrasing did not anticipate as the Commander's own responsibility.

### assertion:w3-door-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Ran python3 -m scripts.code_map build --root . and committed the resulting 6-line map/INDEX.md diff separately (16d6f631) before re-running the full suite, which then passed at 3730 passed, 9 skipped, 1277 subtests passed.

## Diagnosis (optional)

### assertion:w3-door-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: No pre-commit hook is actually installed in this worktree (569-w3-door), so whatever mechanizes map/INDEX.md regeneration elsewhere in the corpus did not fire here between the implementer's commit and the Commander's suite run.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
