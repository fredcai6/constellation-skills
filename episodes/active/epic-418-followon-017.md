<!-- episode-state: schema=1 id=epic-418-followon-017 status=active -->

# episode: epic-418-followon-017

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-followon-017.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Merge C3's lifecycle work after it reported a green suite and five reviewers approved it.

### assertion:epic-418-followon-017.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A green number reported from the worktree that produced the change describes the change.

### assertion:epic-418-followon-017.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: C3 reported 2932 passed from its own worktree. The same commit in a detached foreign checkout gave 1 failed, 2931 passed: a test in tests/test_spine_lifecycle.py derived its work id from a path that only existed under C3's own worktree name.

### assertion:epic-418-followon-017.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Five APPROVE verdicts and the crew's own suite run all passed a tree that was red anywhere else. The cold review refused the merge, which cost one repair dispatch and roughly an hour.

### assertion:epic-418-followon-017.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Ran the suite in a git worktree add --detach scratch checkout with SPINE_FILE, SPINE_SESSION and SPINE_ENGINE unset before believing any green number, and dispatched R0 to make the test portable.

## Diagnosis (optional)

### assertion:epic-418-followon-017.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Every reviewer read the same worktree the implementer wrote in, so the environment that made the test pass was common to all six observations.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
