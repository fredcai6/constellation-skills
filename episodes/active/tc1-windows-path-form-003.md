<!-- episode-state: schema=1 id=tc1-windows-path-form-003 status=active -->

# episode: tc1-windows-path-form-003

## Mechanical
- run: tc1-windows-path-form
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/tc1-windows-path-form/REPLAN_INPUT.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/tc1-windows-path-form/execute.json

## Agent-supplied

### assertion:tc1-windows-path-form-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Advance g1-integrate once its postconditions -- the amended check re-run and the already-integrated reviewer APPROVE -- were both satisfied.

### assertion:tc1-windows-path-form-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: advance <task> would succeed once the underlying postconditions were met, the same way the immediately prior amend and retext-check calls had.

### assertion:tc1-windows-path-form-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: REFUSED: 'advancing a non-exempt gate requires a running understanding -- pass --why "<understanding>" ... or --mechanical'. This requirement was not visible in execute.json's own ACTIVE-line output at the time; it only became apparent from the failure message itself (and, in hindsight, from spine.json's separately-rendered next: line for its own execute step, which did show the --why form).

### assertion:tc1-windows-path-form-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One avoidable failed command, plus a second ~124s background wait for the engine's own re-run of the full-suite check inside the successful advance, on top of the confirmation run already performed manually before attempting it.

### assertion:tc1-windows-path-form-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The advance call on this non-exempt gate refused until it carried a --why with a genuine one-line understanding statement; supplying that statement up front on the retry avoided a second refusal round-trip and the extra background wait for the engine's own full-suite re-run inside the successful advance.
- history: restated — restated from advice to a future reader into an observation of what this run did and found (tc1-episode-rewording, per LAUNCH_ORDER admiral-post-568) — original statement was: Always pass --why with a genuine one-line understanding statement on every advance call for a non-exempt gate, rather than waiting for the refusal to name it.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
