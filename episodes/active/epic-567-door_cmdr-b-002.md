<!-- episode-state: schema=1 id=epic-567-door_cmdr-b-002 status=active -->

# episode: epic-567-door_cmdr-b-002

## Mechanical
- run: epic-567-door/cmdr-b
- project: constellation-skills
- role: implementer
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-b/crew-handoffs/g1-implement-IMPLEMENTER_HANDOFF.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: scripts/run_crew.py

## Agent-supplied

### assertion:epic-567-door_cmdr-b-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Remove ExternalBackend.dispatch()'s old refusal of --spine so a caller could supply it for verification purposes, per the handoff's change 1.

### assertion:epic-567-door_cmdr-b-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Removing the refusal block would be a clean, isolated deletion with no other code path affected.

### assertion:epic-567-door_cmdr-b-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Removing the refusal exposed a latent crash: _require_handoff(spec.handoff, ...) calls Path(handoff) with no None-guard, previously unreachable with handoff=None because the old --spine refusal always fired first whenever spine was given alongside handoff=None. The full suite would have failed test_external_backend_refuses_spine_only_with_no_handoff (a crash, not the expected refusal message) had this gone unnoticed.

### assertion:epic-567-door_cmdr-b-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Caught by the implementer itself during its own TDD pass (test-first per the handoff's Test Mode), before returning IMPLEMENTER_RESULT -- fixed in the same gate with a two-line explicit handoff-is-None guard, at the cost of one extra self-check cycle; not caught by the handoff's own three-change list, which did not anticipate this specific interaction.

### assertion:epic-567-door_cmdr-b-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Added 'if spec.handoff is None: raise CrewLaunchError(...)' in ExternalBackend.dispatch() before the _require_handoff call, restoring the original test's passing scenario and message contract unchanged; documented explicitly in IMPLEMENTER_RESULT's Out-of-scope observations rather than silently folding it into the main diff.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
