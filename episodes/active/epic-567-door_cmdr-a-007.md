<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-007 status=active -->

# episode: epic-567-door_cmdr-a-007

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 2
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
- artifact-ref: .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-rereview-review-result.md

## Agent-supplied

### assertion:epic-567-door_cmdr-a-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Have an independent reviewer attack the stated isolation property, which was decision:isolation-not-fencing's recorded settle condition.

### assertion:epic-567-door_cmdr-a-007.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The property -- one checkout's work-area tree per process -- would hold, since I had run six boundary attacks myself and all six refused.

### assertion:epic-567-door_cmdr-a-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Two independent reviewers returned BLOCK on the same two defects by separate routes. The property was false: the cross-checkout guard asked git about the UNRESOLVED candidate.parent while the containment check resolves, so a symlink inside the door's own work area pointing at a nested checkout satisfied both, and one reviewer showed the door writing a live lease into another checkout's spine.

### assertion:epic-567-door_cmdr-a-007.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Two blockers and a rework cycle. Not one of my own six attacks used a symlink.

### assertion:epic-567-door_cmdr-a-007.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Rework resolved before asking git (candidate.resolve().parent) and caught the NUL-byte ValueError; a narrow re-review then APPROVED after 11 symlink spellings in a real multi-checkout topology.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-007.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Two guards on the same input resolved paths differently, and the attack lived in the gap between them rather than in either guard.

### assertion:epic-567-door_cmdr-a-007.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The one-token fix retires the which-spelling-of-which-checkout question rather than adding a third guard beside the other two.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
