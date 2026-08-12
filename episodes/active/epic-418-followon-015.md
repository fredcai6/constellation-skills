<!-- episode-state: schema=1 id=epic-418-followon-015 status=active -->

# episode: epic-418-followon-015

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-015.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive this epic's own closeout through the MCP door, which is the access path this epic exists to establish.

### assertion:epic-418-followon-015.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The Admiral's door was bound to this epic's spine, so spine_status and the lifecycle tools would act on .agent-work/epic-418-followon/spine.json.

### assertion:epic-418-followon-015.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The door was bound to a wave-1 scratch demo spine. spine_status returned another run's gates, and every lifecycle call would have acted on the wrong file, so the Admiral drove its own closeout through the engine CLI directly.

### assertion:epic-418-followon-015.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The exact defect this epic was convened to remove landed on the Admiral at its own closeout, and the run that measured the defect in ten dispatch scripts did not check its own binding until the last gate.

### assertion:epic-418-followon-015.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Called the engine directly against an explicit --file, and checked spine_status before trusting the door rather than assuming the dispatch had bound SPINE_FILE.

## Diagnosis (optional)

### assertion:epic-418-followon-015.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The Admiral was launched by a human at a terminal rather than by run_crew.py, so nothing in the launch path set SPINE_FILE; the door fell back to whatever spine it found first.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
