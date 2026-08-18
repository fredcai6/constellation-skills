<!-- episode-state: schema=1 id=epic-567-door-029 status=active -->

# episode: epic-567-door-029

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
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/templates/TEMPLATES_MANIFEST.json

## Agent-supplied

### assertion:epic-567-door-029.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Counting live referrers to six workbench files, to tell the human what was genuinely deletable at the cheap tier.

### assertion:epic-567-door-029.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Excluding .agent-work/ from the search cuts archived run artifacts, which quote paths as history rather than depending on them.

### assertion:epic-567-door-029.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: That exclusion also dropped .agent-work/templates/TEMPLATES_MANIFEST.json, a tracked overlay manifest that is a live referrer. One file was reported as having zero referrers when it has two, and re-measuring showed all six files have live referrers -- checklist-engine.md 32, status-model.md 10, STATE_NOTE 9, WORKFLOW_CLOSEOUT 8, CONSTELLATION_FEEDBACK 5, DEFAULT 2. This was the third bad count of the same file set in two days.

### assertion:epic-567-door-029.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: It changed the answer rather than a detail of it: there was no deletion available at the cheap tier at all, which is what closed the lane.

### assertion:epic-567-door-029.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Corrected to the human before the number was acted on. The earlier bad counts were caught by implausibility (125 and 180 referrers) rather than by measuring correctly, which is a weaker check.

## Diagnosis (optional)

### assertion:epic-567-door-029.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A path-shaped exclusion filter cannot separate archive noise from tracked content when both live under the same prefix, and .agent-work/ holds both an archive and a tracked template overlay.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
