<!-- episode-state: schema=1 id=w3-basis-003 status=active -->

# episode: w3-basis-003

## Mechanical
- run: w3-basis
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: ctx-w3-basis-feedback@4e9829e3ad7dfa78bb9743e0eaec40a7daa64186
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w3-basis/execute.json

## Agent-supplied

### assertion:w3-basis-003.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Drive execute.json's child gates (e0-context, g1-implement, g1-review, g1-integrate) through the engine after authoring the plan, per the spine's execute step imperative.

### assertion:w3-basis-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Expected the same mcp__spine__* MCP tools bound to the top-level commander spine (spine.json) to also address execute.json's own gates by task_id, since both are engine-driven checklists in the same run.

### assertion:w3-basis-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: mcp__spine__spine_evidence with task_id='g1-implement' returned REFUSED: no such item 'g1-implement' -- the MCP door only resolves against SPINE_FILE (spine.json), never a child_checklist file. Driving execute.json required the separate scripts/checklist_engine.py CLI directly, invoked as `python3 checklist_engine.py --file .agent-work/w3-basis/execute.json <verb> ...`, which uses the same verb vocabulary (start/attest/attach/advance) but takes a --cond flag before the condition id rather than the MCP tool's condition_id parameter.

### assertion:w3-basis-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One failed MCP call plus a documentation/reference read (crew-dispatch.md, commander-core.md's Checklists you own table) to locate the CLI form. No mission-scope impact once found; would have cost more on a first-time run without commander-core.md's explicit table naming checklist_engine.py as the execute.json driver.

### assertion:w3-basis-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Used `python3 /home/.../checklist_engine.py --file .agent-work/w3-basis/execute.json <verb>` for every execute.json gate transition (start/attest/attach/advance), reserving the mcp__spine__* MCP tools for the top-level spine.json only.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
