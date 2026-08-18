<!-- episode-state: schema=1 id=epic-567-door-020 status=active -->

# episode: epic-567-door-020

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/567-a/triage-candidates/gauge-writer-hook-fixed-temp-name.md

## Agent-supplied

### assertion:epic-567-door-020.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: The same review, applied to a defect in what the repo presents as its canonical atomic write.

### assertion:epic-567-door-020.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A live corruption risk in a hook every session runs.

### assertion:epic-567-door-020.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: scripts/hooks/gauge_writer_hook.py's _atomic_write_json uses one fixed temp name per target, so two concurrent writers share it, and a cold critic reproduced a durably unparseable document. In practice gauge files are keyed per session, so two writers on one path is rare and the critic had to construct it. What is actually wrong is the labelling: it is presented as the canonical atomic write, which invites reuse into places where two writers are ordinary.

### assertion:epic-567-door-020.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: No observed corruption in this epic. The cost is prospective and arrives through copying rather than through this call site.

### assertion:epic-567-door-020.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Left unfixed and recorded. Hook code runs from the main checkout for every live session, so editing one mid-wave can break other running agents.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
