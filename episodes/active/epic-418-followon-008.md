<!-- episode-state: schema=1 id=epic-418-followon-008 status=active -->

# episode: epic-418-followon-008

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/CURRENT_TRUTH.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/transitions/w7x-lifecycle/REPLAN_INPUT.json

## Agent-supplied

### assertion:epic-418-followon-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Record at the wave-5 boundary which of the epic's five definition-of-done items now held, so the next wave could be planned against what was left.

### assertion:epic-418-followon-008.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A workstream's own report that it had removed every CLI mention from agent-facing instruction could be carried into the boundary record.

### assertion:epic-418-followon-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Remeasured a wave later: 15 CLI-fallback clauses across 11 shipped files and 8 live <engine> tokens across 4 orchestrator templates. The wave-5 cleanup had covered the crew-facing skills and left the orchestrator tier untouched, and its claim was never checked against the corpus.

### assertion:epic-418-followon-008.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A definition-of-done item was recorded as holding for a full wave while being false, and two of the surviving clauses assert that the CLI is the only path for an in-session dispatched crew -- a claim the same epic had already disproved by dispatching one.

### assertion:epic-418-followon-008.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Re-run the measurement at the boundary rather than carrying a crew's summary of it; the grep costs seconds and the claim rode for a wave.

## Diagnosis (optional)

### assertion:epic-418-followon-008.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A definition-of-done item is checked when it is first claimed and never again, so a partial fix that reports as complete is never contradicted.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
