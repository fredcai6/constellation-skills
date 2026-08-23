<!-- episode-state: schema=1 id=w3-promote-002 status=active -->

# episode: w3-promote-002

## Mechanical
- run: w3-promote
- project: constellation-skills
- role: reviewer
- spine-step: g5-review
- context-manifest-ref: ctx-w3-promote-g5
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/charter/templates/CHARTER.template.json

## Agent-supplied

### assertion:w3-promote-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Independently red-proof the g5 CHARTER.template.json promotion by hand-mutating the shipped JSON and confirming the new test class genuinely fails, then restoring the original.

### assertion:w3-promote-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Running `git checkout -- <path>` after a self-authored mutation would undo only that mutation, returning the file to the state it carried immediately before the reviewer's own edit.

### assertion:w3-promote-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: `git checkout --` reverted the file all the way to pre-g5 HEAD instead, because the implementer's own promotion edit was itself still uncommitted -- there was no intermediate commit to return to. Caught immediately via `git diff` (the diff pointed the wrong direction), corrected by re-applying the implementer's exact line, and confirmed the restoration was byte-identical to the original diff before proceeding.

### assertion:w3-promote-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Self-caught within the same review pass, zero cost to schedule; the Commander independently re-verified the restored diff byte-identical and the suite still green before accepting the review result.

### assertion:w3-promote-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Restore via a saved copy or `git stash`/`git apply` instead of a bare `git checkout --` when mutation-testing an uncommitted diff, since the bare form resets to the last COMMIT, not to "the state before my last edit," whenever the target file already carries uncommitted changes.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
