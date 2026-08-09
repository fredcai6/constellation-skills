<!-- episode-state: schema=1 id=issue-458-readiness-004 status=active -->

# episode: issue-458-readiness-004

## Mechanical
- run: issue-458-readiness
- project: constellation-skills
- role: implementer
- spine-step: execute
- context-manifest-ref: .agent-work/issue-458-readiness/context/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/issue-458-readiness/crew-handoffs/g1-implement-result.json

## Agent-supplied

### assertion:issue-458-readiness-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive g1-implement's own TDD plan gate-by-gate, observing red before green on each of the four readiness checks and the CLI layer.

### assertion:issue-458-readiness-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The plan's postcondition text for the CLI-mode gate expected the first test run to fail because the function under test did not exist yet (an AttributeError).

### assertion:issue-458-readiness-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The implementer wrote the CLI mode's implementation and its tests together rather than strictly test-first; the first real test run instead caught a genuine pre-existing defect -- resolve_target_roots rejects --project at --scope user, which collided with readiness's own orthogonal use of --project for the work-area item -- rather than the by-design AttributeError the plan text anticipated.

### assertion:issue-458-readiness-004.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: The net TDD value held (a real defect caught before green), but the letter of the plan's expected-failure text did not match what actually failed; recorded honestly in the engine's attest note rather than silently reconciled to match the plan's wording.

### assertion:issue-458-readiness-004.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Fixed resolve_target_roots to strip --project from target-root resolution only when scope == 'user', then continued the TDD cycle normally.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
