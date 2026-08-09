<!-- episode-state: schema=1 id=w5-gates-007 status=active -->

# episode: w5-gates-007

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/w5-gates/context/g3-implement.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/crew-handoffs/g3-implement-RESULT.md

## Agent-supplied

### assertion:w5-gates-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Invent a test mechanism for the archive-reachability check at gate g3.

### assertion:w5-gates-007.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The handoff would name what is on PATH, since the mechanism to be invented depends entirely on that answer.

### assertion:w5-gates-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It did not. `gh --jq` uses an embedded gojq and there is no standalone `jq` on this host; `bash` and `python` are present; `gh` is present but unusable offline. The g3 implementer and the g3 reviewer each determined this separately and both asked for the same single line in the handoff.

### assertion:w5-gates-007.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The most expensive part of the gate was fully determined by that answer, and two crews on the same gate paid to discover it independently.

### assertion:w5-gates-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each crew probed PATH itself before building the mechanism and recorded the finding in its RESULT.

## Diagnosis (optional)

### assertion:w5-gates-007.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Host capability is treated as ambient knowledge, so it is rediscovered per crew rather than stated once where the work is handed over.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
