<!-- episode-state: schema=1 id=crew-verdict-and-door-003 status=active -->

# episode: crew-verdict-and-door-003

## Mechanical
- run: crew-verdict-and-door
- project: constellation-skills
- role: commander
- spine-step: context
- context-manifest-ref: .agent-work/crew-verdict-and-door/map-orientation.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/crew-verdict-and-door/map-orientation.json

## Agent-supplied

### assertion:crew-verdict-and-door-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Resolve map orientation before reading any source, per the context step's map-first imperative, for a repo (constellation-skills) that maintains its own derived code map under map/.

### assertion:crew-verdict-and-door-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A repo that runs `python -m scripts.code_map build` as part of its own test suite would have a populated map/ids.jsonl, since the tool exists specifically to produce citable structure.

### assertion:crew-verdict-and-door-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: map/ids.jsonl was empty (0 entries), and a fresh `python -m scripts.code_map build --root .` still reported "ids": 0 in its own summary -- this is a repo-wide, structural characteristic, not staleness fixable by rebuilding, and every map_orient.py orientation in this repo currently reads DEGRADED-UNPARSEABLE as a result.

### assertion:crew-verdict-and-door-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Discharged the DEGRADED verdict via declared substitutes (README.md, docs/CHECKLIST_ENGINE_DESIGN.md, docs/agents/CREW_CONTEXT.md) and a recorded escalation, costing one extra orient/verify-orientation round-trip; the mission frame then had to avoid all anchor-shaped tokens (word:id syntax) entirely, since any such token in a DEGRADED-mode frame is treated as an unresolvable citation attempt and fails c6, which was not obvious on first pass and cost one failed verify-frame plus a rewrite.

### assertion:crew-verdict-and-door-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Rewrote the mission frame's constraint/decision/claim sections to avoid the `word:id` anchor pattern entirely (e.g. "Ruling task-1-is-the-lane" instead of "decision:task-1-is-the-lane"), keeping only the declared substitute file paths as literal citations, which made verify-frame pass (FRAME-OK, 0 problems).

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
