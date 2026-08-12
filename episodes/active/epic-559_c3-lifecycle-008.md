<!-- episode-state: schema=1 id=epic-559_c3-lifecycle-008 status=active -->

# episode: epic-559_c3-lifecycle-008

## Mechanical
- run: epic-559/c3-lifecycle
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: LAUNCH_ORDER-C3@293b7721
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c3-lifecycle/GATE_PLAN.json
- artifact-ref: .agent-work/epic-559/c3-lifecycle/execute.json

## Agent-supplied

### assertion:epic-559_c3-lifecycle-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive the authored gate plan through the engine, gate by gate, as the commander doctrine requires -- work the engine never saw did not happen.

### assertion:epic-559_c3-lifecycle-008.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Expected to drive GATE_PLAN.json through the same MCP door that drives my spine, since both are engine checklists in the same work area.

### assertion:epic-559_c3-lifecycle-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The door binds ONE spine per process and _identity_violation refuses any argv resolving --file off it, so the gate plan cannot be driven through the door at all. The only shipped way an agent drives a second checklist is a second server hand-registered in the user-level ~/.claude.json, which is what the Admiral's own spine-epic entry is -- a manual config edit that cannot take effect mid-session. Separately, the gate-plan template's default filename is execute.json, which is also what this run's spine was named, so writing the plan to its default path would have overwritten the spine mid-run.

### assertion:epic-559_c3-lifecycle-008.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The gate plan was executed as a frozen document with every close-criterion command run by hand instead of by the engine, losing the engine's postcondition enforcement over the gate plan. The filename collision was avoided by writing GATE_PLAN.json.

### assertion:epic-559_c3-lifecycle-008.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Recorded the binding limit as triage candidate tc1 and the filename collision as workflow feedback, ran every gate's close-criteria myself and attached the outcomes to the spine the door IS bound to, and named both in the return rather than letting the run read as fully engine-driven.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
