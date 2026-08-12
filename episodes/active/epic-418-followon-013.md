<!-- episode-state: schema=1 id=epic-418-followon-013 status=active -->

# episode: epic-418-followon-013

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/transitions/w6x-generate-the-spine/REPLAN_RESULT.json

## Agent-supplied

### assertion:epic-418-followon-013.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Build a generator that compiles a typed spec into a spine, so an author never writes a check as a shell string from memory.

### assertion:epic-418-followon-013.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Typing the check kinds would remove the class of defect that hand-authored checks produce.

### assertion:epic-418-followon-013.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first generator could still author a check that cannot fail and one that cannot pass: numeric fields reached the compiled shell command unquoted and untyped, and the script probe could not see a check's required arguments. Both were found by driving the generator rather than by reading it.

### assertion:epic-418-followon-013.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The defect class the generator exists to close was reproducible inside the generator itself on its first pass, which is what justified the rework round rather than the merge.

### assertion:epic-418-followon-013.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Refuse a non-integer on every numeric field, and call the oracle as the literal last statement before writing so any fault or undecidable entry refuses with nothing written.

## Diagnosis (optional)

### assertion:epic-418-followon-013.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A closed vocabulary constrains the shape of a check and not the values inside it, so an untyped field in a typed format is the same footgun with a smaller surface.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
