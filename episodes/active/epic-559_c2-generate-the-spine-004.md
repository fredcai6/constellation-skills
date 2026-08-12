<!-- episode-state: schema=1 id=epic-559_c2-generate-the-spine-004 status=active -->

# episode: epic-559_c2-generate-the-spine-004

## Mechanical
- run: epic-559/c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 2
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-implement-result.md
- artifact-ref: map/INDEX.md

## Agent-supplied

### assertion:epic-559_c2-generate-the-spine-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Add a new module, `scripts/generate_spine.py`, and keep the suite green at every gate boundary.

### assertion:epic-559_c2-generate-the-spine-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Adding a module changes only the files the change touches and their tests.

### assertion:epic-559_c2-generate-the-spine-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It staled `map/INDEX.md`, which asserts the module and entity counts: 57 modules against 56 committed. It surfaced as one red test in an unrelated file, `tests/test_code_map.py`. The implementer stashed its own changes, saw the failure persist, and reported it as pre-existing -- a true statement about its own diff and the wrong conclusion, because the module had been added by the previous gate's own commit, already underneath the stash. The same thing happened a second time when the driven crew extended the module.

### assertion:epic-559_c2-generate-the-spine-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Two cycles of diagnosis, one of them by a crew that then filed an incorrect attribution in its result, plus two map regenerations by the Commander.

### assertion:epic-559_c2-generate-the-spine-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: `python -m scripts.code_map build --root .` both times, and the Commander checked the crew's inference rather than accepting it, which is how the misattribution was caught.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
