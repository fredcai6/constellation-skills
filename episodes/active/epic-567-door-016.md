<!-- episode-state: schema=1 id=epic-567-door-016 status=active -->

# episode: epic-567-door-016

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-016.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Model tiers chosen per lane, least-powerful-that-works, recorded in each launch order's budget slot.

### assertion:epic-567-door-016.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Sonnet lanes running Sonnet work.

### assertion:epic-567-door-016.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The lanes ran at their assigned tiers, and the crews they dispatched did not. run_crew.py inherits the host settings default when --model is unset, so one Opus-tiered lane spawned 15 crew sessions all on Opus, 6 of them abandoned and retried. The budget slot names a tier for the dispatched Commander and reaches nothing below it.

### assertion:epic-567-door-016.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Unbudgeted spend across an entire lane subtree. Nothing surfaced it during the run; the human noticed it on the bill and asked.

### assertion:epic-567-door-016.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Remaining work was pinned to Sonnet by human ruling. The Admiral's first proposed fix -- inherit the dispatcher's tier -- was rejected by the human as laundering the same defect, and replaced by a per-role default with an allowed set and a recorded reason for deviation.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
