<!-- episode-state: schema=1 id=epic-418-redux-008 status=active -->

# episode: epic-418-redux-008

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: .agent-work/epic-418-redux/closeout/SWEEP_LIST.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-redux/closeout/harvest_probe.sh
- artifact-ref: .agent-work/archive/2026-08-09-epic-418-redux/harvest/HARVEST_RESULT.md

## Agent-supplied

### assertion:epic-418-redux-008.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Collect anything durable out of the seven epic worktrees before removing them, using the harvest probe's three channels -- uncommitted, on-this-branch-only, and ignored -- as the collection source.

### assertion:epic-418-redux-008.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A file the probe reports as on-this-branch-only should be content that removal would destroy, since that is the channel's stated purpose.

### assertion:epic-418-redux-008.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The probe reported roughly 240 branch-only files for epic418-w5-gates. Comparing the worktree against the main checkout by filename showed 241 of its 244 files already on main; the only three absent were two __pycache__ .pyc files and gauge.json. The single branch-only file reported for epic418-w5-engine, w5c4-engine/IMPLEMENTER_RESULT.md, was also already on main -- diff called the files different, diff --strip-trailing-cr returned zero lines.

### assertion:epic-418-redux-008.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The channel fails safe: over-reporting means declining to sweep, which is the recoverable direction, unlike the under-reporting that would silently destroy a run's learning. The cost was legibility -- one real signal was buried under 240 lines of noise, and the harvest had to be re-derived by content comparison before anything could be removed.

### assertion:epic-418-redux-008.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each reported line was re-checked by content rather than trusted: find | sort plus comm -23 between the worktree and the main checkout, and diff --strip-trailing-cr for the single-file case. The harvest verdict was recorded as a real null naming all three channels, and the only genuinely worktree-exclusive content -- three uncommitted engine-state files in epic418-w5-docs, confirmed as real changes under --ignore-cr-at-eol -- was archived before removal.

## Diagnosis (optional)

### assertion:epic-418-redux-008.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: harvest_probe.sh line 80 computes the channel as `git diff --name-only main...HEAD`. The three-dot form diffs against the merge base. PR #516 was squash-merged, so main's copy of those files arrived in a commit that is not an ancestor of the branch, the merge base stays at the old fork point, and every file the branch ever added still reads as branch-only. SWEEP_LIST.md opens by warning in prose that an ancestry test cannot distinguish merged from abandoned under squash-merge; the tool that list gates performs exactly that test in code.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
