<!-- episode-state: schema=1 id=epic-567-door_cmdr-g-004 status=active -->

# episode: epic-567-door_cmdr-g-004

## Mechanical
- run: epic-567-door/cmdr-g
- project: constellation-skills
- role: commander
- spine-step: review
- context-manifest-ref: .agent-work/epic-567-door/cmdr-g/context/feedback.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-reviewer-result.md
- artifact-ref: .agent-work/epic-567-door/cmdr-g/crew-handoffs/g2-reviewer-result.md
- artifact-ref: .agent-work/epic-567-door/cmdr-g/crew-handoffs/g3-reviewer-result.md

## Agent-supplied

### assertion:epic-567-door_cmdr-g-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatched three independent reviewer crews (g1, g2, g3), each instructed to run the constellation-reviewer skill's own engine-driven survey including its mandatory Fowler pass.

### assertion:epic-567-door_cmdr-g-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Each reviewer's survey engine calls would resolve cleanly against this project's own work-area layout.

### assertion:epic-567-door_cmdr-g-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: All three reviewers independently hit the identical defect: the r6-fowler survey item's postcondition command assumes a flat .agent-work/<work-id>/ layout, but this project's actual convention nests review state under .agent-work/epic-567-door/cmdr-g/<gate>-review/. Each reviewer worked around it identically via the survey template's own documented amend --delta / retext-check repair path.

### assertion:epic-567-door_cmdr-g-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A small, bounded detour for each of three reviewer crews; never blocked a verdict, but recurred three times in one lane without ever being fixed at the source.

### assertion:epic-567-door_cmdr-g-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each reviewer applied the template's own documented repair path independently; the Commander recorded the recurrence as a triage candidate rather than attempting to fix the reviewer skill's own template (outside this lane's file ownership).

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
