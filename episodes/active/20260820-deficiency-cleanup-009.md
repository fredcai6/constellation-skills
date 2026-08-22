<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-009 status=active -->

# episode: 20260820-deficiency-cleanup-009

## Mechanical
- run: 20260820-deficiency-cleanup
- project: constellation-skills
- role: admiral
- spine-step: closeout
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/20260820-deficiency-cleanup/architecture/C-VIABILITY.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Decide whether option C, demoting the lease from a claim to a presence marker, was viable.

### assertion:20260820-deficiency-cleanup-009.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The lease's record arms the Stop hook's anti-abandonment guard, so demoting it while keeping the record preserves the guard.

### assertion:20260820-deficiency-cleanup-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The guard is armed by the binding store, not by the lease record, and the binding store is written only by the observed act of claim or release. decide_stop returns {} when the binding view is empty and never scans spines. C preserves the record and removes the act, so the guard would have stayed exactly as inert as it already is. C was not broken, it was dominated: changing which verbs arm the binding is one predicate in one hook, touching zero refusal paths and zero spines on disk.

### assertion:20260820-deficiency-cleanup-009.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A design was almost adopted on a mechanism nobody had traced. The claim that the record arms the guard came from a subagent lane, was relayed to the human by the Admiral as the basis for keeping the lease, and was wrong in its mechanism though right in its conclusion.

### assertion:20260820-deficiency-cleanup-009.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The investigation was scoped to four questions with the deciding one named first, and it was told that an honest 'not viable, here is the single reason' was the most valuable outcome available.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
