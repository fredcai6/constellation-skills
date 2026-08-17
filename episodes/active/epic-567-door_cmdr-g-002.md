<!-- episode-state: schema=1 id=epic-567-door_cmdr-g-002 status=active -->

# episode: epic-567-door_cmdr-g-002

## Mechanical
- run: epic-567-door/cmdr-g
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/epic-567-door/cmdr-g/context/feedback.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: PLAN_CRITIQUE.md
- artifact-ref: PLAN_CRITIC.md
- artifact-ref: .agent-work/epic-567-door/cmdr-g/execute.json

## Agent-supplied

### assertion:epic-567-door_cmdr-g-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Ran design-it-twice (2 candidates) and dispatched a cold plan critic with no authoring context, reading only the mission frame and candidate plans plus real source, before authoring execute.json's gate imperatives.

### assertion:epic-567-door_cmdr-g-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The critic would surface stylistic or minor gaps in an otherwise sound converged design.

### assertion:epic-567-door_cmdr-g-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The dispatched critic (and, independently, a second critique authored by the design-it-twice fork under the same name PLAN_CRITIC.md) both found the same three Serious/BLOCKING defects: a pre-close verify predicate that would refuse on every legitimate call because it duplicated a lease check that could not yet pass, a reap-before-child-release ordering that would leave the exact staleness class the mission exists to fix, and a mission-order phrase ('release as the last journaled action') that does not match how the base engine's journal actually works. A third independent source -- the g1 implementer itself, reading the same code -- rediscovered the first defect a third time before any correction reached it.

### assertion:epic-567-door_cmdr-g-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: All three findings were corrected in execute.json and the crew handoffs before real implementation code was written against the corrected version, at the cost of one extra pass over the plan artifacts.

### assertion:epic-567-door_cmdr-g-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Independently re-verified every Serious finding against source (line numbers, function bodies) before accepting it, rather than trusting either critique's prose; folded the corrected design into execute.json and every downstream crew handoff.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
