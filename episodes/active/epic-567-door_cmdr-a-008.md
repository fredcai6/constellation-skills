<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-008 status=active -->

# episode: epic-567-door_cmdr-a-008

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: scripts/checklist_engine.py
- artifact-ref: tests/test_checklist_engine_atomic_save.py

## Agent-supplied

### assertion:epic-567-door_cmdr-a-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Reuse the repo's own canonical atomic-write pattern for save(), per one-canonical-path.

### assertion:epic-567-door_cmdr-a-008.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Mirroring scripts/hooks/gauge_writer_hook.py:513 _atomic_write_json would be the safe choice.

### assertion:epic-567-door_cmdr-a-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A cold critic ran that pattern with two concurrent writers and it installed a DURABLY unparseable document: the fixed temp name means both writers share one temp path, so the loser's buffered flush writes into the inode os.replace just installed as the live file. Today's tear is transient and heals on the next write; an installed corrupt document is permanent.

### assertion:epic-567-door_cmdr-a-008.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The handoff as written would have shipped a worse bug than the one being fixed, in a repo where run_crew's parent-heartbeat thread makes two writers a supported case.

### assertion:epic-567-door_cmdr-a-008.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Respecified the write directly: unique tempfile.mkstemp, mode restored, flush plus fsync, os.replace, temp unlinked in a finally. Recorded the hook's own hazard as a triage candidate rather than editing a fenced file.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-008.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The pattern is presented as canonical and carries a confident comment, so it invites reuse without being read.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
