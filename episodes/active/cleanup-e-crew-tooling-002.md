<!-- episode-state: schema=1 id=cleanup-e-crew-tooling-002 status=active -->

# episode: cleanup-e-crew-tooling-002

## Mechanical
- run: cleanup-e-crew-tooling
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-e-crew-tooling/MISSION_FRAME.md
- artifact-ref: .agent-work/cleanup-e-crew-tooling/execute.json

## Agent-supplied

### assertion:cleanup-e-crew-tooling-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Ran two parallel plan-alternative candidates (minimal-diff vs. defense-in-depth constraints) then one cold plan critic with no authoring context, per design-it-twice + critical-spec-review doctrine, before freezing execute.json.

### assertion:cleanup-e-crew-tooling-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Expected the cold critic to either confirm the converged plan or surface stylistic/minor gaps, given both independent candidates had already converged on the same #607/#525 mechanisms.

### assertion:cleanup-e-crew-tooling-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The cold critic found two real, load-bearing defects the converged plan shared with both candidates: (1) g2's scratch_dir key tuple dropped worktree even though the plan's own cited anchor (next_attempt/active_duplicate) keys duplicate-detection on the full 4-field tuple including worktree -- would have let two worktrees collide at the same attempt number, reintroducing #525 one field narrower; (2) g1's self-collision guard (skip heartbeating when child's spine equals parent's ambient spine) would have disabled the fix for the common no-explicit---spine dispatch, since crew_env() inherits the parent's ambient SPINE_FILE/SPINE_SESSION unchanged in that case by documented design. Both findings survived independent re-verification during implementation and review (two separate crews each independently traced next_attempt's real scoping and checklist_engine.heartbeat()'s real ownership check from source, not from the plan's restatement of them).

### assertion:cleanup-e-crew-tooling-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Both findings were fixed in execute.json before any implementer was dispatched, at zero rework cost to the crews -- both g1 and g2 implemented the corrected design on the first attempt, and both reviewers independently confirmed the corrected design (including running their own mutation tests: g2's reviewer temporarily stripped worktree from the key and confirmed 4 tests failed). Had either gap shipped, the eventual defect would have been the exact hazard #607/#525 were filed to close, discovered later and at higher cost.

### assertion:cleanup-e-crew-tooling-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none -- both findings were incorporated directly into execute.json's anchors before dispatch.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
