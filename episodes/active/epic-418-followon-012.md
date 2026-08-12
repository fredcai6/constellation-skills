<!-- episode-state: schema=1 id=epic-418-followon-012 status=active -->

# episode: epic-418-followon-012

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/launch-orders/LAUNCH_ORDER-C3-lifecycle.md

## Agent-supplied

### assertion:epic-418-followon-012.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Instruct a Commander in its launch order to pass --parent naming itself and --model naming Sonnet on every crew it dispatches.

### assertion:epic-418-followon-012.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A Commander given both instructions in a frozen launch order would put both flags on the command line.

### assertion:epic-418-followon-012.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Six sub-crews were dispatched naming the Admiral as parent rather than the dispatching Commander, and none carried an explicit model. The Sonnet instruction appeared once in the launch order as a graded human ruling and nine more times in the Commander's own frozen execute.json, and still never became a flag.

### assertion:epic-418-followon-012.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A sub-crew that blocked would have asked up two rungs, past the only tier that had briefed it, to an Admiral without its handoff in context -- against a standing human ruling that crews fail up one rung at a time.

### assertion:epic-418-followon-012.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The spec declares the crews a gate dispatches and the generator emits the dispatch with parent and model already in it, so removing them requires editing a committed file and shows up in a diff.

## Diagnosis (optional)

### assertion:epic-418-followon-012.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Restating an instruction does not make it more likely to be followed: it was present ten times before the dispatch that dropped it. Prose cannot enforce itself, which is the epic's own thesis landing one tier up from where it was aimed.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
