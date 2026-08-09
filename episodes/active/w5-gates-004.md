<!-- episode-state: schema=1 id=w5-gates-004 status=active -->

# episode: w5-gates-004

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: triage
- context-manifest-ref: .agent-work/w5-gates/context/g4-review.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/TRIAGE_RECOMMENDATIONS.md

## Agent-supplied

### assertion:w5-gates-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Route 14 triage candidates and file the ones that warrant issues.

### assertion:w5-gates-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The latitude contract classes issue filing as delegated, so filing would be available.

### assertion:w5-gates-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Class-level delegation, but the TOOL gh issue create is listed pre-clear, annotated 'the gh issue create gap has now recurred four times'. This is the fifth. Delegation of a decision class with no cleared tool is not filing authority.

### assertion:w5-gates-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Nothing filed; 14 issue-ready recommendations handed up instead. The findings are preserved but they are not on the tracker, which is the outcome the human has previously objected to.

### assertion:w5-gates-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Routed all 14 as recommend-and-defer -- the triage skill's own recorded form of 'ask' -- with a suggested split, and floated the authority gap itself as worth a ruling rather than absorbing it a fifth time.

## Diagnosis (optional)

### assertion:w5-gates-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Decision-class authority and tool-level pre-clearance are recorded in separate tables and can disagree.

### assertion:w5-gates-004.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: Reconcile the two tables, or make the contract state which one wins when they conflict.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
