<!-- episode-state: schema=1 id=commander-315-native-004 status=active -->

# episode: commander-315-native-004

## Mechanical
- run: commander-315-native
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/commander-315-native/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: scripts/mcp_spine_server.py
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1c-reviewer-result.md

## Agent-supplied

### assertion:commander-315-native-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Use the spine MCP server rather than the checklist-engine CLI for every engine interaction in an already-running Codex host.

### assertion:commander-315-native-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The native spine MCP tools or a concise manual-stdio invocation example would be available after the server was added to the harness.

### assertion:commander-315-native-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The host did not hot-load the new MCP tools, and handoffs supplied environment bindings but no initialize, tools/list, or tools/call JSON-RPC envelopes; one guessed tool name also failed before tools/list exposed the actual schema.

### assertion:commander-315-native-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Every Commander and replacement-crew engine call required newline-delimited JSON construction and result parsing, and implementers/reviewers independently reconstructed the same protocol.

### assertion:commander-315-native-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The run kept persistent stdio server sessions bound to each exact job file, called tools/list to discover schemas, and used only JSON-RPC MCP calls for engine state changes.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
