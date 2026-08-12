<!-- episode-state: schema=1 id=epic-418-followon-004 status=active -->

# episode: epic-418-followon-004

## Mechanical
- run: epic-418-followon
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 4
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-followon/transitions/w7x-lifecycle/REPLAN_RESULT.json

## Agent-supplied

### assertion:epic-418-followon-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Gate every merge on a cold review by a reviewer independent of the implementer, re-running the implementer's own controls.

### assertion:epic-418-followon-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Independent reviews would catch what a single review missed, so more rounds would mean more coverage.

### assertion:epic-418-followon-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: One branch was reviewed five times. The first four each ran real commands and each answered its own questions correctly, and each missed something different: a field that was never quoted, a stale session id present on nine of nine gates, that same id written into a review's own evidence line as proof of completeness, and a divergence one reviewer saw, described accurately, then scoped away. The fifth found nine stale ids nobody had looked for.

### assertion:epic-418-followon-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Four review rounds established that mechanisms operated while a wrong value rode through all of them; the defect survived every round that was supposed to catch it, and was caught only when a reviewer changed method rather than tried harder.

### assertion:epic-418-followon-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Ask two questions of every check, not one: does this mechanism work, and is the value it carries correct. The fifth reviewer's difference was treating its own green results as questions.

## Diagnosis (optional)

### assertion:epic-418-followon-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A review confirms that a mechanism operates and does not interrogate the value it operates on. Absence reads as correct because there is nothing to look at, and ubiquity reads as correct because nine-of-nine reads as deliberate.

### assertion:epic-418-followon-004.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The repo's three-way guard fixture covers absence; nothing covers a value that is wrong but consistent, and that gap is what the fifth round had to close by hand.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
