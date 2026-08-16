<!-- episode-state: schema=1 id=cleanup-c-liveness-rail-003 status=active -->

# episode: cleanup-c-liveness-rail-003

## Mechanical
- run: cleanup-c-liveness-rail
- project: constellation-skills
- role: commander
- spine-step: g3-verify
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: map/INDEX.md
- artifact-ref: tests/test_code_map.py

## Agent-supplied

### assertion:cleanup-c-liveness-rail-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run the full clean-env suite at this lane's head and re-measure a main baseline at gate time, per the launch order's Return Shape and merge-gate requirements.

### assertion:cleanup-c-liveness-rail-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The main baseline, re-measured at a fresh worktree checked out at main's current tip, would be green (3057 passed / 0 failed per the launch order's Inherited Context, recorded at dispatch).

### assertion:cleanup-c-liveness-rail-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: This lane's own head suite failed once on map/INDEX.md staleness (map_tree_freshness) after g1+g2 added four new functions, changing the corpus's own entity count -- rebuilding and committing the map fixed it locally (590bf44d). Separately, re-measuring main at ITS current tip (43c577d4, which had moved from the a69bbac4 dispatch-time baseline because a sibling lane's work had already merged) showed the SAME map-staleness failure signature, independently, unrelated to anything this lane touched -- confirmed by tracing that main's own committed map/INDEX.md entity count did not match a fresh build of main's own tip.

### assertion:cleanup-c-liveness-rail-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The map-freshness check fired correctly both times it should have -- once for a genuine staleness this lane introduced (fixed before integrate closed) and once for a genuine staleness on main that this lane did not introduce and could not fix (outside its file ownership and worktree; recorded as a triage candidate instead). Distinguishing the two required checking out a disposable worktree at main's actual current tip rather than trusting the dispatch-time baseline number recorded in the launch order, since main had moved in the interim.

### assertion:cleanup-c-liveness-rail-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: For this lane's own staleness: ran `python -m scripts.code_map build --root .` and committed the regenerated map/INDEX.md. For main's staleness: none applied -- recorded as triage candidate tc3 and left for the Admiral, since it was outside this lane's file ownership and worktree.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
