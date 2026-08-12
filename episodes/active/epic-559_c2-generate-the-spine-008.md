<!-- episode-state: schema=1 id=epic-559_c2-generate-the-spine-008 status=active -->

# episode: epic-559_c2-generate-the-spine-008

## Mechanical
- run: epic-559/c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g1-review-result.md
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-review-result.md

## Agent-supplied

### assertion:epic-559_c2-generate-the-spine-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch cold reviewers through run_crew.py with a handoff, so each reviews a gate independently.

### assertion:epic-559_c2-generate-the-spine-008.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A crew dispatched without `--spine` has no spine bound to it.

### assertion:epic-559_c2-generate-the-spine-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both reviewers found `SPINE_FILE` and `SPINE_SESSION` pointing at the Commander's own spine -- the `execute` gate, session `commander` -- inherited from the dispatching process's environment. Each recognized it was not a spine bound to them and built its own survey from REVIEW_SURVEY.template.json instead, and each reported the leak unprompted in its workflow feedback.

### assertion:epic-559_c2-generate-the-spine-008.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: No damage, because both crews' own doctrine told them not to drive a spine they were not given. The spine they would have driven is their dispatcher's.

### assertion:epic-559_c2-generate-the-spine-008.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Neither crew drove it; both reported it. The Commander recorded it as a triage candidate.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
