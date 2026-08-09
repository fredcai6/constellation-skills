<!-- episode-state: schema=1 id=w5-gates-006 status=active -->

# episode: w5-gates-006

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/w5-gates/context/g3-review.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/crew-handoffs/g2-review-RESULT.md

## Agent-supplied

### assertion:w5-gates-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive the checklist engine's verbs as a crew member following the engine reference.

### assertion:w5-gates-006.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: `--session-id` could be passed where the reference lists it, ahead of the verb.

### assertion:w5-gates-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The flag is parsed per-verb, so only `<verb> --session-id ...` is accepted; placing it first fails with `invalid choice`. Three crews hit this independently -- g1-review, g2-review and g3-review. In g3-review the first `start` failed with a REFUSED that reads like a lease conflict rather than a missing argument.

### assertion:w5-gates-006.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One wasted round trip per crew across three crews, plus one refused batch at g2-review. The refusal text points at the lease rather than at argument order, so the reader is sent to the wrong diagnosis.

### assertion:w5-gates-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each crew re-issued the call with the flag after the verb. On this segment I read `claim --help` before claiming rather than trusting the reference's ordering.

## Diagnosis (optional)

### assertion:w5-gates-006.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The reference documents the flag in a per-verb flag list, which does not convey positional requirement, and the refusal message names the lease rather than the parse failure.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
