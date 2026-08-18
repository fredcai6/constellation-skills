<!-- episode-state: schema=1 id=epic-567-door-023 status=active -->

# episode: epic-567-door-023

## Mechanical
- run: epic-567-door
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 1
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-567-door/ADMIRAL_LOG.md
- artifact-ref: .agent-work/epic-567-door/EPIC_SUMMARY.md

## Agent-supplied

### assertion:epic-567-door-023.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: A declaration form chosen for the bookend freeze, with the human picking per-gate flags over a single declared region.

### assertion:epic-567-door-023.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The chosen form's silent-permissive failure mode would surface eventually, mitigated by a lint.

### assertion:epic-567-door-023.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It surfaced within minutes of the merge, on the first spine minted afterwards. init_work_area.py mints from the installed corpus, which predated the merge, so the repo carried two declarations and the installed copy carried none -- and the new spine came out undeclared with nothing saying so. The freeze protects nothing until the corpus is reinstalled.

### assertion:epic-567-door-023.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: No run was harmed, but the mechanism was inert at the moment it was believed to be protecting runs, and only an unrelated check caught it.

### assertion:epic-567-door-023.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The lint was promoted from a deferred candidate to part of the same wave, and scoped to catch repo-versus-installed drift as well as a missing declaration, because the second is how the first happens.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
