<!-- episode-state: schema=1 id=commander-315-native-006 status=active -->

# episode: commander-315-native-006

## Mechanical
- run: commander-315-native
- project: constellation-skills
- role: implementer
- spine-step: g1-implement
- context-manifest-ref: .agent-work/commander-315-native/g1c-implement/IMPLEMENTER_PLAN.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 4
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1b-implementer-result.md
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1c-implementer-result.md
- artifact-ref: .agent-work/commander-315-native/crew-handoffs/g1c-reviewer-result.md

## Agent-supplied

### assertion:commander-315-native-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Apply bounded TDD and reversible review arms in the assigned sibling worktree using the mandated patch workflow.

### assertion:commander-315-native-006.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The apply_patch helper would operate in the delegated worktree and temporary directories available to the crew.

### assertion:commander-315-native-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Multiple implementer and reviewer patch-helper attempts failed during bwrap loopback setup for both the sibling worktree and temporary space, before any requested patch content was applied.

### assertion:commander-315-native-006.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: At least four failed patch invocations across crews, plus extra byte-hash verification and temporary-copy handling for every deliberate-breakage arm.

### assertion:commander-315-native-006.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Crews applied bounded reversible git patches and verified pre/post SHA-256 equality; the Commander later used an escalated interactive apply_patch process rooted in the delegated worktree.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
