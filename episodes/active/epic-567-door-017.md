<!-- episode-state: schema=1 id=epic-567-door-017 status=active -->

# episode: epic-567-door-017

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-017.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A dispatched lane reaching the context HARD band mid-run.

### assertion:epic-567-door-017.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A handoff.

### assertion:epic-567-door-017.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The lane refused the engine's own advisory to close its gate and hand off, because the gate's postconditions were genuinely unmet and closing it would produce a successor that closed it again. It left the gate pending with a refresh-request attached, committed its plan, and wrote a resume note. A relaunch was then refused by the duplicate-crew guard because the lane's process was still alive -- idle, artifacts complete, but running.

### assertion:epic-567-door-017.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The refusal cost one round-trip and prevented two Commanders being placed in one worktree, which the Admiral had been about to do after reading the spine and the return and concluding the lane had handed off.

### assertion:epic-567-door-017.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The process was confirmed idle from artifacts, terminated, and its absence verified before relaunch. The launcher recorded the attempt as 'failed', which is mechanically true and the wrong adjudication -- a refresh-request is a sanctioned outcome and the vocabulary has no word for it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
