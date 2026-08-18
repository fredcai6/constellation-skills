<!-- episode-state: schema=1 id=epic-567-door-025 status=active -->

# episode: epic-567-door-025

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 1
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-025.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A diagnosis, filed as an issue, that a launcher inherited the host's model default when the flag was unset.

### assertion:epic-567-door-025.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The lane dispatched to fix it would build against that diagnosis.

### assertion:epic-567-door-025.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The launcher refuses a dispatch with no model rather than inheriting one, and had done so since an earlier issue closed that exact failure mode. The escalation came instead from a Commander writing a tier into an unconstrained free-text field in its own handoff, with reasons. Two populations had been measured -- bare helper launches, which do inherit, and launcher dispatches, which refuse -- and written up as one story.

### assertion:epic-567-door-025.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A filed issue carried a false mechanism until the lane reading the code found it. The remedy was unaffected, but anyone building from the issue body would have built against a defect that did not exist.

### assertion:epic-567-door-025.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Corrected publicly on the issue as a comment rather than by a silent edit, so the wrong diagnosis stays visible beside the right one, and the lane restated it in its own return.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
