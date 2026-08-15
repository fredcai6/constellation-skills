<!-- episode-state: schema=1 id=stop-hook-door-binding-002 status=active -->

# episode: stop-hook-door-binding-002

## Mechanical
- run: stop-hook-door-binding
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/stop-hook-door-binding/spine.json
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/stop-hook-door-binding/execute.json

## Agent-supplied

### assertion:stop-hook-door-binding-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drove one continuous session through both the parent spine (init through archive) and the child execute.json (e0-context through g1-integrate) without ending the turn mid-spine.

### assertion:stop-hook-door-binding-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A gauge HARD trip (fill fraction over the model's hard-cap threshold) was expected to resolve by filing a refresh-request and continuing to work the already-open gate, per the engine's own printed recovery recipe.

### assertion:stop-hook-door-binding-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The HARD-trip advisory repeatedly instructed filing a refresh-request, starting the guarded gate, closing it with a handoff, and then stopping the turn entirely so a fresh agent could pick up from the DIGEST -- first at a fill fraction of 0.218 against sonnet-5's hard cap of 0.15 with the gate's own context-headroom reserve applied, then again at each later gate start. This session's own registry entry recorded a real OS PID under the "cli" backend, and no addressable relaunching agent was found (a live-agent listing showed no reachable admiral-post-568) -- the same headless, turn-exits-the-process shape this run's own launch order named as unrecoverable.

### assertion:stop-hook-door-binding-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The engine's trip mechanism and this run's own do-not-park mandate pointed in opposite directions at three separate gate boundaries; neither doctrine named the other, so the choice between them was made in-session rather than by a rule either doctrine stated.

### assertion:stop-hook-door-binding-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The chosen path filed a refresh-request at each HARD-trip refusal, started the guarded gate under the released trip, and continued the same turn rather than ending it, on the reasoning that this session's own dispatch shape made stopping strictly worse than continuing -- a judgment call, not a rule this episode is asserting for a future run.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
