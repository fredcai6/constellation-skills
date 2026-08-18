<!-- episode-state: schema=1 id=epic-567-door-019 status=active -->

# episode: epic-567-door-019

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/567-a/triage-candidates/door-main-catches-only-keyerror.md

## Agent-supplied

### assertion:epic-567-door-019.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A review of which epic findings warranted a tracker issue, against the human's stated bar: a thing that costs agents work repeatedly, rather than a one-off or a risk.

### assertion:epic-567-door-019.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The most severe findings would be the ones filed.

### assertion:epic-567-door-019.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Severity and frequency pointed in different directions. The door's main() catches only KeyError, so any other exception ends the process rather than returning a refusal -- lane A's reviewer found it when a NUL byte in a path raised ValueError and the server exited 1. The blast radius grew during this epic, because the door became the only agent-facing path, so a dead door is now a dead agent rather than a fall-back to the CLI. But it needs an exotic input and has cost exactly one lane one debugging session.

### assertion:epic-567-door-019.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Nothing beyond that one session. Recorded rather than filed, because the human's bar is recurring cost and this is a risk.

### assertion:epic-567-door-019.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Lane A fixed the one instance it hit and left the general shape, deliberately and with the reason stated.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
