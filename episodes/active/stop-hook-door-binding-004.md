<!-- episode-state: schema=1 id=stop-hook-door-binding-004 status=active -->

# episode: stop-hook-door-binding-004

## Mechanical
- run: stop-hook-door-binding
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/stop-hook-door-binding/crew-handoffs/g1-review-handoff.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0

## Agent-supplied

### assertion:stop-hook-door-binding-004.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Dispatched an independent reviewer crew for g1 via run_crew.py with --handoff/--result only, no --spine.

### assertion:stop-hook-door-binding-004.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: The reviewer was expected to get either no spine binding at all, or a binding scoped to its own review.

### assertion:stop-hook-door-binding-004.a3
- kind: observed-behavior
- strength: medium
- lifecycle-standing: active
- statement: The reviewer's process environment carried this Commander's own SPINE_FILE/SPINE_SESSION -- the parent's execute-step bound spine -- because a run_crew.py dispatch without --spine does not rebind the door for the child. The reviewer declined to drive the MCP door against that inherited binding, since doing so would have mutated the Commander's own execute gate, and fell back to its own CLI-driven survey file at the path the handoff named, per the reviewer skill's documented fallback.

### assertion:stop-hook-door-binding-004.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: No incorrect state resulted this run; the reviewer's own returned result named the mismatch and the fallback path it took, unprompted.

### assertion:stop-hook-door-binding-004.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The reviewer's own fallback resolved it without commander intervention; this run recorded the gap as a recommend-and-defer triage candidate rather than editing crew-dispatch.md, which sits outside this run's file-ownership fence.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
