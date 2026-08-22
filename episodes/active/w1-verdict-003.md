<!-- episode-state: schema=1 id=w1-verdict-003 status=active -->

# episode: w1-verdict-003

## Mechanical
- run: w1-verdict
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: ctx-w1-verdict-feedback@55fc16f58a273e3cdea1943150efebcec8e3482f
- refusals: 10
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w1-verdict/map-orientation.json

## Agent-supplied

### assertion:w1-verdict-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: This run's context step ran map_orient.py orient against this repo's own map/ and docs/architecture/ before any source reading, per the shipped spine template's imperative.

### assertion:w1-verdict-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: map/INDEX.md exists and lists real packet-style entries (e.g. scripts.checklist_engine, scripts.validate_spine), so a RESOLVED orientation seemed plausible.

### assertion:w1-verdict-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: map_orient.py returned DEGRADED-UNPARSEABLE: map/INDEX.md's own listed packet directories (map/scripts.checklist_engine/, map/scripts.validate_spine/) do not exist anywhere under map/ (only INDEX.md and an empty ids.jsonl are present), and docs/architecture/generated/map.json parses but carries zero nodes[].id. Independently, tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build fails at this exact commit (244665ee) for the same underlying reason -- map/INDEX.md is stale against a fresh scripts.code_map build -- and that failure was reproduced three times in this run (by the implementer, the reviewer, and this Commander, each independently via git stash + rerun).

### assertion:w1-verdict-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: This run's mission frame, plan-alternatives, and every crew handoff had to be written against source-line pointers and docs substitutes instead of map: node ids -- workable for a small, fully-specified mechanism change, but the map gave zero navigation value for the entire run despite existing and looking populated at a glance.

### assertion:w1-verdict-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Discharged the DEGRADED verdict via map_orient.py's own --substitute/--unmapped/--escalation flags, citing docs/CHECKLIST_SCHEMA.md, docs/CHECKLIST_ENGINE_DESIGN.md, and the two target source files as substitutes; carried the finding forward into REPLAN_INPUT.json as an evidence_only discrepancy for the Admiral/Cartographer reconcile step rather than fixing the map in-mission (out of this mission's scope).

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
