<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-006 status=active -->

# episode: 20260820-deficiency-cleanup-006

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
- artifact-ref: .agent-work/20260820-deficiency-cleanup/architecture/CRITIC_COMPARISON.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-006.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Find what the epic's defect cluster actually amounted to on current code.

### assertion:20260820-deficiency-cleanup-006.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The cluster is about ownership and authority, as the six issues describe it.

### assertion:20260820-deficiency-cleanup-006.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The load-bearing defect was a rendering omission. _is_stale existed, worked, and had four call sites, none of them in any rendering path, so current on a plan whose owner died 22 days ago printed LEASE active plus 'RAIL: A working solution is the MIDDLE of this run -- you are 7 steps from done. Next: the ACTIVE line above. Run it.' All 58 active leases in the checkout were stale. spine_rail.decide_session_start injected the same resume order at SessionStart, unasked, selecting on status == active with no staleness check anywhere in its path.

### assertion:20260820-deficiency-cleanup-006.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The system was not failing to warn an honest agent; it was instructing one into the mistake, in the imperative, with an encouraging progress count. Across this repository's history stale leases were reclaimed 0 times by plain claim and 25 times by --force, which is the cost of the lie expressed as behaviour.

### assertion:20260820-deficiency-cleanup-006.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The fix shipped as display and message changes with no new subsystem: current left RAIL_VERBS, archived plans gained a banner and lost the rail, the lease line renders HELD plus an age, and _scan_active_spine became staleness-gated.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
