<!-- episode-state: schema=1 id=commander-315-native-001 status=active -->

# episode: commander-315-native-001

## Mechanical
- run: commander-315-native
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/commander-315-native/execute.json
- refusals: 1
- reopens: 0
- rework-count: 1
- failed-commands: 1
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1-implementer-result.md
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1b-implementer-result.md

## Agent-supplied

### assertion:commander-315-native-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Preserve the native engine worktree guard while restoring crew and MCP workflows broken by the new ambient-cwd comparison.

### assertion:commander-315-native-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A dispatched crew would already run in its assigned worktree and the in-process MCP door would be able to drive a newly opened origin-stamped spine without weakening the guard.

### assertion:commander-315-native-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The frozen ruling's crew-cwd premise was empirically false because run_crew passed no cwd, and the MCP door could not already stand in a worktree that spine_open had only just created; the untouched lifecycle round trip failed.

### assertion:commander-315-native-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The implementation reached independent review before the false premise was measured, then the only full-suite failure blocked integration and required a human ruling that expanded the production scope to two cwd owners.

### assertion:commander-315-native-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The run floated the collision with measurements, and the human ruled both repairs; commit 48f07123 now establishes an absolute crew cwd and a narrowly scoped MCP engine cwd.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
