<!-- episode-state: schema=1 id=w5-gates-001 status=active -->

# episode: w5-gates-001

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/w5-gates/context/g4-review.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/gauge.json

## Agent-supplied

### assertion:w5-gates-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Pick up an in-flight run at g4-review as a fresh Commander and read my own context headroom before deciding whether to work or hand off.

### assertion:w5-gates-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The context gauge reported on my first `current` call would describe MY context.

### assertion:w5-gates-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: My first reading was 18 percent (at/over hard) with a TRIP HISTORY of 3, carrying my predecessor's number: gauge.json is written per checklist DIRECTORY, not per agent. After one tool call it read 0.034439 and the trip line vanished.

### assertion:w5-gates-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Four crews in this wave were relaunched into the loop -- read inherited number, trip, hand off, relaunch -- and each cycle was indistinguishable from correct doctrine. I avoided it only because my launch brief carried a hand-written warning.

### assertion:w5-gates-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Make any tool call, then re-read before believing any gauge number. Filed as issue 477 and under repair in a parallel worktree.

## Diagnosis (optional)

### assertion:w5-gates-001.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The gauge is keyed to the checklist directory, so identity is inherited rather than established per observing agent.

### assertion:w5-gates-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: Key the reading to the observing agent, or refuse to report a reading whose observer identity does not match the caller.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
