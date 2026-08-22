<!-- episode-state: schema=1 id=w2-reindex-002 status=active -->

# episode: w2-reindex-002

## Mechanical
- run: w2-reindex
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: none -- no context_manifest.py invocation recorded this session
- refusals: 5
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: crew-handoffs/g1-implement-implementer-result.md
- artifact-ref: crew-handoffs/g1-review-reviewer-result.md
- artifact-ref: crew-handoffs/g2-implement-implementer-result.md
- artifact-ref: crew-handoffs/g2-review-reviewer-result.md
- artifact-ref: crew-handoffs/g3-review-reviewer-result.md

## Agent-supplied

### assertion:w2-reindex-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch 5 real implementer/reviewer crews via scripts/run_crew.py's cli backend (no --spine argument, since each gate used the handoff+result-artifact contract rather than a nested spine) for gates g1 and g2's implement/review pairs plus g3's review.

### assertion:w2-reindex-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A cli-backend crew dispatched with no --spine argument would have an unbound or absent SPINE_FILE/SPINE_SESSION, since the wrapper's own door-env assignment is documented as spine-conditional.

### assertion:w2-reindex-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: All 5 of these crews (g1-implement, g1-review, g2-implement, g2-review, g3-review) reported in their own Workflow Feedback / crew-runs.json entries that their inherited SPINE_FILE/SPINE_SESSION resolved toward the dispatching Commander's own bound spine identity rather than being absent, and each one independently recognized this and safely routed around it -- authoring and driving its own scratch checklist/survey through checklist_engine.py's CLI directly, never touching or advancing the Commander's actual spine.

### assertion:w2-reindex-002.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: Zero actual impact on this run -- no spine corruption occurred, confirmed by this Commander re-checking spine_status after every dispatch -- but every one of the 5 affected crews spent part of its own turn diagnosing and routing around the same anomaly independently, a repeated cost that a fixed door-binding contract for --spine-less cli dispatches would remove.

### assertion:w2-reindex-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each crew authored its own scratch checklist/survey and drove it via checklist_engine.py's CLI directly, per this project's own documented branch for a crew whose door resolves to a spine it does not own.

## Diagnosis (optional)

### assertion:w2-reindex-002.d1
- kind: suspected-cause
- strength: weak
- lifecycle-standing: active
- statement: scripts/run_crew.py's _crew_door_env may only assign a fresh SPINE_FILE/SPINE_SESSION to a cli-backend child when --spine is passed, leaving a --spine-less cli dispatch to inherit whatever door-binding state the dispatching process's own environment/MCP session already carries.

### assertion:w2-reindex-002.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: Investigate whether a --spine-less cli-backend dispatch should get an explicitly unbound/absent door assignment rather than inheriting the parent's, so a dispatched crew never has to detect and route around this by its own judgment.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
