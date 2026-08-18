<!-- episode-state: schema=1 id=epic-567-door-018 status=active -->

# episode: epic-567-door-018

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

### assertion:epic-567-door-018.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A suite run by each dispatched crew as its merge gate.

### assertion:epic-567-door-018.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The same result the Admiral's own gate produces.

### assertion:epic-567-door-018.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A crew's own CREW_SCRATCH_DIR leaks into a test that asserts about a constructed environment while building it from os.environ, so ScratchDirResumeTests fails for exactly the population the launcher creates. Four independent confirmations across three lanes and the Admiral, including one lane proving it fires identically on the untouched base commit with zero code changes.

### assertion:epic-567-door-018.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One lane lost a suite run to it. The dangerous outcome was avoided: a crew could have 'fixed' run_crew.py to satisfy a test that was never measuring its change.

### assertion:epic-567-door-018.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Lanes unset the four crew variables for their gate runs. The Admiral's own gate is immune because it runs from a shell carrying none of them, which is why a lane-reported tally is not accepted in place of the Admiral's own.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
