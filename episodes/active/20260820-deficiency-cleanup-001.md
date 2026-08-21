<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-001 status=active -->

# episode: 20260820-deficiency-cleanup-001

## Mechanical
- run: 20260820-deficiency-cleanup
- project: constellation-skills
- role: admiral
- spine-step: execute
- context-manifest-ref: none -- admiral run, no context manifest artifact
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/20260820-deficiency-cleanup/architecture/C-VIABILITY.md
- artifact-ref: .agent-work/20260820-deficiency-cleanup/evidence/CHANNEL-EXPERIMENT.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Establish whether spine_bind's R9 and R10 refusals protect against two agents landing on one derived identity, as part of deciding whether the lease should be demoted to a presence marker.

### assertion:20260820-deficiency-cleanup-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: R9 refuses a bind that would assume an identity already live somewhere else; R10 refuses a rebind while this door still holds a lease. Together they stop two doors driving one spine.

### assertion:20260820-deficiency-cleanup-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Both are gated on checklist_engine._active_lease being non-None, so on a spine with no active lease they return without refusing. Two doors can bind the same spine under the same derived identity today, with no refusal at any point. A crew dispatched through run_crew --backend cli was measured driving a full seven-gate plan with 0 claims and 0 releases, so leaseless is the normal state on the shipped path -- exactly the population where a collision is most likely.

### assertion:20260820-deficiency-cleanup-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: The guard is inert where it matters most and nobody had noticed. A subtraction lane in the same epic cited R9 as the one refusal in the corpus that prevents a nameable mistake, which is the opposite of what it does on the leaseless population.

### assertion:20260820-deficiency-cleanup-001.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: None applied. The human ruled on 2026-08-21 to record this rather than file it, to avoid growing the issue list while it is not markedly getting in the way.

## Diagnosis (optional)

### assertion:20260820-deficiency-cleanup-001.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: R9's liveness test IS the lease, and spine_bind leaves no durable trace to consult instead -- _bind_process_to sets process-local module globals only, and the binding file is written by the hook on claim/release. On a leaseless spine nothing in the system knows a door is bound.

### assertion:20260820-deficiency-cleanup-001.d2
- kind: proposed-remedy
- strength: weak
- lifecycle-standing: active
- statement: Adding a refusal on today's signal was rejected as worse than the silence: the signal is heartbeat-only at 1800s with no pid, and absent for 55 of 57 stale leases, so it would have misfired across a 718-plan leaseless population. Settling what live means is the prerequisite -- the same unresolved question that forced render-age-never-a-verdict on the display work.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
