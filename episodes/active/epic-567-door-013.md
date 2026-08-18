<!-- episode-state: schema=1 id=epic-567-door-013 status=active -->

# episode: epic-567-door-013

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

### assertion:epic-567-door-013.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: The cross-project feedback sweep the Admiral closeout mandates, run per docs/DEBT_SWEEP_CADENCE.md so the loop does not go dormant.

### assertion:epic-567-door-013.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A report of uncollected feedback from the dogfood projects.

### assertion:epic-567-door-013.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The documented roots are Windows paths absent from this Linux host. The documented invocation exited 0 and reported 'No new or open candidates' having opened zero export files. Pointed at the paths that exist, the same script found 10 uncollected candidates, 2 of them recurring -- one about CLI session-id flag position, hit twice by a consuming project while the corpus still taught the CLI. A fourth project carrying an export was absent from the roots list entirely.

### assertion:epic-567-door-013.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The mechanism that exists to stop a loop going dormant had been certifying it healthy while reading nothing. How long is unknown.

### assertion:epic-567-door-013.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Both reports were preserved side by side so the difference is checkable. The sweep was left read-only: marking ten findings collected while nothing had been done with them is how the loop goes dormant while continuing to look healthy.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
