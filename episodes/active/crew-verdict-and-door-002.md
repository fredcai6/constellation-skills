<!-- episode-state: schema=1 id=crew-verdict-and-door-002 status=active -->

# episode: crew-verdict-and-door-002

## Mechanical
- run: crew-verdict-and-door
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/crew-verdict-and-door/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 2

## Agent-supplied

### assertion:crew-verdict-and-door-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run the full cache-clean test suite as g1-integrate's closeout postcondition and compare against the launch order's stated 453f8492 baseline (3002 passed, 7 skipped, 0 failed, 1130 subtests).

### assertion:crew-verdict-and-door-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A cache-clean suite run with only the diff's own additive changes applied would show 0 failed, matching the baseline's failure count exactly.

### assertion:crew-verdict-and-door-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The suite reported 2 failed: the expected map-staleness test (fixable by regenerating the map, already anticipated) and tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ, which asserts SPINE_FILE/SPINE_SESSION are absent from os.environ -- an assertion that is false inside THIS commander's own shell, because this dispatch was itself launched via run_crew.py's cli backend with --spine, which legitimately binds those vars into the shell before pytest ever starts. Running the same single test with the three SPINE_* vars unset passed cleanly.

### assertion:crew-verdict-and-door-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Cost one extra full-suite run (~2 minutes) plus a targeted single-test reproduction to distinguish a genuine regression from an artifact of the commander's own door-binding, before concluding the second failure was unrelated to this run's diff.

### assertion:crew-verdict-and-door-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Used the engine's own retext-check amend op (authority=commander, reason recorded on the checklist) to change g1-integrate's and g2-integrate's suite-check commands to run pytest with SPINE_FILE/SPINE_SESSION/SPINE_PARENT explicitly unset, reproducing the environment the baseline was almost certainly measured in rather than one contaminated by this run's own bound door.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
