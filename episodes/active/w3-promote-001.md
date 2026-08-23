<!-- episode-state: schema=1 id=w3-promote-001 status=active -->

# episode: w3-promote-001

## Mechanical
- run: w3-promote
- project: constellation-skills
- role: commander
- spine-step: g4-implement
- context-manifest-ref: ctx-w3-promote-g4
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/explorer/templates/EXPLORER_SPINE.template.json

## Agent-supplied

### assertion:w3-promote-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Promote check:null conditions in EXPLORER_SPINE.template.json per the g4 handoff, honoring decision:no-basis-backfill (the basis field is reserved for the sibling w3-basis lane, a different population).

### assertion:w3-promote-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A handoff whose Constraints section explicitly names decision:no-basis-backfill would be sufficient for an implementer not to add a basis field.

### assertion:w3-promote-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The implementer's first pass added a basis object to two split conditions (context.c1, spec.c1), citing an out-of-wave precedent (COMMANDER_SPINE's own pre-existing plan.c2/c4/c5, authored before this wave's own pre-rulings existed). Caught and corrected by the Commander before review; the reviewer then independently re-derived the correction's soundness from the actual pre-ruling text (MISSION_FRAME.md's Out of Scope section) rather than trusting the Commander's read.

### assertion:w3-promote-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Caught same-gate, before review, at zero cost to schedule or rework_count. Would have shipped a decision-boundary violation to review if not caught.

### assertion:w3-promote-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Commander stripped the basis field before dispatching to review; g5's implementer was warned explicitly and did not repeat the mistake.

## Diagnosis (optional)

### assertion:w3-promote-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Naming a constraint in a handoff's Constraints list is necessary but was not sufficient here -- the implementer needed to actively check an out-of-wave precedent against this wave's own pre-rulings rather than pattern-match on file-family similarity to a plausible-looking sibling condition.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
