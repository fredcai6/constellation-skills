<!-- episode-state: schema=1 id=epic-418-redux-013 status=active -->

# episode: epic-418-redux-013

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-redux-013.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Check whether a crew had written outside its assigned scope, by reading `git status` in its worktree.

### assertion:epic-418-redux-013.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A ` M` against a file a crew is forbidden to touch should mean the crew modified it.

### assertion:epic-418-redux-013.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Crew 1's worktree showed the Admiral's own transitions/close-to-w5/CURRENT_TRUTH.md and WAVE_REVIEW.md as ` M`. Both `git diff --numstat` and `git diff --ignore-cr-at-eol --numstat` returned completely empty -- zero content change. A verifier rewrites those files with LF, git normalises back to CRLF, and the stat cache reports them modified. The same signal recurred at closeout: the same two files showed ` M` again with no numstat line, and w5c4-engine/IMPLEMENTER_RESULT.md read as different under diff and identical under diff --strip-trailing-cr.

### assertion:epic-418-redux-013.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The first reading of this signal produced a false scope accusation against a crew and cost a retraction; a second was nearly sent on the same evidence. The crew that was accused is the one who diagnosed the cause. It also makes dirty-file count useless as a liveness proxy, since it moves without anyone writing anything.

### assertion:epic-418-redux-013.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Scope questions were re-derived from `git diff` and `git diff --numstat` rather than `git status`, and file-identity questions from `diff --strip-trailing-cr` rather than bare `diff`. At closeout this distinguished three real uncommitted engine-state changes in epic418-w5-docs, which were archived, from two phantom modifications, which were not.

## Diagnosis (optional)

### assertion:epic-418-redux-013.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A repo with CRLF normalisation and tools that write LF puts the stat cache and the content permanently out of step, so the cheapest status signal is also the one that reports changes that do not exist.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
