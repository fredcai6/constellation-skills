<!-- episode-state: schema=1 id=cleanup-a-door-001 status=active -->

# episode: cleanup-a-door-001

## Mechanical
- run: cleanup-a-door
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-a-door/execute.json
- refusals: 12
- reopens: 3
- rework-count: 3
- failed-commands: 4
- artifact-ref: .agent-work/cleanup-a-door/crew-handoffs/g3-final-review-result.md

## Agent-supplied

### assertion:cleanup-a-door-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Sweep the blast radius of the #603 change for prose that the change had made false, after a review found four surviving invalidated claims.

### assertion:cleanup-a-door-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Setting ALLOWED_SCOPE to the rework's editable file would scope the sweep to the work being checked, and a report of zero live in-scope hits would mean the change stranded nothing.

### assertion:cleanup-a-door-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The sweep reported LIVE IN-SCOPE HITS: 0 while its own output also listed six live out-of-scope hits, four of which were one sentence in the changed module's own docstring. The number was accurate and measured the wrong set: ALLOWED_SCOPE is edit permission, not blast radius, so the instrument found the surviving claims and its classification filed them out of the headline.

### assertion:cleanup-a-door-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A third review round and a third rework on a gate whose behaviour had been correct and green since the first attempt; the cap of three reworks was reached on documentation truth alone.

### assertion:cleanup-a-door-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: An independent AST-aware sweep was run over the whole source tree, keyed to the identifiers the change touched, and each of its 4 hits was inspected by hand rather than left to a classifier: 3 turned out to be text quoting the old phrasing precisely to mark that it had changed, and 1 was genuine and sat in a fenced file.

## Diagnosis (optional)

### assertion:cleanup-a-door-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A sweep that reports a count filtered by which files the agent may edit answers 'did I leave a mess I was allowed to clean up' rather than 'what did my change invalidate'.

### assertion:cleanup-a-door-001.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: Blast radius and edit permission were two different sets in this run, and the sweep reported the second under a heading that read as the first.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
