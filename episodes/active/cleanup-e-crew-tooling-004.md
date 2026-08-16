<!-- episode-state: schema=1 id=cleanup-e-crew-tooling-004 status=active -->

# episode: cleanup-e-crew-tooling-004

## Mechanical
- run: cleanup-e-crew-tooling
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: none
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-implementer-result.md
- artifact-ref: .agent-work/cleanup-e-crew-tooling/crew-handoffs/g1-reviewer-result.md
- artifact-ref: .agent-work/cleanup-e-crew-tooling/crew-handoffs/g2-reviewer-result.md

## Agent-supplied

### assertion:cleanup-e-crew-tooling-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatched implementer and reviewer crews via run_crew.py --backend external (a headless claude CLI happened to exist on PATH, but crew-dispatch.md's Constellation Agent-tool harness guidance directs external + synchronous Agent-tool subagents), then independently re-verified every claimed result myself before integrating (diff scope, independent test re-runs, run_crew.py --verify-result) rather than trusting the returned IMPLEMENTER_RESULT/REVIEW_RESULT text at face value.

### assertion:cleanup-e-crew-tooling-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Expected reviewers to read the diff and the implementer's own claims and render a verdict from that.

### assertion:cleanup-e-crew-tooling-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both independent reviewers went further than reading the diff: each ran a live mutation test (temporarily removing the fix under review, confirming the specific tests written to catch it actually failed, then restoring and confirming a byte-identical diff) as the strongest available evidence that the new tests were not vacuous. Neither reviewer was explicitly instructed to do this by their handoff -- both reached it via the handoff's more general instruction to check whether any test 'passes vacuously'.

### assertion:cleanup-e-crew-tooling-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: This caught nothing wrong in either gate (both mutation tests confirmed the fixes and their tests were genuinely load-bearing), but it is exactly the check that would have caught #525's plan-time worktree-key gap had it survived to implementation, since a vacuous test on that specific regression would have passed review with no fix at all.

### assertion:cleanup-e-crew-tooling-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none -- both reviewers' g1-reviewer-result.md and g2-reviewer-result.md workflow-feedback sections independently suggested making an explicit sabotage-and-restore pass a standard requested step for concurrency/collision-correctness reviews specifically, since it was the single highest-signal check either of them ran.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
