<!-- episode-state: schema=1 id=epic-418-redux-012 status=active -->

# episode: epic-418-redux-012

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/triage/templates/TRIAGE_RECOMMENDATION.template.md

## Agent-supplied

### assertion:epic-418-redux-012.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Re-read issues #439, #484 and #446 -- three separately filed defects against the same archive gate postcondition c2b -- against the fix that shipped in PR #516, to confirm the published accounts matched what was actually measured.

### assertion:epic-418-redux-012.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A published repro should exercise the command that shipped.

### assertion:epic-418-redux-012.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The shipped check text was `gh pr list --head <branch> ...` with no quotes. Both #439 and #484 published repros that quoted the placeholder -- `--head "<branch>"` and `--head '<branch>'`. Quoted, the shell passes the literal through and gh runs and returns an empty list. Unquoted, as shipped, the unquoted `<` is input redirection under sh -c: the shell tried to open a file named `branch`, exited 1, and gh was never invoked in any PR state. Measured across four fixtures -- no-PR, OPEN, MERGED, CLOSED-unmerged -- exit 1 every time. #446 claimed the gate 'accepts only an OPEN PR', read off the check text by eye; the gate accepted nothing. #484's own suggested fix measured exit 0 in all four states, which would have converted a check that cannot pass into one that cannot fail.

### assertion:epic-418-redux-012.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Three issues reached the correct verdict by the wrong mechanism, and the wrong mechanism was the part a later reader would act on. An unresolved-placeholder bug would still have queried the forge and returned an honest empty list; a shell metacharacter never reaches the network at all. The issue that coined 'a check that cannot pass' for this repo carried the mirror defect as its own remedy.

### assertion:epic-418-redux-012.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each issue's original body was preserved as a comment and the body itself replaced with a corrected account, so the body stays correct rather than accumulating a mix of errors. The triage recommendation template was then reshaped so an issue records observations with baselines -- what's wrong, expected, conditions, type measured-or-inferred with how, and rev -- with possible fix demoted to an optional hypothesis and open questions beside it.

## Diagnosis (optional)

### assertion:epic-418-redux-012.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Nothing in the issue format asked how a claim was established, so an inferred claim and a measured one were written in the same voice. The three filings shared a verdict, which made the disagreement between their mechanisms invisible until the fix forced all three to be read against the same shipped text.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
