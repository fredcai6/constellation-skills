<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-003 status=active -->

# episode: cleanup-f-derive-worktree-003

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-f-derive-worktree/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/cleanup-f-derive-worktree/REPLAN_INPUT.json

## Agent-supplied

### assertion:cleanup-f-derive-worktree-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Re-measure the full suite in the worktree at the integrate gate, in my own hands, rather than citing the previous leg's numbers.

### assertion:cleanup-f-derive-worktree-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The same command on the same commit would reproduce the previous leg's green result, 3192 passed / 5 skipped / 0 failed.

### assertion:cleanup-f-derive-worktree-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It reported 1 failed: `test_containment_repo_agent_work_untouched_by_the_chain`, whose diff was exactly two files -- `gauge.json` and the per-owner gauge -- under the live `.agent-work/`. That test snapshots `.agent-work/` by size and mtime, and every tool call an agent makes fires the gauge chain, which writes there. I had backgrounded the run and polled it about fifteen times, so the tree the test was snapshotting was moving because I was watching it. The identical command run quiet by the engine's own postcondition was green.

### assertion:cleanup-f-derive-worktree-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One 128-second suite run wasted, and a red that was indistinguishable from a regression at a gate whose postcondition is a green suite. The same test cost an earlier reviewer on this lane a full run and a false red for the same underlying reason.

### assertion:cleanup-f-derive-worktree-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The engine's own postcondition re-ran the identical command with no agent tool calls in flight, and it was green; that quiet run became the number of record, and the noisy one was recorded as an instrument defect rather than a regression.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-003.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A test that asserts over live agent-workspace state measures its observer, not just its subject. Recorded as a triage candidate rather than fixed here: the repair is to exclude the current run's work-id subtree or the gauge files, and it belongs to whoever owns that test.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
