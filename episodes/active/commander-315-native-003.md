<!-- episode-state: schema=1 id=commander-315-native-003 status=active -->

# episode: commander-315-native-003

## Mechanical
- run: commander-315-native
- project: constellation-skills
- role: commander
- spine-step: g1-integrate
- context-manifest-ref: .agent-work/commander-315-native/execute.json
- refusals: 2
- reopens: 0
- rework-count: 0
- failed-commands: 3
- artifact-ref: .agent-work/commander-315-native/mcp_amend_delta_20260813T143848826680.json
- artifact-ref: .agent-work/commander-315-native/REPLAN_INPUT.json

## Agent-supplied

### assertion:commander-315-native-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close the execute integration gate with the same full test suite that passed in the reviewer and a clean shell.

### assertion:commander-315-native-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The engine-owned pytest child would see the normal clean caller environment and reproduce 2981 passing tests.

### assertion:commander-315-native-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The MCP server's SPINE_FILE, SPINE_ENGINE, and SPINE_SESSION bindings were inherited by the pytest child, deterministically failing DC3InheritanceMechanismTests while the same tree passed when those three names were absent.

### assertion:commander-315-native-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Two engine advance refusals and one exact reproduction were needed to separate a harness-environment false red from product rework; the frozen gate command could not pass under the selected MCP-first interaction path.

### assertion:commander-315-native-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: An Admiral-ratified MCP retext-check changed only g1-integrate.c1 to clear the three door bindings for pytest; the engine then recorded 2981 passed without a waiver.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
