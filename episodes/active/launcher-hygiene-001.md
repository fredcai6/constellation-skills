<!-- episode-state: schema=1 id=launcher-hygiene-001 status=active -->

# episode: launcher-hygiene-001

## Mechanical
- run: launcher-hygiene
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/launcher-hygiene/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/launcher-hygiene/execute.json

## Agent-supplied

### assertion:launcher-hygiene-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close execute.json's g5-suite-and-map gate, whose postcondition c1 is the command `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q`, re-verified live by checklist_engine.py's own advance call rather than trusted from an earlier manual run.

### assertion:launcher-hygiene-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Having already run the full suite once via the mandated poll-until idiom (nohup + until-grep, foreground-blocking) and captured its green result, the engine's own re-verification of the same command was expected to either reuse that evidence or complete quickly.

### assertion:launcher-hygiene-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: checklist_engine.py advance re-ran the full suite command itself as part of postcondition verification, took longer than the harness's foreground command timeout, and was moved to background by the harness at 120s -- the exact auto-backgrounding trigger LAUNCH_ORDER-2.md's own text named and the prior five occurrences all failed at.

### assertion:launcher-hygiene-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Cost one extra ~2-minute wait, polled actively via TaskOutput(block=true) inside this same turn rather than ending the turn to wait, so no dispatch was lost -- but it demonstrates the trigger fires even when the agent has already internalized and used the idiom once earlier in the same turn: the engine's own mechanical re-verification is an independent source of the same hazard, not something a single successful poll-until run upstream neutralizes.

### assertion:launcher-hygiene-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Called TaskOutput with block=true and a generous timeout on the backgrounded task id the harness returned, read its completed output (exit 0, gate closed) inside the same turn, and continued driving the spine rather than ending the turn on the pending job.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
