<!-- episode-state: schema=1 id=cleanup-a-door-004 status=active -->

# episode: cleanup-a-door-004

## Mechanical
- run: cleanup-a-door
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/cleanup-a-door/execute.json
- refusals: 12
- reopens: 3
- rework-count: 3
- failed-commands: 4
- artifact-ref: .agent-work/cleanup-a-door/crew-handoffs/plan-critic-result.md

## Agent-supplied

### assertion:cleanup-a-door-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Freeze a three-gate plan for the door cleanup, built from the launch order's pre-rulings and a direct read of the server.

### assertion:cleanup-a-door-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A cold critic reading only the mission frame, the plan and the source would confirm the plan or find refinements.

### assertion:cleanup-a-door-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The critic returned four blocking findings, each independently reproducible: a second hard os.environ['SPINE_FILE'] read sitting on spine_open's own path, so the plan as written could not reach its exit criterion; open_work returning three binding values, so binding one leaves the engine refusing claim; .mcp.json's ${SPINE_FILE:-} expanding to empty rather than unset, a failure world the plan had not described and the one production takes; and both integrate postconditions passing on the defective tree, measured.

### assertion:cleanup-a-door-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The plan would have shipped a change that refused correctly and still could not bind, with two gate postconditions that could not discriminate. Catching it cost one dispatch before any implementation.

### assertion:cleanup-a-door-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Every load-bearing critic claim was reproduced independently before any of it was acted on, and the plan was then revised: the gate order was reversed, two gates gained a required pre-fix-failing regression test, and three committed assertions the change would break were budgeted into the last gate.

## Diagnosis (optional)

### assertion:cleanup-a-door-004.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A plan authored from a frozen order inherits the order's blind spots, and its author cannot see them by re-reading it.

### assertion:cleanup-a-door-004.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The critic saw what the plan's own author could not, because the author had inherited the same blind spots from the frozen order.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
