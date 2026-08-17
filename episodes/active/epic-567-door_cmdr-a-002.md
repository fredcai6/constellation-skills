<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-002 status=active -->

# episode: epic-567-door_cmdr-a-002

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: init
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: notes-a.md

## Agent-supplied

### assertion:epic-567-door_cmdr-a-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Write working notes to notes-a.md, which the order assigned and called me sole writer of.

### assertion:epic-567-door_cmdr-a-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The assigned filename would be free.

### assertion:epic-567-door_cmdr-a-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: notes-a.md was already tracked at the base commit: 197 lines written by an earlier lane (cleanup/a-door) and committed at 33dc3086. The first write destroyed all of it in the working tree.

### assertion:epic-567-door_cmdr-a-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Recovered fully from git; git diff --numstat showed 178 added and 0 removed. No content lost, but the recovery cost a detour and the risk was total.

### assertion:epic-567-door_cmdr-a-002.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Restored with git show HEAD:notes-a.md and appended my own record below a separator, keeping both lanes' content in one file.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-002.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The order checked the filename against a harness tool guard (it explains at length why not 'findings-a.md') but never against git ls-files.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
