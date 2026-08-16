<!-- episode-state: schema=1 id=cleanup-a-door-003 status=active -->

# episode: cleanup-a-door-003

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
- artifact-ref: .agent-work/cleanup-a-door/crew-handoffs/g3-reviewer-result.md

## Agent-supplied

### assertion:cleanup-a-door-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Rebuild map/INDEX.md after adding a new test module, as the freshness gate requires.

### assertion:cleanup-a-door-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Running code_map build and committing the result would leave the map fresh and the suite green.

### assertion:cleanup-a-door-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The rebuild ran eight minutes before the new test file was staged. code_map enumerates via git ls-files, so it counted 83 test modules, wrote an index matching that, and its own freshness guard passed. Staging the file made it tracked and the same guard went red at 84. The trap fired twice in one run, at g1 and again at g3; a gate in between repaired the first instance incidentally, which hid it.

### assertion:cleanup-a-door-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A review round returned BLOCK on a red suite for a gate whose behaviour was correct, and the bisect to attribute it cost seven revision checkouts.

### assertion:cleanup-a-door-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The rework staged every file first, rebuilt the map last, and committed after that, and the freshness guard then stayed green.

## Diagnosis (optional)

### assertion:cleanup-a-door-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A rebuild run against a partially-staged tree is self-consistent, so the guard confirms the rebuild rather than the corpus.

### assertion:cleanup-a-door-003.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The closeout order determined whether the guard saw the real corpus; the rebuild happened while the tree was only partly staged.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
