<!-- episode-state: schema=1 id=tc6-doctrine-002 status=active -->

# episode: tc6-doctrine-002

## Mechanical
- run: tc6-doctrine
- project: constellation-skills
- role: commander
- spine-step: context
- context-manifest-ref: .agent-work/tc6-doctrine/map-orientation.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/tc6-doctrine/map-orientation.json
- artifact-ref: .agent-work/tc6-doctrine/MISSION_FRAME.md

## Agent-supplied

### assertion:tc6-doctrine-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Orient map-first at the context step, before opening any source file, per inherited doctrine, for a repo with no docs/architecture packet map.

### assertion:tc6-doctrine-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: map_orient.py's fixed fallback probe order (generated-map, index, packets-dir, code-map-index, code-map-ids) was expected to resolve against at least one populated candidate.

### assertion:tc6-doctrine-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Every candidate came back absent or empty: no docs/architecture directory exists in this repo, and this repo's own derived code map (map/ids.jsonl) built to 0 citable ids even after a fresh python -m scripts.code_map build --root . run, with map/INDEX.md an unfilled landing-zone stub. Orientation returned DEGRADED-UNPARSEABLE and was discharged by declaring six repo files as substitutes; verify-orientation then confirmed the contract satisfied, and verify-frame confirmed the mission frame's citations resolved against those same declared substitutes.

### assertion:tc6-doctrine-002.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: About ten minutes spent reading the six substitute files directly in place of a map, plus one code-map rebuild that produced no new anchors.

### assertion:tc6-doctrine-002.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Declared substitutes via map_orient.py orient --substitute/--unmapped/--escalation rather than proceeding on an undischarged degraded verdict, matching the documented degraded path for a repo with no packet map.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
