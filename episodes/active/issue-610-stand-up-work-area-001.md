<!-- episode-state: schema=1 id=issue-610-stand-up-work-area-001 status=active -->

# episode: issue-610-stand-up-work-area-001

## Mechanical
- run: issue-610-stand-up-work-area
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: n/a -- no context-manifest artifact produced this run
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/admiral/templates/LAUNCH_ORDER.template.md
- artifact-ref: skills/admiral/references/fleet-doctrine.md

## Agent-supplied

### assertion:issue-610-stand-up-work-area-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a 7-gate plan for issue #610 (retire the Commander's self-scaffolding recipe everywhere it appears) and get it critiqued before execution.

### assertion:issue-610-stand-up-work-area-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The issue names one edit spot in LAUNCH_ORDER.template.md's Workspace section for the retired cd+--here recipe.

### assertion:issue-610-stand-up-work-area-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A dispatched cold plan critic (fresh agent, mission frame + candidate plan only) greped the actual file and found a second --here reference at line 84 (a return-report evidence clause) the named edit spot did not cover. Following that thread up manually surfaced two more coupled paragraphs (an ordering-hazard callout and a stale-premise paragraph) that also only made sense under the retired recipe -- four spots total, not one, across two files.

### assertion:issue-610-stand-up-work-area-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One extra investigation pass before execute, plus a widened gate imperative and an explicit scope-note surfaced to the human at plan approval. Caught before any file was edited, not as rework.

### assertion:issue-610-stand-up-work-area-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none.

## Diagnosis (optional)

### assertion:issue-610-stand-up-work-area-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: An issue's own prose names the one spot the author noticed; a recipe repeated across explanatory/callout/evidence-clause prose in the same doc is easy to under-scope from the issue text alone.

### assertion:issue-610-stand-up-work-area-001.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: When a plan gate retires an instruction, grep the target file(s) for every mention of the retiring mechanism's own name/flag, not just the one paragraph the issue names, before scoping the gate's postcondition.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
