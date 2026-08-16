<!-- episode-state: schema=1 id=cleanup-a-door-002 status=active -->

# episode: cleanup-a-door-002

## Mechanical
- run: cleanup-a-door
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-a-door/execute.json
- refusals: 12
- reopens: 3
- rework-count: 3
- failed-commands: 4
- artifact-ref: .agent-work/cleanup-a-door/crew-handoffs/g3-rereview-result.md

## Agent-supplied

### assertion:cleanup-a-door-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Confirm no prose still asserted that spine_open re-reads SPINE_FILE fresh, after removing that read.

### assertion:cleanup-a-door-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: git grep -F 're-read fresh' across the tree would find every surviving instance of the phrase.

### assertion:cleanup-a-door-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The grep returned 0 files tree-wide while a whitespace-normalized sweep returned 1: the surviving instance is assembled from two adjacent string literals, '...re-read ' + 'fresh)...', so the phrase exists on no single line and a line-oriented tool cannot see it. It sat in a test's failure message, where a future debugger would have acted on it.

### assertion:cleanup-a-door-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One full review-and-rework round, and the miss happened inside the sweep that had just been added to enforce the blast-radius rule.

### assertion:cleanup-a-door-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The sweep was rewritten to parse AST string constants, which join implicit concatenation, together with comment runs, and to whitespace-collapse both before matching; the surviving instance then appeared.

## Diagnosis (optional)

### assertion:cleanup-a-door-002.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Implicit string concatenation makes a message's source text and its runtime value different strings; line-based search reads the source text.

### assertion:cleanup-a-door-002.d2
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: A message's source text and its runtime value are different strings once implicit concatenation is involved, and the line-based search read the source text.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
