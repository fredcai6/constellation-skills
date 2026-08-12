<!-- episode-state: schema=1 id=epic-418-followon_commander-f2-002 status=active -->

# episode: epic-418-followon_commander-f2-002

## Mechanical
- run: epic-418-followon/commander-f2
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: ctx-epic-418-followon/commander-f2-feedback@working-tree
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/commander-f2/IDENTITY_TRADE.md
- artifact-ref: .agent-work/epic-418-followon/commander-f2/evidence/g4b/MEASUREMENT.md
- artifact-ref: .agent-work/epic-418-followon/commander-f2/PLAN_CRITIC.md

## Agent-supplied

### assertion:epic-418-followon_commander-f2-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Make agents drive the checklist engine through the MCP door by default, and make the door record the rejections it answers itself, for issues #542 and #541.

### assertion:epic-418-followon_commander-f2-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Editing role spine instructions to name the door was expected to be sufficient for a dispatched agent to use it.

### assertion:epic-418-followon_commander-f2-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Two dispatched implementer agents drove the spine entirely through the CLI while the door was connected and all seven of its tools were offered; a third agent, driving a role that owns its process's bound spine, used the door for all nine engine invocations and the CLI for none.

### assertion:epic-418-followon_commander-f2-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Four review passes were spent on one gate's pin, each reviewer defeating the previous fix one layer deeper, which left no budget for the installer gate; that gate was deferred and its criterion reported open.

### assertion:epic-418-followon_commander-f2-002.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The acceptance measurement was re-run against a role that owns its bound spine after the first two arms were found to have measured a role the fleet's own doctrine directs to the CLI.

## Diagnosis (optional)

### assertion:epic-418-followon_commander-f2-002.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A dispatched agent reads the installed corpus rather than repository source, so instruction edits under skills/ had no effect on the first arm until the corpus was installed.

### assertion:epic-418-followon_commander-f2-002.d2
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Each successive version of the identity pin asserted over a surface rather than over a property, and each reviewer defeated it by acting outside the surface it enumerated: declared arguments, then literal key names, then the calls made, then containment of the engine's output.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
