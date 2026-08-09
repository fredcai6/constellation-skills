<!-- episode-state: schema=1 id=w5-gates-008 status=active -->

# episode: w5-gates-008

## Mechanical
- run: w5-gates
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/w5-gates/context/g3-review.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w5-gates/crew-handoffs/g3-review-RESULT.md

## Agent-supplied

### assertion:w5-gates-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Verify commit scope at review against the handoff's scope assertion.

### assertion:w5-gates-008.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The handoff's statement about which paths are tracked would match the repository.

### assertion:w5-gates-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The g2 and g3 review handoffs both stated that everything under `.agent-work/` is local-only and correctly absent from the tracked diff. It is tracked here: the g2 commit carries nine tracked `.agent-work/w5-gates/` files, and the g3 numstat range showed twelve paths rather than two because the range spanned two intermediate Commander commits.

### assertion:w5-gates-008.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The g3 reviewer nearly raised a false scope alarm and had to read git history to resolve the contradiction. The g2 reviewer met the same contradiction while under an explicit instruction to flag any tracked file outside the named pair.

### assertion:w5-gates-008.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Both reviewers ran `git show` against the named commit instead of trusting the range, and reported the wording error in their RESULT.

## Diagnosis (optional)

### assertion:w5-gates-008.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A scope assertion phrased about a commit range answers a different question than one phrased about a single commit, and the handoff text carried the convention from a repository where `.agent-work/` is untracked.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
