<!-- episode-state: schema=1 id=w5-gates-005 status=active -->

# episode: w5-gates-005

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
- artifact-ref: references/windows.md

## Agent-supplied

### assertion:w5-gates-005.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Run the test suite as the shipped Windows reference instructs.

### assertion:w5-gates-005.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: references/windows.md section 4 would describe this host correctly.

### assertion:w5-gates-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It is wrong on this box: it prefers `py`, but `py` has no pytest here, so `py -m pytest` exits nonzero and reads EXACTLY like a red suite when nothing ran.

### assertion:w5-gates-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Cost three crews in this epic real time. A doc that produces a convincing false red is worse than a doc that is merely absent.

### assertion:w5-gates-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Every invocation on this run used `python`, and no test command was piped into tail or head, because the exit status then belongs to the pipe and a zero-match -k selector exits 5 while reading as 0. Output went to a file with the status echoed separately.
- history: restated — restated as an observation: the original opened with the bare imperatives 'Use' and 'Redirect' and instructed a future agent rather than recording what this run did. Original statement: Use `python` always, and never pipe a test command into tail or head -- the exit status then belongs to the pipe, and a zero-match -k selector exits 5 but reads as 0. Redirect to a file and echo the status separately. — original statement was: Use `python` always, and never pipe a test command into tail or head -- the exit status then belongs to the pipe, and a zero-match -k selector exits 5 but reads as 0. Redirect to a file and echo the status separately.

## Diagnosis (optional)

### assertion:w5-gates-005.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The reference generalizes across Windows hosts where the py launcher and the active interpreter differ.

### assertion:w5-gates-005.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: Have the doc tell the reader to verify which interpreter has pytest rather than naming one.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
