<!-- episode-state: schema=1 id=epic-418-followon-commander-424-004 status=active -->

# episode: epic-418-followon-commander-424-004

## Mechanical
- run: epic-418-followon-commander-424
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-followon/commander-424/crew-runs.json
- refusals: 3
- reopens: 0
- rework-count: 0
- failed-commands: 3
- artifact-ref: .agent-work/epic-418-followon/commander-424/triage-candidates/TRIAGE.md
- artifact-ref: .agent-work/epic-418-followon/commander-424/evidence/verify_replan_input.py

## Agent-supplied

### assertion:epic-418-followon-commander-424-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Use the standard Commander tooling for a run whose work id is 'epic-418-followon/commander-424' -- resolve completed crews with run_crew.py --verify-result, and satisfy the execute step's command postcondition with verify_iterative_role_artifacts.py.

### assertion:epic-418-followon-commander-424-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both tools accept the work id the epic/commander convention produces, which always contains a slash.

### assertion:epic-418-followon-commander-424-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both refused, for the same reason in different code. run_crew.py's load_registry_for_resume() takes session.split('/')[1] as the whole work id, so it looked for .agent-work/epic-418-followon/crew-runs.json and reported 'no crew recorded'. verify_iterative_role_artifacts.py guards the work id with SAFE_ID = ^[A-Za-z0-9][A-Za-z0-9._-]*$, which forbids a slash, and refused with 'work-id contains unsafe path characters' before reading any file. The predecessor had hit the first one silently: two completed g1 crews sat in the registry marked 'running' with their result artifacts already on disk.

### assertion:epic-418-followon-commander-424-004.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The registry misreported finished work as live across a handoff, which is the state a successor is told to resolve before dispatching. The second refusal was worse than an inconvenience: it fired before verification, and behind it sat a real defect -- the inherited REPLAN_INPUT.json had completed_outcomes as an array of strings where the G2 schema requires objects. That violation had been invisible for as long as the path guard fired first.

### assertion:epic-418-followon-commander-424-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: For run_crew.py, an untracked read-side symlink .agent-work/epic-418-followon/crew-runs.json pointing at commander-424/crew-runs.json, after which every --verify-result succeeded; writes were already correct because they use entry['work_id']. For the verifier, the execute step's command postcondition was retexted through the engine's amend verb to run the same verify_replan_input check on an explicit path, and the packet was repaired and verified. Both defects were routed as triage candidates rather than fixed, being outside the run's file fence.

## Diagnosis (optional)

### assertion:epic-418-followon-commander-424-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Two independent tools encode the same assumption that a work id is a single path segment, while the epic/commander convention always nests one. In run_crew.py the read and write paths disagree with each other, which is why the failure presents as a confusing 'no crew recorded' rather than an obvious refusal.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
