<!-- episode-state: schema=1 id=epic-418-redux-009 status=active -->

# episode: epic-418-redux-009

## Mechanical
- run: epic-418-redux
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: .agent-work/epic-418-redux/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-418-redux/ADMIRAL_LOG.md

## Agent-supplied

### assertion:epic-418-redux-009.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive this epic's own spine while other checklists from earlier runs were present on disk in the same tracked directory tree.

### assertion:epic-418-redux-009.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A spine rail that fires at an agent should name work that agent is responsible for.

### assertion:epic-418-redux-009.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: 165 leases read `active` across the epic418-* worktrees, the oldest 289 hours old. Two rails fired at this Admiral within twenty minutes -- impl-w5-g3 at gate m3-coupled-suite and g4-implement-attempt-1 at gate m6-closure-check -- both naming gates for work already merged in PR #516. Because .agent-work/ is tracked, every unreleased lease from every finished run is committed and materialises in every worktree.

### assertion:epic-418-redux-009.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The population of stale bind targets is self-selecting in the wrong direction: releasing the lease is the last thing a healthy run does, so a trip-abandoned agent never releases, and the runs that fail are exactly the ones that leave a rail behind -- permanently, once committed. An agent that obeys one resumes a dead run's gate instead of its own.

### assertion:epic-418-redux-009.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Each rail was checked three ways before being declined -- whose lease it is, whether that work had merged, and what this run's own `current` says. Exactly two were released, both this run's own dead crew plans with death established first, gates left pending and satisfied null. The other 163 were left untouched as committed artifacts of other epics; the measurement was posted to #457.

## Diagnosis (optional)

### assertion:epic-418-redux-009.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: Lease state lives inside a tracked directory, so it is versioned and distributed like content rather than being per-checkout runtime state. Rewriting those files to quiet the signal would edit the instrument rather than the defect.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
