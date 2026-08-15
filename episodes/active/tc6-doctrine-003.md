<!-- episode-state: schema=1 id=tc6-doctrine-003 status=active -->

# episode: tc6-doctrine-003

## Mechanical
- run: tc6-doctrine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/tc6-doctrine/execute.json
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/tc6-doctrine/amend-g1-c4.json

## Agent-supplied

### assertion:tc6-doctrine-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a falsifiable command postcondition on execute.json gate g1 asserting the unforgeability-withdrawal sentence in docs/CHECKLIST_SCHEMA.md survived the rewrite unchanged, via a literal grep for its text.

### assertion:tc6-doctrine-003.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The grep pattern 'does not make the comparison unforgeable' was expected to match the sentence as it stood in the document.

### assertion:tc6-doctrine-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: advance g1 refused on postcondition c4. The document's actual wording bolds the word 'not' in Markdown ('does **not** make...'), so the literal asterisks broke the plain substring match even though the sentence itself was present and unchanged from before the rewrite.

### assertion:tc6-doctrine-003.a4
- kind: impact-cost
- strength: weak
- lifecycle-standing: active
- statement: One refused advance call and one amend round-trip; no document content was wrong, only the check text that verified it.

### assertion:tc6-doctrine-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Corrected via the engine's own amend --delta retext-check op, which requires a reason and authority and leaves an audit entry, rather than hand-editing execute.json's check text directly.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
