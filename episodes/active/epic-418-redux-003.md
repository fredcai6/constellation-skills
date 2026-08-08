<!-- episode-state: schema=1 id=epic-418-redux-003 status=active -->

# episode: epic-418-redux-003

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: origin-run:epic-418-redux
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-redux-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Sync the installed constellation skill bundles before dispatching a wave, so crews drive their spines on the engine that main actually carries.

### assertion:epic-418-redux-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Most bundles would already be current, since the previous wave had merged hours earlier and one bundle had matched main before that merge.

### assertion:epic-418-redux-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: All nine installed bundles carried a pre-merge engine. None had the fix that had just been merged. Crews would have driven spines on an engine where a HARD context reading still refuses the advance verb -- the exact defect the previous wave existed to remove.

### assertion:epic-418-redux-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Nothing in the dispatch path reports the drift. The staleness was found only because the drift was measured deliberately, and a run that skipped that measurement would have looked identical up to the moment a crew tripped.

### assertion:epic-418-redux-003.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Drift was measured per bundle with git hash-object against main's blob rather than read from the installer's own report, the install was re-run, and the 9-in-sync result was re-derived the same way afterwards.

## Diagnosis (optional)

### assertion:epic-418-redux-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: No provenance record names the engine build that executed a gate, so a spine driven by a stale engine leaves the same journal as one driven by a current engine. That gap is filed separately as #502.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
