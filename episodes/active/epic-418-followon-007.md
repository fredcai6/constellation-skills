<!-- episode-state: schema=1 id=epic-418-followon-007 status=active -->

# episode: epic-418-followon-007

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 4
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/context/salvaged-n1-allowedtools-comment.patch

## Agent-supplied

### assertion:epic-418-followon-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Close the verb gap by adding spine_capture and spine_amend to the MCP door, so all eighteen engine verbs are reachable without the CLI.

### assertion:epic-418-followon-007.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A tool present in the door's TOOLS list would be callable by any dispatched crew.

### assertion:epic-418-followon-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: CREW_ALLOWED_TOOLS in run_crew.py restates the door's tool list, and the two new names were not added to it. The workstream's own cold reviewer called spine_capture four times, was refused at the permission layer each time with a generic message and no engine refusal to explain why, and fell back to the CLI.

### assertion:epic-418-followon-007.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The fallback read as evidence that an agent preferred the CLI, in the very wave whose purpose was to measure door adoption, when the door had in fact been shut on it.

### assertion:epic-418-followon-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Derive the crew allow-list from the door's own tool list rather than restating it; a coupling maintained by memory has already regressed once.

## Diagnosis (optional)

### assertion:epic-418-followon-007.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A permission-layer denial and a deliberate choice produce the same transcript, so a shut door is indistinguishable from a preference unless the allow-list is checked.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
