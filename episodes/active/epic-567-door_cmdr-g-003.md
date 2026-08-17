<!-- episode-state: schema=1 id=epic-567-door_cmdr-g-003 status=active -->

# episode: epic-567-door_cmdr-g-003

## Mechanical
- run: epic-567-door/cmdr-g
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/epic-567-door/cmdr-g/context/feedback.json
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: RETURN.md

## Agent-supplied

### assertion:epic-567-door_cmdr-g-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Re-measured the #552 lease census against the current tree, per the launch order's pre-empted-steps invitation, rather than trusting the abad896d/2026-08-10 figures silently.

### assertion:epic-567-door_cmdr-g-003.a2
- kind: expected-behavior
- strength: weak
- lifecycle-standing: active
- statement: The figures might have improved somewhat given close_work/closeout_refusal (PR #564) had already landed on main since the original measurement.

### assertion:epic-567-door_cmdr-g-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: 52 active leases and 50 archived-but-still-active, both worse than the launch order's cited 43 and 17 -- the defect is measurably live and worsening, not stale, independent of this lane's own fix landing.

### assertion:epic-567-door_cmdr-g-003.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: None to this run directly; the number is load-bearing evidence for whoever next decides whether the 41 (now more) pre-existing stale leases warrant a dedicated sweep.

### assertion:epic-567-door_cmdr-g-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Wrote a small, explicitly read-only census script and ran it against the worktree's own .agent-work tree rather than reusing the launch order's stale numbers.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
