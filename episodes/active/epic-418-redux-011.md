<!-- episode-state: schema=1 id=epic-418-redux-011 status=active -->

# episode: epic-418-redux-011

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 3
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-redux-011.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Have a reviewer subagent record an approving verdict on a crew's pull request through the forge, so the approval is visible on the PR rather than only in run notes.

### assertion:epic-418-redux-011.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: `gh pr review --approve` should record the reviewer's verdict on the pull request.

### assertion:epic-418-redux-011.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The forge refused with 'Can not approve your own pull request'. Every agent in this fleet authenticates as the same GitHub identity that authored the PR, so no agent can ever approve any agent's work. The refusal was read as reviewer negligence three separate times -- most visibly on #470 -- before the identity cause was established.

### assertion:epic-418-redux-011.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: A structural impossibility presented as a behavioural failure, and it was attributed to the reviewer each time. Two of those readings produced corrective pressure aimed at an agent that had done nothing wrong.

### assertion:epic-418-redux-011.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Verdicts were recorded with `gh pr review <PR> --comment -F <file>`, verdict on the first line. Bodies were passed by file rather than as a double-quoted bash string, after a backticked code span in a body was executed as command substitution on #264 -- the comment posted anyway, silently missing that phrase, with every success signal intact.

## Diagnosis (optional)

### assertion:epic-418-redux-011.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: One credential shared by author and reviewer collapses a two-party forge check into a self-check. The forge is correct to refuse; the fleet's review evidence therefore cannot live in the approval channel at all.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
