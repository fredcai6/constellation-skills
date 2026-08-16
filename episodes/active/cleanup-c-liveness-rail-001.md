<!-- episode-state: schema=1 id=cleanup-c-liveness-rail-001 status=active -->

# episode: cleanup-c-liveness-rail-001

## Mechanical
- run: cleanup-c-liveness-rail
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: none -- delegated commander run, no context manifest artifact this lane
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-c-liveness-rail/PLAN_CONVERGENCE.md
- artifact-ref: .agent-work/cleanup-c-liveness-rail/MISSION_FRAME.md

## Agent-supplied

### assertion:cleanup-c-liveness-rail-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a converged gate plan for #599 and #549 from two parallel candidate plans (smallest-diff, most-testable), then subject the convergence to a cold plan critic with no authoring context before cutting it into execute.json.

### assertion:cleanup-c-liveness-rail-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The cold critic would likely rubber-stamp a plan that already synthesized two independent candidates, since the harder design work was already done twice.

### assertion:cleanup-c-liveness-rail-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The cold critic found a real, previously-unflagged contradiction: the mission frame's own framing cited recover_crews.classify_entry as 'the closest existing precedent' for the pid-less liveness branch, but that precedent's pid=None mapping is the OPPOSITE of the fail-toward-active pre-ruling this run was bound to. It also found the converged plan named only two liveness buckets (pid-present, external-pidless) while a real, owned, must-pass test fixture (test_duplicate_active_lock_is_refused, no pid, no backend key) needed a third bucket the plan never named, plus a small arithmetic error in the heartbeat-window justification (2.29x reported as '>2.3x'). Both findings were verified true by reading the actual source and the actual test fixture, not asserted from the plan text alone.

### assertion:cleanup-c-liveness-rail-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Both findings were fixed in the plan document and folded into the execute.json gate imperative before any crew was dispatched. Had they survived to implementation, the precedent contradiction would likely have produced a #599 fix that silently violated its own governing pre-ruling for the pid-less/non-external case, and the missing third bucket would likely have broken an existing, must-pass test on first implementation attempt -- caught only at g1-integrate's test run, one full implement+review cycle later.

### assertion:cleanup-c-liveness-rail-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none -- the critic pass itself was the mechanism; no workaround was needed once the findings were triaged and folded back into the plan before cutting gates.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
