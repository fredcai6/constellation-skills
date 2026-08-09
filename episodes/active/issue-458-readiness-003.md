<!-- episode-state: schema=1 id=issue-458-readiness-003 status=active -->

# episode: issue-458-readiness-003

## Mechanical
- run: issue-458-readiness
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/issue-458-readiness/context/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/issue-458-readiness/REPLAN_INPUT.json

## Agent-supplied

### assertion:issue-458-readiness-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Satisfy execute.c2, which runs 'python scripts/verify_iterative_role_artifacts.py commander --work-id issue-458-readiness' to confirm REPLAN_INPUT.json is a valid G2 input.

### assertion:issue-458-readiness-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The repo's own vendored scripts/verify_iterative_role_artifacts.py, run against a correct REPLAN_INPUT.json, exits 0.

### assertion:issue-458-readiness-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The repo-vendored command always refuses with 'role verifier must run from an installed constellation-* skill' regardless of REPLAN_INPUT.json's content, because verify_iterative_role_artifacts.py's _installed_skills_root() guard checks that Path(__file__).resolve().parents[1].name starts with 'constellation-', which a worktree's own scripts/ directory never satisfies. Running the identical artifact through the INSTALLED copy at ~/.claude/skills/constellation-commander/scripts/verify_iterative_role_artifacts.py passed clean ('iterative role artifact ok'), confirming the artifact was correct and the guard was the only obstacle.

### assertion:issue-458-readiness-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: execute.c2 cannot pass for any Commander spine dogfooded on this repo's own worktree -- a structural property of the check, not a defect in any one run's REPLAN_INPUT.json. Independently re-derives crew 1's own report this same wave against #501/#468, which predicted exactly this would hit a Commander.

### assertion:issue-458-readiness-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Waived execute.c2 (FORCED) on the Admiral's authority, citing both commands' exact output verbatim in the waiver reason, after floating the finding rather than force-waiving unilaterally.

## Diagnosis (optional)

### assertion:issue-458-readiness-003.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: verify_iterative_role_artifacts.py's _installed_skills_root() guard assumes it is always invoked from an installed skill bundle (it dynamically loads sibling installed verifiers by relative path from the skills root), which is true for a normal project consuming Constellation but false when Constellation's own source repo dogfoods its own Commander spine against its own vendored scripts/.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
