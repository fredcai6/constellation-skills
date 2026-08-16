<!-- episode-state: schema=1 id=cleanup-g-crew-tier-001 status=active -->

# episode: cleanup-g-crew-tier-001

## Mechanical
- run: cleanup-g-crew-tier
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: none -- delegated commander run, no context manifest artifact this lane
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-g-crew-tier/PLAN_CONVERGENCE.md
- artifact-ref: .agent-work/cleanup-g-crew-tier/PLAN_CRITIC_FINDINGS.md
- artifact-ref: .agent-work/cleanup-g-crew-tier/execute.json

## Agent-supplied

### assertion:cleanup-g-crew-tier-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run plan-alternatives (two candidates under distinct constraints) and a cold plan critic against the converged plan for #611, before cutting execute.json's gates.

### assertion:cleanup-g-crew-tier-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The two independently-authored candidates would likely converge on the same refusal seam and scoping, since both were told to read the same source and the mission's pre-rulings were already narrow -- the value of the exercise would be mostly in test-decomposition detail, not seam disagreement.

### assertion:cleanup-g-crew-tier-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both candidates independently converged on the exact same seam (CrewSpec.__post_init__, not build_crew_argv, not argparse required=True) and the exact same resume/bare-abandon exemption reasoning, without having seen each other's work -- strong corroboration of that specific design choice. Where they genuinely differed was gate granularity (2 gates vs 6), and Candidate B surfaced a real unresolved fork the mission's pre-rulings never named: main()'s abandon+relaunch branch has no model-inherit-fallback today, asymmetric with reasoning_effort's existing fallback, and either behavior was equally testable -- this needed an explicit Commander ruling, not just synthesis. The cold critic separately found the converged plan never operationalized the mission's own named 'trap' (naming a tier for every crew the Commander itself dispatches) anywhere in execute.json's gate imperatives, and that g1-integrate's own test-command postcondition was missing the mandatory cache-clear step g3-verify already had.

### assertion:cleanup-g-crew-tier-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The relaunch-semantics fork, if left unresolved, would have been silently decided by whichever way the implementer happened to write the guard clause, with no record of it being a deliberate choice. The missing-trap gap, if it had survived to execution, risked the exact failure mode the mission's own 'trap' section warns about by name: a Commander reproducing the tierless-dispatch defect inside its own fix. Both were fixed in the plan/execute.json before any crew was dispatched.

### assertion:cleanup-g-crew-tier-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none -- ruled the relaunch fork directly (relaunch requires explicit --model, no inherit fallback, matching the mission's 'never inherited' wording) and added explicit --model reminders to g1-implement/g1-review's imperatives before opening either gate.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
