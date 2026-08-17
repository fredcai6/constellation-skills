<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-003 status=active -->

# episode: epic-567-door_cmdr-a-003

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

## Agent-supplied

### assertion:epic-567-door_cmdr-a-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run verify_worktree_isolation.py --here after cd-ing into the assigned worktree, as the order sequences it.

### assertion:epic-567-door_cmdr-a-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The two-step sequence would report the worktree as isolated.

### assertion:epic-567-door_cmdr-a-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It reported 'wrong worktree: you are in /home/tommy/projects/constellation-skills' and exited 1. The shell's working directory does not persist between tool calls in this harness, so the bare cd in one call had no effect on the check in the next.

### assertion:epic-567-door_cmdr-a-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Reads as a failed isolation gate when isolation was fine. The previous agent on this lane ran 47 minutes, wrote zero bytes, and its last words were that the bash cwd resets between calls.

### assertion:epic-567-door_cmdr-a-003.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: A single compound call, cd <abs> && py ... --here <abs>, which returns 'worktree OK' and exit 0.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-003.d1
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The order could prescribe the compound single-call form rather than a two-step sequence.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
