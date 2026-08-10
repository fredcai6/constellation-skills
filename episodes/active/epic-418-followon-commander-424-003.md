<!-- episode-state: schema=1 id=epic-418-followon-commander-424-003 status=active -->

# episode: epic-418-followon-commander-424-003

## Mechanical
- run: epic-418-followon-commander-424
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/commander-424/execute.json
- refusals: 1
- reopens: 0
- rework-count: 2
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/commander-424/crew-handoffs/g3-implementer-result.md
- artifact-ref: .agent-work/epic-418-followon/commander-424/evidence/g1-resolve-varexp

## Agent-supplied

### assertion:epic-418-followon-commander-424-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Resolve a gate blocked by its own reviewer over whether scripts/gen_mcp_config.py was necessary, by measuring the one fact the blocker named: does an in-session Task-tool subagent share its parent's already-launched MCP server?

### assertion:epic-418-followon-commander-424-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The blocker recorded the branch explicitly: if the subagent shares the parent's server then ${VAR} expansion cannot reach that case and per-dispatch config generation is required; if it spawns its own process, generation is redundant.

### assertion:epic-418-followon-commander-424-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The antecedent measured TRUE -- a Task-tool subagent inherits its dispatching process's MCP scope wholesale and reached the parent's exact spine and identity with no configuration of its own, reproduced twice with independent nonces and corroborated by the server's own call log. The stated consequent did not follow. A generated config binds at server launch per process exactly as ${VAR} does, so it cannot give an in-session subagent its own identity either. The measurement expected to justify the file named a case neither mechanism reaches, and therefore did not distinguish them.

### assertion:epic-418-followon-commander-424-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: scripts/gen_mcp_config.py was removed rather than justified, along with four generation-only tests, and two test files were rewired onto the shipped ${VAR} path. Had the blocker's stated implication been taken at face value, the measurement would have read as confirming the file and it would have shipped on a false justification -- the second false justification that file had accumulated.

### assertion:epic-418-followon-commander-424-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Removal went through the gate's own rework path rather than an override: a rework implementer removed the file, and the same reviewer that blocked re-reviewed and returned APPROVE after re-reproducing the ${VAR} identity measurement itself. The tombstone and the non-implication were written into docs/CHECKLIST_ENGINE_DESIGN.md, because the measured YES is exactly the fact a later reader would use to rebuild the file.

## Diagnosis (optional)

### assertion:epic-418-followon-commander-424-003.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The blocker recorded a conditional whose two halves were not symmetric: it checked whether ${VAR} could reach the shared-server case but never asked the same question of generation. Both mechanisms bind identity at server launch, so any case beyond one is beyond the other.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
