<!-- episode-state: schema=1 id=w2-basis-004 status=active -->

# episode: w2-basis-004

## Mechanical
- run: w2-basis
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: none -- no context-manifest artifact produced this run
- refusals: 10
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w2-basis/crew-handoffs/g1-implementer-result.md
- artifact-ref: .agent-work/w2-basis/crew-handoffs/g1-reviewer-result.md
- artifact-ref: .agent-work/w2-basis/crew-handoffs/g2-implementer-result.md
- artifact-ref: .agent-work/w2-basis/crew-handoffs/g2-reviewer-result.md
- artifact-ref: .agent-work/w2-basis/crew-handoffs/g3-implementer-result.md
- artifact-ref: .agent-work/w2-basis/crew-handoffs/g3-reviewer-result.md

## Agent-supplied

### assertion:w2-basis-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: All 6 crew dispatches this run (3 gates x implementer + reviewer) used run_crew.py's cli backend per the launch order's instruction to use real independent crews, not self-review.

### assertion:w2-basis-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Given crew-dispatch.md's description of the cli backend ('a fresh process: run_crew._crew_door_env assigns its SPINE_FILE/SPINE_SESSION/SPINE_PARENT, so its door is bound to its own plan from the first call'), each crew's door was expected to resolve to its own gate-scoped plan/survey, not to the dispatching Commander's own spine.

### assertion:w2-basis-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: All 6 crews independently reported, in their own Workflow Feedback sections, that SPINE_FILE/SPINE_SESSION in their dispatch environment resolved to the parent Commander's own execute.json/spine, and that their own crew-runs.json entry recorded spine: null -- confirming no door was actually bound for them specifically. Every one of the 6 correctly declined to drive the parent's spine and instead authored and drove its own local plan/survey JSON through the CLI directly, citing what reads as an already-established convention from prior work on this and a sibling work-id. Zero crews mistakenly touched the parent's execute.json or spine.json.

### assertion:w2-basis-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: No incorrect engine state produced by any crew, and no rework needed -- but 6 out of 6 dispatched crews spent part of their own context independently re-discovering and re-confirming the identical spine:null situation, which the w1-verdict episode already recorded once for a sibling wave. This is now the third independent run (w1-verdict, and this run's own g1/g2/g3 pairs) to hit and correctly self-resolve the same pattern.

### assertion:w2-basis-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: No Commander-side intervention was needed at any of the 6 dispatches -- every crew self-corrected per its own role skill's documented branch for a spine:null dispatch.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
