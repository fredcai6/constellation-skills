<!-- episode-state: schema=1 id=epic-567-door-008 status=active -->

# episode: epic-567-door-008

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

### assertion:epic-567-door-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: An Admiral epic lease, claimed through the door at session start, and a probe written to check whether it was still held.
- history: restated — retracted — there is no lease lapse. The lease lives in engine_session and a spine has no `lease` key at all; the probe read d.get('lease'), got None on every spine, and the Admiral reported that as a lapse to the human as one of five criticals. Measured after: epic-567-door engine_session.status active with a current heartbeat, held for the whole run. — original statement was: An Admiral epic lease, claimed through the door at session start and used continuously for four hours.

### assertion:epic-567-door-008.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The probe was expected to report the lease's state. It read a top-level `lease` key.
- history: restated — retracted — there is no lease lapse. The lease lives in engine_session and a spine has no `lease` key at all; the probe read d.get('lease'), got None on every spine, and the Admiral reported that as a lapse to the human as one of five criticals. Measured after: epic-567-door engine_session.status active with a current heartbeat, held for the whole run. — original statement was: The lease held until deliberately released at closeout.

### assertion:epic-567-door-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: There is no `lease` key on a spine; the lease lives in `engine_session`. The probe therefore returned None on every spine it was pointed at, and the Admiral read that as the lease having silently lapsed, reporting it with two spines as corroboration -- which was one broken read applied twice. Measured afterwards: epic-567-door carried engine_session.status active with a current heartbeat for the entire run, and 567-carto carried released, cleanly, at its close.
- history: restated — retracted — there is no lease lapse. The lease lives in engine_session and a spine has no `lease` key at all; the probe read d.get('lease'), got None on every spine, and the Admiral reported that as a lapse to the human as one of five criticals. Measured after: epic-567-door engine_session.status active with a current heartbeat, held for the whole run. — original statement was: During an unrelated hygiene survey the spine carried no active lease, and two directories that should not exist had appeared -- one nested inside the live epic work area -- both timestamped while lanes were running their archive gates. Re-claiming returned 'resumed lease ... heartbeat refreshed, claim re-stamped', so the identity was recognised rather than treated as new. Every mutating verb had continued to succeed throughout, because an unleased spine has no ownership guard.

### assertion:epic-567-door-008.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A false defect reached the human and a triage candidate was staged for it. The engine had already contradicted the reading: a re-claim answered 'resumed lease ... claim re-stamped', where resumed means a lease already held, and that message was cited as proof of the lapse it disproved. Two stray directories under the epic work area were attached to the hypothesis and now have no explanation.
- history: restated — retracted — there is no lease lapse. The lease lives in engine_session and a spine has no `lease` key at all; the probe read d.get('lease'), got None on every spine, and the Admiral reported that as a lapse to the human as one of five criticals. Measured after: epic-567-door engine_session.status active with a current heartbeat, held for the whole run. — original statement was: Nothing was lost, but the lapse was found by accident. A run that never looked would have reached the closeout provenance check with an unexplainable gap.

### assertion:epic-567-door-008.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The candidate was deleted, the log entry marked void, and the probe corrected to read engine_session and to distinguish an absent key from a released lease. The general shape, recorded because it recurred four times in one run: a real observation attached to a mechanism nobody checked.
- history: restated — retracted — there is no lease lapse. The lease lives in engine_session and a spine has no `lease` key at all; the probe read d.get('lease'), got None on every spine, and the Admiral reported that as a lapse to the human as one of five criticals. Measured after: epic-567-door engine_session.status active with a current heartbeat, held for the whole run. — original statement was: The lease was re-claimed through the door. The causal direction was not established and was recorded as a hypothesis rather than a finding.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
