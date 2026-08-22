<!-- episode-state: schema=1 id=w1-wiring-004 status=active -->

# episode: w1-wiring-004

## Mechanical
- run: w1-wiring
- project: constellation-skills
- role: commander
- spine-step: g4-disposition
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1

## Agent-supplied

### assertion:w1-wiring-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run the full local pytest suite (3579+ tests, ~146s) as one foreground command that does not return until the suite's summary line lands, per the documented nohup+until-loop idiom, so the harness never auto-backgrounds it mid-run.

### assertion:w1-wiring-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: One Bash tool call running the nohup-launch-then-poll-loop together would complete inside that same call once the suite finished.

### assertion:w1-wiring-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The harness moved the call to the background anyway after its own ~120s default timeout, before the poll loop's condition could be observed to have been met inside that same call -- even though the idiom's whole point is that the loop itself is the one foreground command being waited on.

### assertion:w1-wiring-004.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: No work was lost -- the background task notification arrived with the correct completed output -- but the turn's own Bash call reported an unrelated cwd-reset side note that could be mistaken for a problem, and a second, separate polling Bash call was needed to actually observe the result.

### assertion:w1-wiring-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Treated the harness's auto-background as expected once the idiom's own single-call form was already tried and moved on: issued the poll loop again as its own Bash call (no new launch, same log file) and read the result from there, rather than re-launching the suite a second time.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
