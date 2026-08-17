<!-- episode-state: schema=1 id=epic-567-door_cmdr-a-012 status=active -->

# episode: epic-567-door_cmdr-a-012

## Mechanical
- run: epic-567-door/cmdr-a
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-a/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: RETURN.md
- artifact-ref: notes-a.md

## Agent-supplied

### assertion:epic-567-door_cmdr-a-012.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Keep the run's records accurate as reviewers refined each other's findings.

### assertion:epic-567-door_cmdr-a-012.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A reviewer's correction to an earlier reviewer's finding could be adopted as-is.

### assertion:epic-567-door_cmdr-a-012.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first reviewer narrowed a finding -- the NUL byte kills the door 'only when already bound' -- and I adopted that into two records. A later reviewer disproved the narrowing: the unbound door dies too, through a different code path. My original unconditional statement had been right.

### assertion:epic-567-door_cmdr-a-012.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Two records carried a false refinement for part of the run. Small in consequence, and it happened in the one dimension the run was otherwise disciplined about.

### assertion:epic-567-door_cmdr-a-012.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Corrected both records and named the asymmetry: I spent the run refusing to accept reviewers' claims without re-deriving them, and accepted a reviewer's correction without re-deriving it.

## Diagnosis (optional)

### assertion:epic-567-door_cmdr-a-012.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A correction reads as a concession rather than as a new claim, so it invites less scrutiny than the claim it corrects.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
