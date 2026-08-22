<!-- episode-state: schema=1 id=w2-ledger-002 status=active -->

# episode: w2-ledger-002

## Mechanical
- run: w2-ledger
- project: constellation-skills
- role: commander
- spine-step: feedback
- context-manifest-ref: .agent-work/w2-ledger/STATE_NOTE.md
- refusals: 7
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/w2-ledger/crew-handoffs/g3-implement-implementer-result.md

## Agent-supplied

### assertion:w2-ledger-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: The g3-implement handoff asked for closeout to visibly render override-ledger activity, both through the immediate return of an engine closeout function and through the durable episode record produced by a separate validated-writer module.

### assertion:w2-ledger-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: Wiring a new mechanical field into the episode-authoring allowlist and validator, and into the closeout function's return dict, was expected to make the override activity visible at both the immediate and durable layers.

### assertion:w2-ledger-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The first implementer attempt wired the new field into the allowlist, the validator, the mechanical-fields composer, and all four return points of the closeout function, and all of that passed its own tests. It then found, and reported as an out-of-scope observation rather than claiming full compliance, that the episode-writer module's own record-construction step never read the new field out of the validated input at all -- the value passed shape validation and was then silently discarded before ever reaching the persisted text on disk. The immediate-return half of the intent was fully met; the durable-record half was not, despite the underlying validation appearing to succeed.

### assertion:w2-ledger-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Had the implementer's self-report not distinguished "validates" from "persists," this gap could have shipped unnoticed: every test that checked mechanical-fields output or closeout's return dict passed, and only a test reading the actual bytes written to disk would have caught the missing persistence.

### assertion:w2-ledger-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The Commander ordered a bounded rework adding the missing field to the record's own data structure and its render/parse round-trip, with a new test that read the actual persisted file from disk rather than an in-memory object. The independently-dispatched reviewer for that gate reproduced the round-trip invariant itself from a standalone script rather than trusting the test names, and confirmed the fix.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
