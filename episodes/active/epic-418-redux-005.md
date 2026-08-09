<!-- episode-state: schema=1 id=epic-418-redux-005 status=active -->

# episode: epic-418-redux-005

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

### assertion:epic-418-redux-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Relaunch four crews that had each tripped on a HARD context reading at a gate boundary, filed a refresh-request, and stood down.

### assertion:epic-418-redux-005.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Each fresh agent would open with a low context reading of its own and proceed through the gate its predecessor could not start.

### assertion:epic-418-redux-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first relaunched agent reported a reading already over the hard line and asked whether it should proceed or hand off. The gauge file showed that value had been observed roughly nine minutes before that agent existed: the gauge is written per checklist directory, so a fresh agent reads its predecessor's value until its own first tool call lands.

### assertion:epic-418-redux-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The reading carries no owner and no staleness marker where the agent reads it, so an inherited value is indistinguishable from a self-measured one. The resulting failure is a loop -- relaunch, inherit, trip, hand off, relaunch -- in which every cycle looks like correct doctrine being followed. Four crews had been relaunched within a few minutes.

### assertion:epic-418-redux-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The three remaining relaunches were sent a correction before any of them read a gauge, stating that the value they would see belonged to their predecessor, that a tool call of their own would refresh it, and that a refresh-request filed against an inherited reading would restart the loop. None of the three subsequently tripped on an inherited value.
- history: restated — Restated to drop imperatives and second person: the original quoted the Admiral's instruction to the crews verbatim, so the record read as a prescription for a future agent rather than as an account of what was done. The strict observation guard flagged it, which is the defect #460 catalogued in this same store. — original statement was: The three remaining relaunches were sent a correction before any of them read a gauge: the number is the predecessor's, make any tool call and re-read, and do not file a refresh-request against a reading you did not produce.

## Diagnosis (optional)

### assertion:epic-418-redux-005.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A value with no provenance cannot be checked. There is no predicate over the number alone that separates an inherited reading from a self-measured one; the missing data is when it was taken and by whom, and it is missing at the point the value is written.

### assertion:epic-418-redux-005.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The loop was broken by an agent doubting a number it was handed rather than obeying it, which is also how two other defects in this run surfaced.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
