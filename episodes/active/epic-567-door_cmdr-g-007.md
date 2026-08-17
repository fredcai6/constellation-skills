<!-- episode-state: schema=1 id=epic-567-door_cmdr-g-007 status=active -->

# episode: epic-567-door_cmdr-g-007

## Mechanical
- run: epic-567-door/cmdr-g
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-567-door/cmdr-g/context/feedback.json
- refusals: 0
- reopens: 1
- rework-count: 0
- failed-commands: 2
- artifact-ref: PR #622
- artifact-ref: episodes/active/epic-567-door_cmdr-g-006.md

## Agent-supplied

### assertion:epic-567-door_cmdr-g-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Pushed the second CI-fix commit, which included a new episode recorded via apply_episode_delta.py, without locally running the episode-observation guard suite (tests/test_episode_observations.py) alongside the code-focused suite that had already been checked.

### assertion:epic-567-door_cmdr-g-007.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Since apply_episode_delta.py's own writer enforces schema validity at write time, the newly-created episode was assumed sufficient without a separate guard run.

### assertion:epic-567-door_cmdr-g-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The subsequent Windows CI run reported two new failures, both in the episode-observation guard suite, absent from the very first CI run for this PR. The guard's clause-opening-imperative heuristic flagged the word 'read' in the new episode's workaround statement, because that statement placed it as the first word of a comma-delimited clause -- a position the heuristic treats as a bare imperative regardless of the surrounding sentence's actual past tense. Separately, an earlier stray file write to a not-yet-existing work-area path caused a later git mv of that same directory to nest one level deeper than intended, silently, until the resulting spine.json path was checked by hand.

### assertion:epic-567-door_cmdr-g-007.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A third reopen-fix-rearchive cycle, plus a mid-cycle manual correction of the mis-nested directory (individually moving each real file, since git mv's directory-wildcard form refused on an interspersed untracked debris subdirectory).

### assertion:epic-567-door_cmdr-g-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Fixed the episode wording with the sanctioned restate-assertion write path rather than hand-editing the file under episodes/. Verified the corrected wording against the guard suite locally before pushing this time, rather than trusting the writer's own schema validation as sufficient. Verified the corrected directory layout by reading spine.json's own content (not just the absence of a git error) before trusting the move had landed where intended.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
