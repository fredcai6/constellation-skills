<!-- episode-state: schema=1 id=episode-guard-at-write-004 status=active -->

# episode: episode-guard-at-write-004

## Mechanical
- run: episode-guard-at-write
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: ctx-egaw-replan-input@54544404
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 1
- artifact-ref: .agent-work/episode-guard-at-write/REPLAN_INPUT.json

## Agent-supplied

### assertion:episode-guard-at-write-004.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Satisfy execute's c2 postcondition, a G2-schema REPLAN_INPUT.json verified by verify_iterative_role_artifacts.py, for a single-issue frozen launch order with no epic-level wave plan behind it.

### assertion:episode-guard-at-write-004.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: A lighter path might exist for a one-issue delegated run with no multi-issue wave to describe.

### assertion:episode-guard-at-write-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The full G2 schema (epic, definition_of_done, good_enough, hard_constraints, fixed_decisions, a typed current_wave with one issue, wave_forecast, uncertainty_register, parked_possibilities, completed_outcomes, wave_evidence, discrepancies, an open/unlaunched partition, repo_state) had to be authored in full, synthesizing epic-shaped fields that did not otherwise exist for a single-issue launch order, to pass verify_replan_input's strict allowed-field checks. The first attempt failed validation on one extra key ("issue") left in a wave_evidence entry; removing it passed.

### assertion:episode-guard-at-write-004.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: One schema-authoring pass and one validator round-trip.

### assertion:episode-guard-at-write-004.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: This run filled every required G2 field with real content drawn from LAUNCH_ORDER-2 and the actual test and commit evidence, rather than leaving template placeholder text, and dropped the one non-conforming key the validator named.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
