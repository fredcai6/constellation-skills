<!-- episode-state: schema=1 id=episode-guard-at-write-003 status=active -->

# episode: episode-guard-at-write-003

## Mechanical
- run: episode-guard-at-write
- project: constellation-skills
- role: commander
- spine-step: execute-g1-implement
- context-manifest-ref: ctx-egaw-g1-suite@54544404
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 1
- artifact-ref: map/INDEX.md

## Agent-supplied

### assertion:episode-guard-at-write-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Confirm the clean-env cache-clean full suite passed with 0 failed before treating execute's g1-implement c5 as satisfied.

### assertion:episode-guard-at-write-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The suite would pass cleanly on the first run, since the code changes (apply_episode_delta.py, the new test file, install_constellation.py) had already been implemented and reviewed by the Admiral before this run began.

### assertion:episode-guard-at-write-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first clean-env run found exactly one failure: MapTreeFreshnessTests, because map/INDEX.md had not been regenerated after the guard's code changes landed (81 modules, 4640 entities from a fresh build versus 80 modules, 4620 entities committed). A second clean-env run, after rebuilding the map, passed 3040 tests, 6 skipped, 1146 subtests, 0 failed.

### assertion:episode-guard-at-write-003.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: One extra full-suite run, about two minutes, plus one map rebuild; LAUNCH_ORDER-2 had already anticipated a map move, so the failure was expected in kind, only not yet resolved when this run started.

### assertion:episode-guard-at-write-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: This run rebuilt the map with the code_map builder and reran the identical clean-env suite command a second time, rather than accepting the first run's stale-map failure as final.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
