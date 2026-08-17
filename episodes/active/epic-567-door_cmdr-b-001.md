<!-- episode-state: schema=1 id=epic-567-door_cmdr-b-001 status=active -->

# episode: epic-567-door_cmdr-b-001

## Mechanical
- run: epic-567-door/cmdr-b
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/epic-567-door/cmdr-b/MISSION_FRAME.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-b/PLAN_ALTERNATIVES.md

## Agent-supplied

### assertion:epic-567-door_cmdr-b-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a design for ExternalBackend to default-refuse a spineless-but-fresh crew dispatch (#432), then send it through a cold plan critic (fresh agent, no authoring context, given only the mission frame and candidate plan) before dispatching any implementer.

### assertion:epic-567-door_cmdr-b-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The first-draft design (optional --spine, mtime-only-plus-warning when absent) would be sound enough to hand to an implementer largely as written.

### assertion:epic-567-door_cmdr-b-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The cold critic found 2 CRITICAL findings: (1) accepting --spine newly legalized result=None + spine=<path> on the external path, and the draft's verify() sketch would call result_exists(None, root), a TypeError; (2) the dominant real-world case (dispatcher does not know the spine path at dispatch time) was left as mtime-only-plus-a-stderr-warning -- still an unqualified clean pass, missing the mission's own bar of 'impossible ... to return a clean success.'

### assertion:epic-567-door_cmdr-b-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Caught before any implementer dispatch: the design was revised (verify-time --verify-spine independent of dispatch-time --spine, default-refuse instead of default-warn, an explicit --accept-mtime-only-risk escape hatch, and a result=None guard) in the plan step, at the cost of one extra planning pass, versus what would otherwise have been an implementer building a fix that still left the mission's actual bar unmet for the common case, caught only much later at review or after merge.

### assertion:epic-567-door_cmdr-b-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Rewrote MISSION_FRAME.md's decision anchors, PLAN_ALTERNATIVES.md (added a 'Revision after cold critic' section naming both findings and their fix), and execute.json's g1-implement anchors/constraints before authoring the IMPLEMENTER_HANDOFF, so the handoff the crew actually received already carried the corrected design.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
