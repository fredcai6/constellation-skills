<!-- episode-state: schema=1 id=epic-418-followon-011 status=active -->

# episode: epic-418-followon-011

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-011.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Carry issue #555 -- the door does not launch where python3 is not a command -- unworked for a wave, with no spend authorized and its disposition reserved to the human.

### assertion:epic-418-followon-011.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: An issue carried as unworked has no work done against it, so carrying it costs only the carrying.

### assertion:epic-418-followon-011.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The fix already existed on an unmerged branch, fix/mcp-door-launchable, measured against a specific client version with marker-writing launcher scripts and proven on Windows CI. It sat unmerged for three waves while the issue was carried as unworked, and .mcp.json on main still hardcoded python3.

### assertion:epic-418-followon-011.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The door remained unlaunchable on the repo owner's own platform for three waves, on the grounds that no spend was authorized, when the spend had already happened and only the merge was missing.

### assertion:epic-418-followon-011.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Before carrying an issue as unworked, check whether a branch already answers it; the worktree sweep found this one, which means nothing before the sweep was looking.

## Diagnosis (optional)

### assertion:epic-418-followon-011.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: 'Carried, no spend authorized' describes a decision about future work and says nothing about work already done, so it stays true and stops being relevant at the same moment.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
