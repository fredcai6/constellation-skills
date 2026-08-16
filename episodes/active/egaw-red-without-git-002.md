<!-- episode-state: schema=1 id=egaw-red-without-git-002 status=active -->

# episode: egaw-red-without-git-002

## Mechanical
- run: egaw-red-without-git
- project: constellation-skills
- role: commander
- spine-step: g1-integrate
- context-manifest-ref: .agent-work/egaw-red-without-git/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 1

## Agent-supplied

### assertion:egaw-red-without-git-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Confirmed the full clean-env suite stayed at zero failures after the one intended test-file change.

### assertion:egaw-red-without-git-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The suite would report the same pass/skip/subtest counts as the pre-change baseline named in LAUNCH_ORDER.md, with the one rewritten test method as the only difference.

### assertion:egaw-red-without-git-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first clean-env run surfaced one unrelated failure: MapTreeFreshnessTests found the tracked map/INDEX.md stale, because removing three symbols (PRE_CHANGE_REV, a helper function, and another function) from the edited test file changed the repository's real entity count. Regenerating the derived map via the command the failing assertion itself named touched only map/INDEX.md, three lines, and the suite then matched the baseline exactly.

### assertion:egaw-red-without-git-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: One extra clean-env suite run plus one map-regeneration command; no code change was needed.

### assertion:egaw-red-without-git-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: none — the failing test named its own fix command directly, so no improvisation was needed.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
