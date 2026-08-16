<!-- episode-state: schema=1 id=episode-guard-at-write-002 status=active -->

# episode: episode-guard-at-write-002

## Mechanical
- run: episode-guard-at-write
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: ctx-egaw-plan@2c46cab8
- refusals: 1
- reopens: 1
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/episode-guard-at-write/LAUNCH_ORDER-2.md
- artifact-ref: .agent-work/episode-guard-at-write/spine.json

## Agent-supplied

### assertion:episode-guard-at-write-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close plan.c6 (verify-frame) after MISSION_FRAME.md cited anchors that could not resolve against a map inventory.

### assertion:episode-guard-at-write-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine would refuse a commander's own attempt to waive its own bound spine check, per the doctrine that a crew must not waive its own bound check.

### assertion:episode-guard-at-write-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The prior attempt hit exactly that refusal on plan.c6, blocked, and escalated to the Admiral rather than self-waiving. The Admiral verified the empty-map claim directly against map/ids.jsonl (0 bytes, 0 lines) on main, corrected one supporting detail in the blocker text (map/INDEX.md was populated, not an unfilled template), and recorded a waiver as evidence e-plan-2. This run read that waiver, attached the required c3 user-decision evidence, and advanced plan without ever waiving c6 itself.

### assertion:episode-guard-at-write-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One full commander attempt spent its entire run reaching and reporting the blocker, with plan never advancing past it; a second attempt resumed from the recorded waiver rather than re-deriving the same evidence.

### assertion:episode-guard-at-write-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The commander escalated to the Admiral through the engine's block path instead of waiving its own bound check; the Admiral's independent verification and recorded waiver, not a self-granted exception, is what unblocked plan.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
