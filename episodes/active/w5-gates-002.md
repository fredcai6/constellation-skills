<!-- episode-state: schema=1 id=w5-gates-002 status=active -->

# episode: w5-gates-002

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/w5-gates/context/g4-review.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/crew-handoffs/g4-implement-RESULT.md

## Agent-supplied

### assertion:w5-gates-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close g4-implement when its implementer tripped hard before writing its own result file.

### assertion:w5-gates-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A transcribed result would carry the implementer's measurements intact.

### assertion:w5-gates-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The implementer correctly REFUSED to attest what it had not run, which is the doctrine working. The Commander transcribed instead, and one claim changed meaning in transit: 'only the doctrine test file differs from aa2038d9 outside .agent-work/' is true against the g4 baseline 84d1e998 but false against the fork point, where THREE production paths differ.

### assertion:w5-gates-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Caught by the g4 reviewer and corrected before the PR; the +24 conclusion was unaffected. Cost one review float and one Commander re-derivation.

### assertion:w5-gates-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The reviewer was told explicitly it was the first independent eyes on those numbers and treated every measurement as a claim. I re-derived with git diff --numstat rather than reasoning about which baseline was meant.

## Diagnosis (optional)

### assertion:w5-gates-002.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A measurement's baseline is implicit in prose, so across a handoff the frame of reference can swap silently while the sentence stays grammatical.

### assertion:w5-gates-002.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: Transcribed measurements name their baseline ref inline, so a reader can re-run rather than infer it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
