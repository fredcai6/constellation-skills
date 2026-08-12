<!-- episode-state: schema=1 id=epic-418-followon-005 status=active -->

# episode: epic-418-followon-005

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
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Check whether a Commander had honoured the standing instruction to dispatch its crews on Sonnet, by reading the model field on each crew's registry entry.

### assertion:epic-418-followon-005.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: An absent model field would mean the flag was never passed, since the field is present on entries that do carry it.

### assertion:epic-418-followon-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: run_crew.py's cli backend never passed model to build_entry, while the external backend did. Dispatching a real crew with an explicit --model sonnet showed the flag on run_crew.py's own command line and on the child claude -p command line, with the registry entry still recording no model at all.

### assertion:epic-418-followon-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A finding was built and logged across nine dispatches on a field that records nothing on the only path that spawns a process, and it was wrong. Every registry entry in this repo's history is silent about model tier for the same reason, so no run record could answer the question that was asked of it.

### assertion:epic-418-followon-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Verification ran against the process command line rather than the record, until the record was shown to carry the field. The record was then fixed and both paths pinned, because the asymmetry between them was the defect.
- history: restated — Restated as an observation. The original was written in the imperative and read as a rule for a future agent to follow; an episode records what happened, and a rule belongs in docs/agents/*. Caught by scripts/verify_episode_observations.py at the epic's closeout. — original statement was: Verify against the process command line, not the record, until the record is proven to carry the field; then fix the record and pin both paths, because the asymmetry between them is the bug.

## Diagnosis (optional)

### assertion:epic-418-followon-005.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A field that is absent for two different reasons -- never supplied, or supplied and dropped -- cannot distinguish them, and its presence on a sibling code path is exactly what makes the absence look like data.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
