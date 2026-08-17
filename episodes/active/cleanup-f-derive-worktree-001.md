<!-- episode-state: schema=1 id=cleanup-f-derive-worktree-001 status=active -->

# episode: cleanup-f-derive-worktree-001

## Mechanical
- run: cleanup-f-derive-worktree
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-f-derive-worktree/execute.json
- refusals: 9
- reopens: 0
- rework-count: 4
- failed-commands: 0
- artifact-ref: .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-reviewer-rework4-result.md
- artifact-ref: .agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-4.md

## Agent-supplied

### assertion:cleanup-f-derive-worktree-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Delete `_foreign_worktree`, a bad ownership test that answered 'is this spine mine' by comparing worktrees, and replace it at both call sites with binding-key provenance.

### assertion:cleanup-f-derive-worktree-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Replacing one predicate with a better one at two call sites was scoped as a single gate: the risk was thought to live in the replacement being wrong, so the plan's checks all asked whether the new predicate decided correctly.

### assertion:cleanup-f-derive-worktree-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The gate cost five reviews and four reworks, and four of the five findings were not wrong decisions by the new predicate at all -- they were sessions arriving somewhere they had never previously reached. While the bad guard stood it was also, incidentally, keeping a whole class of session out of `decide_session_start`'s fall-through; deleting it widened the population reaching code nobody had re-examined. B4 was a withholding that fell through into the scan-bind, B5 was a second route into the same writer, B6 was the render half of a rule that had been shipped for the write half only.

### assertion:cleanup-f-derive-worktree-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Four rework cycles and five independent reviews, on a change whose final diff at the last rework was five lines. Every one of the four findings was measured rather than read; not one was found by reading the diff.

### assertion:cleanup-f-derive-worktree-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The four rework cycles each began by enumerating the class of session the deleted guard had been keeping out of `decide_session_start`'s fall-through, and each finding fell out of that list rather than out of re-reading the replacement predicate. ADMIRAL_RULING-4 adopted the practice as a rule for later gates.

## Diagnosis (optional)

### assertion:cleanup-f-derive-worktree-001.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: A predicate has two effects: the decision it returns, and the paths it keeps callers away from. Review attention follows the first because that is what the diff shows; the second is invisible in a diff and is where a deletion's real blast radius lives.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
