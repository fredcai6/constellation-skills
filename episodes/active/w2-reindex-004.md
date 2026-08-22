<!-- episode-state: schema=1 id=w2-reindex-004 status=active -->

# episode: w2-reindex-004

## Mechanical
- run: w2-reindex
- project: constellation-skills
- role: commander
- spine-step: execute:g3-implement
- context-manifest-ref: none -- no context_manifest.py invocation recorded this session
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: map/INDEX.md
- artifact-ref: g3-implement-handoff-relaunch2.md

## Agent-supplied

### assertion:w2-reindex-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: g3's end-to-end proof gate's own full-suite regression check was meant to confirm gates 1-2's shipped mechanism caused no suite regression.

### assertion:w2-reindex-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The full suite would go straight to green once the end-to-end test file itself passed, since gates 1-2 had each already run and reported their own targeted suites green.

### assertion:w2-reindex-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The full suite reported 1 failed (tests/test_code_map.py::MapTreeFreshnessTests) even though every gate 1-3 test passed. Root-caused by the g3-implement crew (attempt-2): this repo's own map/INDEX.md had gone stale from gate 2's own tracked-file edits to scripts/install_constellation.py and tests/test_install_constellation.py, never rebuilt, because nothing in this branch's own history had committed a real git commit yet -- the very mechanism this mission built would have caught it, but only fires on a real commit, and gates 1-2 landed as uncommitted working-tree edits. Neither gate 1 nor gate 2's own required evidence had included a full-suite run, only their own targeted test files, so this gap was invisible until g3's broader regression check reached it.

### assertion:w2-reindex-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One mechanical fix (python -m scripts.code_map build --root ., 6 lines changed) plus one additional short re-verification crew dispatch (attempt-3) to confirm the full suite green afterward, rather than a real defect in gates 1-2's shipped code.

### assertion:w2-reindex-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The Commander ran the rebuild directly (a mechanical step explicitly authorized by this repo's own docs/agents/AGENT_GUIDE.md build instructions), then dispatched a short pure-verification relaunch to confirm the full suite green with a real crew's own evidence rather than trusting the Commander's own in-session claim.

## Diagnosis (optional)

### assertion:w2-reindex-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: This is the mission's own subject matter recurring inside its own execution: a stale map going undetected until a broad-enough check ran, exactly the class of problem the launch order's whole mission exists to close, surfaced here only because the new hook could not yet fire (no real commit had landed on this branch).

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
