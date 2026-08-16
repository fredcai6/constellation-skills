<!-- episode-state: schema=1 id=cleanup-a-door-005 status=active -->

# episode: cleanup-a-door-005

## Mechanical
- run: cleanup-a-door
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-a-door/execute.json
- refusals: 12
- reopens: 3
- rework-count: 3
- failed-commands: 4
- artifact-ref: .agent-work/cleanup-a-door/LAUNCH_ORDER.md

## Agent-supplied

### assertion:cleanup-a-door-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive a ten-step commander spine to a terminal archive under a launch order.

### assertion:cleanup-a-door-005.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine's context band would restrict work only when context was genuinely spent.

### assertion:cleanup-a-door-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The HARD band tripped on the first start verb of the execute step, at 22% of a 1M window with roughly 780K left, and then on nearly every subsequent start and reopen: e0-context, three g3 reopens, three g3-review starts, reconcile, triage, review and feedback. The band is an absolute 150K cap, which loading the skill, its references, the templates and the order already exceeds.

### assertion:cleanup-a-door-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Eleven extra refusal-and-attach round trips. Without the launch order's explicit pre-ruling that arriving over HARD is not a stop condition, the correct-looking response at each trip was to advance and hand off, which the order names as producing an infinite handoff chain with no deliverable.

### assertion:cleanup-a-door-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: A refresh-request was attached against the current why-record before each start verb, which is the release path the engine and the launch order both name, and the run then continued rather than handing off.

## Diagnosis (optional)

### assertion:cleanup-a-door-005.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: An absolute token cap does not scale with the model's window, so on a large-window model it reads as exhausted at the moment a role finishes loading its own doctrine.

### assertion:cleanup-a-door-005.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The band is an absolute token count rather than a fraction of the window, so a large-window model reads as exhausted once a role has finished loading its own doctrine.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
