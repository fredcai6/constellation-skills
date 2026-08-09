<!-- episode-state: schema=1 id=issue-458-readiness-005 status=active -->

# episode: issue-458-readiness-005

## Mechanical
- run: issue-458-readiness
- project: constellation-skills
- role: reviewer
- spine-step: execute
- context-manifest-ref: .agent-work/issue-458-readiness/context/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/issue-458-readiness/g1-review/review.json

## Agent-supplied

### assertion:issue-458-readiness-005.a1
- kind: task-intent
- strength: medium
- lifecycle-standing: active
- statement: Run the r6-fowler item of REVIEW_SURVEY.template.json, invoking the check command its postcondition names.

### assertion:issue-458-readiness-005.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: The r6-fowler item's imperative prose and its postcondition c1 name the same check-command path.

### assertion:issue-458-readiness-005.a3
- kind: observed-behavior
- strength: medium
- lifecycle-standing: active
- statement: The imperative prose ships with 'templates/FOWLER_PASS.template.json' as its literal check-command path, while postcondition c1 (the thing advance/record actually gates on) already carries the real resolved instance path filled in at instantiation. The documented normal path worked cleanly once the instance path was substituted; the wording of the two only disagrees, it does not disagree in behavior.

### assertion:issue-458-readiness-005.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: A less careful reader could stumble trying to run the imperative's literal template path directly instead of the resolved instance path.

### assertion:issue-458-readiness-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: None needed -- substituted the resolved instance path from postcondition c1 and proceeded.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
