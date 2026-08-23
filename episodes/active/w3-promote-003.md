<!-- episode-state: schema=1 id=w3-promote-003 status=active -->

# episode: w3-promote-003

## Mechanical
- run: w3-promote
- project: constellation-skills
- role: commander
- spine-step: g7-implement
- context-manifest-ref: ctx-w3-promote-g7
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/scout/templates/SCOUT.template.json
- artifact-ref: skills/cartographer/templates/CARTOGRAPHER.template.json

## Agent-supplied

### assertion:w3-promote-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author the g7 handoff reversing decision:blocking-where-adjudicated's default to report-only, since both SCOUT.template.json and CARTOGRAPHER.template.json measured zero live check kinds before this gate -- the first report-only-biased handoff this wave, after four straight blocking-biased ones.

### assertion:w3-promote-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A default-reversal handoff, being a genuine departure from the pattern the crew had followed four times already, might need a round-trip question from the implementer or reviewer to confirm the reversal was intentional and not a handoff-authoring mistake.

### assertion:w3-promote-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Neither the implementer nor the reviewer needed a round-trip. The handoff's CRITICAL section pre-answered the hardest judgment call (report-only-by-default for a first-use file) precisely enough, including a concrete worked model (map_orient.py's own --report-only flag) and an explicit worked example of what a report-only command check must look like, that both crews executed and independently verified the reversal without escalating.

### assertion:w3-promote-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Zero round-trips, zero rework, APPROVE on first pass -- the gate closed in the same shape as every prior gate despite carrying a genuine default reversal.

### assertion:w3-promote-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none.

## Diagnosis (optional)

### assertion:w3-promote-003.d1
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: When a wave needs to flip a default mid-run, name the flip explicitly in its own CRITICAL/bolded section with a concrete worked model to copy, rather than relying on the crew to infer the reversal from the per-template measurement alone.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
