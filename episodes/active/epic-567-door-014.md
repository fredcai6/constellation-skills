<!-- episode-state: schema=1 id=epic-567-door-014 status=active -->

# episode: epic-567-door-014

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
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-014.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: An architecture reconcile against the repo's map, and orientation for every lane that ran in it.

### assertion:epic-567-door-014.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A map to orient against.

### assertion:epic-567-door-014.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: map/INDEX.md is fully built at 30,743 bytes across 165 module directories, and map/ids.jsonl is 0 bytes. Rebuilding from a clean detached worktree exits 0, leaves map/ with no diff, and leaves ids.jsonl empty -- because it is written from minted anchor ids and this repo has none. Every Commander that runs here therefore orients DEGRADED, permanently. Two lanes reported it independently.

### assertion:epic-567-door-014.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Every lane this wave paid a degraded orientation, and a downstream check (verify-frame) passes only frames that cite nothing, for the same root cause.

### assertion:epic-567-door-014.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: A wave-1 triage candidate had recorded the symptom with the wrong diagnosis -- stale generated file -- and the corrected diagnosis was recorded against it rather than by editing another lane's staged file.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
