<!-- episode-state: schema=1 id=epic-567-door-010 status=active -->

# episode: epic-567-door-010

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-010.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A progress report on the epic's headline lane, to inform a human decision about whether to stop and relaunch it.

### assertion:epic-567-door-010.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: An accurate statement of how much work remained.

### assertion:epic-567-door-010.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The lane was reported as 'at gate 4 of 17'. That was the spine's step count; inside its execute step, 13 of 17 plan gates were complete. The two numbers describe the same run and imply opposite decisions. The human chose to stop and relaunch on the wrong one.

### assertion:epic-567-door-010.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The error was caught while capturing state to execute that choice, before anything was touched, and the corrected numbers were put back to the human, who then chose to let the lane finish. It finished within minutes.

### assertion:epic-567-door-010.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The correction was made before acting rather than after. A progress number reported at the wrong altitude says the opposite of the truth.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
