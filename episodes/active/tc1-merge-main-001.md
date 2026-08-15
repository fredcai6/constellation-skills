<!-- episode-state: schema=1 id=tc1-merge-main-001 status=active -->

# episode: tc1-merge-main-001

## Mechanical
- run: tc1-merge-main
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/tc1-merge-main/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/tc1-merge-main/execute.json

## Agent-supplied

### assertion:tc1-merge-main-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close g1-verify (a gate inside the child checklist execute.json, distinct from the top-level spine.json) after the clean-env suite passed, using the MCP door tools available in this session.

### assertion:tc1-merge-main-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Calling mcp__spine__spine_advance with task_id 'g1-verify' would close that gate, since spine_status's ACTIVE line and the launch order both referred to gate-level work without distinguishing which checklist file backed it.

### assertion:tc1-merge-main-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: mcp__spine__spine_advance refused with 'REFUSED: no such item g1-verify' -- the running MCP door was bound (via SPINE_FILE/SPINE_SESSION at server start) to the top-level spine.json, whose only items are steps like context/plan/execute/reconcile/triage/review, not execute.json's own gates (e0-context, g1-merge, g1-verify, g1-push). The child checklist had to be driven with the CLI directly: python scripts/checklist_engine.py --file .agent-work/tc1-merge-main/execute.json advance g1-verify.

### assertion:tc1-merge-main-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One refused tool call plus a re-read of skills/workbench/references/checklist-engine.md's 'One agent, one plan' section to confirm the door does not follow child_checklist references -- a few minutes, no rework, no wasted execution.

### assertion:tc1-merge-main-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Switched to `python scripts/checklist_engine.py --file .agent-work/tc1-merge-main/execute.json <verb>` for every execute.json gate (g1-verify, g1-push), and kept using the mcp__spine__* door tools only for the top-level spine.json steps (execute, reconcile, triage, review) that the running door was actually bound to.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
