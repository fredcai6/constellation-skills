<!-- episode-state: schema=1 id=epic-567-door-030 status=active -->

# episode: epic-567-door-030

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 2
- failed-commands: 2
- artifact-ref: .agent-work/567-n/RETURN.md
- artifact-ref: specs/

## Agent-supplied

### assertion:epic-567-door-030.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatching an implementer with a spine, so it would drive its plan through the MCP door like every other lane in this epic.

### assertion:epic-567-door-030.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Every role in this corpus has a spine, so init_work_area.py --role implementer would provision one.

### assertion:epic-567-door-030.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: No implementer spine role exists. The provisioning call rejected the argument and the --spine form wanted a path that had nothing to point at. The lane was dispatched with --handoff/--result and no SPINE_FILE, so its door bound nothing, and it drove its own IMPLEMENTER_PLAN.json through scripts/checklist_engine.py instead.

### assertion:epic-567-door-030.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The Admiral's own dispatch shape forced a CLI use inside the epic whose subject is removing the CLI as an agent-facing path. Two failed provisioning commands before the shape was understood.

### assertion:epic-567-door-030.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Dispatched on the result-artifact shape, which is the correct shape for a role judged on a deliverable rather than a terminal state.

## Diagnosis (optional)

### assertion:epic-567-door-030.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The door binds one spine at process start, so a role with no spine is a role the door structurally cannot serve. This sits in the same family as the self-waive refusal and the archive-move deadlock -- the door's path, identity and spine are all fixed before the work starts -- and is the sharpest instance, because it is not a run acting on itself but a role with nothing to bind.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
