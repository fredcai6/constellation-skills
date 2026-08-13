<!-- episode-state: schema=1 id=commander-315-native-002 status=active -->

# episode: commander-315-native-002

## Mechanical
- run: commander-315-native
- project: constellation-skills
- role: reviewer
- spine-step: g1-review
- context-manifest-ref: .agent-work/commander-315-native/g1b-review/review.json
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 2
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1b-reviewer-result.md
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1c-reviewer-result.md

## Agent-supplied

### assertion:commander-315-native-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Independently verify that the ruled crew-cwd repair always supplies an absolute assigned worktree to dispatch and resume.

### assertion:commander-315-native-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The focused tests and the crew_cwd docstring's absolute-path contract would cover the real parser defaults as well as absolute temporary roots.

### assertion:commander-315-native-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: All original tests supplied an already-absolute temporary root, while the actual default pair root='.' and worktree='.' returned a relative Path; the first fresh reviewer blocked on that exact discrepancy.

### assertion:commander-315-native-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One bounded rework and a second independent review were required after an apparently green first repair; without the review probe the production default would have violated the claimed contract.

### assertion:commander-315-native-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The reviewer appended an explicit default-dot criterion; g1c added parser-default dispatch and resume tests, normalized root before joining, and a fresh reviewer approved the repaired boundary.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
