<!-- episode-state: schema=1 id=b433-render-directives-003 status=active -->

# episode: b433-render-directives-003

## Mechanical
- run: b433-render-directives
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/b433-render-directives/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/b433-render-directives/evidence/g3-schema-doc-correction.txt

## Agent-supplied

### assertion:b433-render-directives-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Correct docs/CHECKLIST_SCHEMA.md so the schema record matches the shipped behaviour, verified by postconditions frozen at plan time.

### assertion:b433-render-directives-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A postcondition asserting the old false claim is gone would be enough to prove the record was corrected.

### assertion:b433-render-directives-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A cold critic showed the bare negation passes on any rewording and also passes if the whole section is deleted, giving identical output in the healthy and the defective world, so the gate was re-authored as a conjunction pairing the negation with a positive assertion, and a second check was narrowed from a whole-file grep to the table row itself.

### assertion:b433-render-directives-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Caught before execution rather than after, so the cost was one planning revision instead of a doc gate that would have reported green against a deleted section.

### assertion:b433-render-directives-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The gate was re-authored so that its negation postcondition was paired with a positive one, and a second check was narrowed from a whole-file grep to the specific table row that had to change, so that a word added anywhere else could not satisfy it.
- history: restated — issue #460 gate g5 -- restated from imperative instruction to observation, grounded in a3, which records this exact re-authoring as done in this run, and a4, which records it as caught before execution at a cost of one planning revision — original statement was: Pair every negation postcondition with a positive one, and scope a grep to the specific line that must change rather than to the file, so a word added anywhere else cannot satisfy it.

## Diagnosis (optional)

### assertion:b433-render-directives-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A postcondition phrased only as the absence of a bad string is satisfied by deleting the content entirely, which is not the outcome intended.

### assertion:b433-render-directives-003.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The remedy this run applied was to state the doc postcondition as what the document now had to say rather than only as what it no longer had to say; d1 records why the negation-only form is satisfiable by deletion, and a3 records the re-authoring that carried this out.
- history: restated — issue #460 gate g5 -- restated from imperative instruction to observation, grounded in a3 (the gate was re-authored as a conjunction pairing the negation with a positive assertion) and d1 (a postcondition phrased only as the absence of a bad string is satisfied by deleting the content entirely) — original statement was: State doc postconditions as what the document must now say, not only as what it must no longer say.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
