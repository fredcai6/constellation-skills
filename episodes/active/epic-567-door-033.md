<!-- episode-state: schema=1 id=epic-567-door-033 status=active -->

# episode: epic-567-door-033

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 2
- failed-commands: 0
- artifact-ref: scripts/check_role_spine_bookends.py
- artifact-ref: scripts/checklist_engine.py

## Agent-supplied

### assertion:epic-567-door-033.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Shipping a bookend freeze and a drift lint that stop a run deleting the steps that make it finish.

### assertion:epic-567-door-033.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A merged, green, gated deliverable on main is a delivered deliverable.

### assertion:epic-567-door-033.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both were inert on main. The lint named its own gap precisely -- repo=['closeout','init'] installed=[] for the admiral template, and the same shape for commander and explorer -- because the freeze reads declarations from the installed corpus, not the repo source. After the human ordered a reinstall it flipped to all 3 role spine template(s) declare bookends and match the installed corpus.

### assertion:epic-567-door-033.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Between merge and reinstall, two deliverables the epic reported as shipped protected nothing on the machine that runs the agents.

### assertion:epic-567-door-033.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The reinstall was requested from the human rather than performed unasked, because it is a deployment action on their machine and this session had already reverted one installer-caused change.

## Diagnosis (optional)

### assertion:epic-567-door-033.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: For anything the installed corpus reads rather than the repo source, merged and deployed are different states, and the suite can only see the first.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
