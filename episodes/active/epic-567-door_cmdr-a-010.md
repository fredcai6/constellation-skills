<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-010 status=active -->

# episode: epic-567-door_cmdr-a-010

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: scripts/checklist_engine.py

## Agent-supplied

### assertion:epic-567-door_cmdr-a-010.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Audit the new tests for Windows-only hazards before CI, on the Admiral's warning.

### assertion:epic-567-door_cmdr-a-010.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The hazards would be in the tests -- a missing git identity in a fixture, or a byte-for-byte comparison broken by CRLF.

### assertion:epic-567-door_cmdr-a-010.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The tests were already clean on both counts. The defect was in the shipped code: save() called os.fchmod unguarded, and os.fchmod is Unix-only while this repo's CI is windows-latest. Every save of an existing file would raise AttributeError, and every mutating engine verb ends in save().

### assertion:epic-567-door_cmdr-a-010.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Not a red test but a dead engine on the only platform CI runs. No Linux run could have surfaced it, and it was found during closeout rather than by any gate.

### assertion:epic-567-door_cmdr-a-010.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Added _restore_mode: fchmod on the FD where it exists, os.chmod on the path otherwise, with a failed mode copy deliberately non-fatal. The guard test runs on every platform and is proven non-vacuous.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-010.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: The warning pointed at test hazards, and the same platform reasoning applied to the implementation was what actually found it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
