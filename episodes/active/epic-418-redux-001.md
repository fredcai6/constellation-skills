<!-- episode-state: schema=1 id=epic-418-redux-001 status=active -->

# episode: epic-418-redux-001

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: origin-run:epic-418-redux
- artifact-ref: .agent-work/epic-418-redux/transitions/w4-to-close/REPLAN_RESULT.json
- artifact-ref: .agent-work/epic-418-redux/spine.json

## Agent-supplied

### assertion:epic-418-redux-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close the Admiral spine's execute gate after the epic's final wave merged, by satisfying postcondition c3, which runs verify_iterative_role_artifacts.py admiral-prelaunch against the wave boundary.

### assertion:epic-418-redux-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A boundary whose packet was G2-validated and whose transition was audit-recorded would satisfy the closure check, since those are the properties the check names.

### assertion:epic-418-redux-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The check additionally requires NEXT_WAVE.launch_id to be nonempty and the decision to be advance or replan. A boundary that exits stop -- the correct exit when a final wave completes -- cannot satisfy it. Three successive refusals were walked down: launch_id null, then an invalid trigger, then 'only advance or replan may authorize NEXT_WAVE', which cannot be fixed without changing the boundary's verdict.

### assertion:epic-418-redux-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The gate cannot be closed by a run that finishes. Its output is red in the world where the epic went well and red in the world where it went badly, so it discriminates nothing -- and because it is red rather than green, the two available exits were a waiver or changing the decision from stop to advance, which is falsifying a boundary verdict to satisfy a check.

### assertion:epic-418-redux-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Neither shortcut was taken. The gate was blocked with the engine's block verb and bubbled to the human, and the defect was filed as #506. When the human later authorized another wave, the boundary was re-derived as a NEW material_exception boundary exiting advance rather than by editing the already-exited stop verdict, and the gate then closed with nothing bent.

## Diagnosis (optional)

### assertion:epic-418-redux-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: admiral-prelaunch is a launch-authorization check being used as a gate-closure check, and those answer different questions. The artifact cannot even express a stop: NEXT_WAVE.launch_id has no legal value meaning 'no launch authorized'.

### assertion:epic-418-redux-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The stop path was never exercised by a test, only the advance path, which is consistent with the defect surviving until an epic actually tried to finish.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
