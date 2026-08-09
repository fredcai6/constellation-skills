<!-- episode-state: schema=1 id=w5-gates-009 status=active -->

# episode: w5-gates-009

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

### assertion:w5-gates-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Respond to a context trip that fired after every measurement for the gate was already complete.

### assertion:w5-gates-009.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The reach-up doctrine and the crew doctrine would agree on what to do when a trip lands late in a run.

### assertion:w5-gates-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: They collide. Reach-up doctrine says to file a refresh-request and go idle; crew doctrine says the result file IS the task and that an idle turn-end with it unwritten strands the gate with no error signal. The same collision then recurred one level up: my predecessor tripped at `feedback` after it had already written and applied all five episodes, so the successor brief described the whole step as outstanding when only the reflection remained.

### assertion:w5-gates-009.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: At g3 a complete set of measurements would have been discarded had the doctrine been followed literally. At the spine level the episode capture was already green while being re-briefed as work to do, and one relaunch was spent establishing that.

### assertion:w5-gates-009.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The g3 implementer filed the refresh-request without starting the gate and wrote its result anyway, flagging the collision rather than claiming a clean reading. On this segment I ran the capture gate first, found it already passing, and wrote only the reflection.

## Diagnosis (optional)

### assertion:w5-gates-009.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A trip is handled as though it always arrives before the step's work, so neither doctrine describes the state where the work is done but unrecorded.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
