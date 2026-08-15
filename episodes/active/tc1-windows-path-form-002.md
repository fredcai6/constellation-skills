<!-- episode-state: schema=1 id=tc1-windows-path-form-002 status=active -->

# episode: tc1-windows-path-form-002

## Mechanical
- run: tc1-windows-path-form
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/tc1-windows-path-form/REPLAN_INPUT.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/tc1-windows-path-form/REPLAN_INPUT.json
- artifact-ref: skills/replan/scripts/verify_replan.py
- artifact-ref: scripts/verify_issue_set.py

## Agent-supplied

### assertion:tc1-windows-path-form-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Satisfy execute.json's directive that REPLAN_INPUT.json pass verify_iterative_role_artifacts.py commander before execute can complete.

### assertion:tc1-windows-path-form-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Expected a lightweight artifact scoped to this run's actual size: one gate, one line of code, one discrepancy.

### assertion:tc1-windows-path-form-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The G2 schema (verify_replan_input, which itself calls verify_manifest_shape) requires a full G1-shaped current_plan nested inside -- epic, definition_of_done, good_enough, hard_constraints, fixed_decisions, a current_wave of typed AFK/HITL issues with dependency-edge validation, wave_forecast, uncertainty_register, and parked_possibilities -- none of which pre-existed for this one-line, single-gate fix. Neither the bundled template nor the directive block named the required shape; it had to be reverse-engineered by reading verify_replan.py and verify_issue_set.py directly.

### assertion:tc1-windows-path-form-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Authoring a schema-valid REPLAN_INPUT.json took materially more turns than the underlying code change itself, and the resulting artifact is far larger than the diff it documents.

### assertion:tc1-windows-path-form-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The run read the verifier source (verify_replan.py and verify_issue_set.py), not just the bundled template, and that read is what exposed the exact required/optional field split -- neither the template nor the directive block had named it. Keeping the template's structural shape and substituting real run content produced a schema-valid REPLAN_INPUT.json, where an earlier attempt at guessing which template fields could be dropped had not.
- history: restated — restated from advice to a future reader into an observation of what this run did and found (tc1-episode-rewording, per LAUNCH_ORDER admiral-post-568) — original statement was: Read the verifier source (not just the template) to get the exact required/optional field split, then keep the template's structural shape and substitute real run content -- rather than guessing at which template fields could be dropped.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
