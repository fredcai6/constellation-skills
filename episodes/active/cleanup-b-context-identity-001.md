<!-- episode-state: schema=1 id=cleanup-b-context-identity-001 status=active -->

# episode: cleanup-b-context-identity-001

## Mechanical
- run: cleanup-b-context-identity
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/cleanup-b-context-identity/execute.json
- refusals: 7
- reopens: 0
- rework-count: 0
- failed-commands: 5
- artifact-ref: .agent-work/cleanup-b-context-identity/ADMIRAL_RULING-2.md
- artifact-ref: .agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-handoff.md

## Agent-supplied

### assertion:cleanup-b-context-identity-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Dispatch the g1 reviewer against the already-written handoff, under a gate imperative frozen at plan time whose check (d) required that two distinct owners in one work directory BOTH write.

### assertion:cleanup-b-context-identity-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The frozen gate imperative and the governing Admiral ruling would agree, so the reviewer could be pointed at the gate's checks (a)-(i) as written.

### assertion:cleanup-b-context-identity-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: They disagreed: ADMIRAL_RULING-2.md was written after execute.json was frozen and amended R4's fourth row from write-every-candidate to skip-plus-sidecars, so check (d) demanded behaviour the Admiral had already ruled wrong, and a reviewer following it literally would have blocked the change for matching the ruling.

### assertion:cleanup-b-context-identity-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The hand-edit ban on execute.json is absolute and the gate could not be corrected in place, so the amendment was relayed through the reviewer handoff instead, costing an amendment section, an edit to the departure list, and a note that the superseded clause must not be raised as a finding.

### assertion:cleanup-b-context-identity-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The handoff is writable where the frozen gate is not, so it carried the amendment: it named the superseded clause explicitly, restated the two obligations the Admiral held to, and the reviewer verified the amended behaviour and recorded departure 1 as resolved rather than adjudicating it.

## Diagnosis (optional)

### assertion:cleanup-b-context-identity-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: A ruling can be amended after the plan that cites it is frozen, and the engine offers amend and reopen for changing gates but nothing for recording that a gate's own text has been superseded by a higher authority.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
