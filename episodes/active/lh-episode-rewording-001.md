<!-- episode-state: schema=1 id=lh-episode-rewording-001 status=active -->

# episode: lh-episode-rewording-001

## Mechanical
- run: lh-episode-rewording
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/lh-episode-rewording/execute.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/lh-episode-rewording/execute.json

## Agent-supplied

### assertion:lh-episode-rewording-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Reword launcher-hygiene-001.a5, launcher-hygiene-002.a3, and launcher-hygiene-003.a5 so the episode-observation guard RealStoreTests passes, without shortening substance, touching the guard, or adding to its exception list.

### assertion:lh-episode-rewording-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Restating the three statements via apply_episode_delta.py restate-assertion op and re-running the full clean-env suite was expected to reach 0 failed directly.

### assertion:lh-episode-rewording-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: After the three restatements, the targeted guard test passed immediately, but the first full clean-env suite run failed test_canon_episode_store_untouched (previously passing) because the freshly restated episode files were tracked-but-unstaged; the test own docstring names the required order as write -> git add -> suite -> commit, which had not yet been followed.

### assertion:lh-episode-rewording-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One extra roughly two-minute suite run, backgrounded past the harness 120s foreground timeout and polled with TaskOutput block=true rather than ending the turn, after staging the three files with git add.

### assertion:lh-episode-rewording-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Staged episodes/active/launcher-hygiene-00{1,2,3}.md with git add before rerunning the full suite, matching test_canon_episode_store_untouched's documented write -> git add -> suite -> commit order; the suite then passed at 3031 passed / 6 skipped / 0 failed.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
