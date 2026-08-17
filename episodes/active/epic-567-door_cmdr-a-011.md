<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-011 status=active -->

# episode: epic-567-door_cmdr-a-011

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md

## Agent-supplied

### assertion:epic-567-door_cmdr-a-011.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Judge whether a reviewer that had produced no result artifact was still alive.

### assertion:epic-567-door_cmdr-a-011.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A dirty working tree with no writes for several minutes would indicate a crashed agent.

### assertion:epic-567-door_cmdr-a-011.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The reviewer was alive and mid-mutation; it went on to deliver a 1651-line review with two real blocking defects. I had used a 6-8 minute no-write threshold and restored a tracked file underneath a working agent, then filed an incident report saying it had died.

### assertion:epic-567-door_cmdr-a-011.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: No damage, because the reviewer md5-verified its own restores and its result matched the mutation I ran myself. The reasoning was wrong regardless, and global-orchestrator.md gives ten minutes as the floor precisely because a shorter threshold adjudicates live agents dead.

### assertion:epic-567-door_cmdr-a-011.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Corrected the record rather than editing the wrong version away, and reframed the related triage candidate from a crew-discipline point to a handoff-template one.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-011.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Crashed-mid-mutation and working-normally-mid-mutation are byte-identical on disk, so no filesystem probe can distinguish them.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
