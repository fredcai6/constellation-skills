<!-- episode-state: schema=1 id=epic-418-redux-010 status=active -->

# episode: epic-418-redux-010

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: .agent-work/epic-418-redux/spine.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-redux/STATE_NOTE.md

## Agent-supplied

### assertion:epic-418-redux-010.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Begin the closeout gate after wave 5 merged, main was green at c9f894f4, and the w5-to-close boundary exited stop with the prelaunch verifier at exit 0.

### assertion:epic-418-redux-010.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: With every precondition satisfied and no work outstanding at execute, `start closeout` should open the gate.

### assertion:epic-418-redux-010.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine refused: context at 29% is at or over the hard limit. The refusal was recorded on the trip ledger as `start closeout -> begin-refused`, a refresh-request was attached to the gate, and the gate was left blocked with a written handoff rather than waived. The block persisted across a further reading at 18%. It cleared only when the session's context was compacted: the gauge measured 0.075289 against a hard band of 150000/1000000, `resume closeout` was accepted, and the gate opened and ran normally with no waiver and no override.

### assertion:epic-418-redux-010.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The epic's own thesis is that a check must be able to fail. An Admiral that overrode its own governor to finish would have falsified the instrument the epic exists to defend, so the run stopped with five of six closeout postconditions unmet and no way to progress from inside that session. The cost was a stall of the whole closeout until an out-of-band context refresh arrived; the alternative -- a waiver -- would have asserted the closeout work was fine to skip, which it was not.

### assertion:epic-418-redux-010.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The blocker was recorded in the spine with its authority-needed and next-action fields naming a fresh Admiral, claim --force, and the STATE_NOTE handoff. The handoff named all five unstarted substeps, the six shape refusals the boundary builder had cost, and the epic418-w5-gauge omission from SWEEP_LIST.md. After the compaction the same session re-read the gauge, reclaimed the stale lease with --force, and resumed the gate against that record rather than from memory.

## Diagnosis (optional)

### assertion:epic-418-redux-010.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The engine's trip guidance at a tripped gate offers `advance <gate> --why` to carry a handoff and stop. At closeout that verb is also the verb that marks the spine done, and closeout is terminal with five unmet postconditions -- so the generic handoff instruction and the gate's actual state point in opposite directions. It was not executed, so whether the postcondition check would have refused it is untested.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
