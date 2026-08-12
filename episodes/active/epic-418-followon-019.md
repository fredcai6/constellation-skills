<!-- episode-state: schema=1 id=epic-418-followon-019 status=active -->

# episode: epic-418-followon-019

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

### assertion:epic-418-followon-019.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Find out why the Admiral's own engine lease showed as released while a dispatched crew was still working, since a released lease reads as an abandoned run.

### assertion:epic-418-followon-019.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A crew dispatched with its own --spine gets its own lease, and the dispatcher's lease is untouched by anything the crew does.

### assertion:epic-418-followon-019.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: _crew_door_env in scripts/run_crew.py leaves SPINE_FILE and SPINE_SESSION untouched when spine is None, which is documented and deliberate. The crew inherited the dispatcher's binding and released the dispatcher's lease when it finished its own run.

### assertion:epic-418-followon-019.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The Admiral's lease showed released mid-epic, which reads as an abandoned run to anything checking it. _active_lease in scripts/checklist_engine.py documents that a released lease does not gate mutation, so the cost was a lost concurrency guard rather than a refused write.

### assertion:epic-418-followon-019.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Read the source rather than inferring from the symptom, confirmed against the _active_lease docstring that no write had been blocked, and re-claimed with the same session id, which is idempotent.

## Diagnosis (optional)

### assertion:epic-418-followon-019.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Inheriting the parent's environment is the right default for most variables and the wrong one for a lease binding, and one code path carried both.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
