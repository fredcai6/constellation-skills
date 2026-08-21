<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-002 status=active -->

# episode: 20260820-deficiency-cleanup-002

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
- artifact-ref: .agent-work/20260820-deficiency-cleanup/evidence/CHANNEL-EXPERIMENT.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Determine whether the lineage edge naming which run dispatched which is written anywhere durable, as evidence for the architecture cluster.

### assertion:20260820-deficiency-cleanup-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: spine_lifecycle.build_origin takes a parent argument and writes it into the spine's origin block, so a plan records who dispatched it.

### assertion:20260820-deficiency-cleanup-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Of 40 plans on disk carrying an origin block, ZERO carry origin.parent -- all have the three-key init_work_area shape. A dispatch through run_crew --backend cli, the channel purpose-built for it with a real parent, still produced parent: null in the registry and no parent key in origin. build_origin's own docstring calls the block PROVENANCE and nothing else, read by nothing that decides anything.

### assertion:20260820-deficiency-cleanup-002.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: A field exists, is documented, and is never populated, so any design reaching for it as a carrier is reaching for something empty. Three independent architecture lanes proposed building lineage identity as new architecture without checking that the slot was already there and unfilled.

### assertion:20260820-deficiency-cleanup-002.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: The carrier actually relied on was crew-runs.json parent, populated on 172 of 545 entries and already read and gate-enforced by verify_declared_dispatch.py. Recorded rather than filed, per human ruling of 2026-08-21.

## Diagnosis (optional)

### assertion:20260820-deficiency-cleanup-002.d1
- kind: proposed-remedy
- strength: medium
- lifecycle-standing: active
- statement: The remedy taken was removing --parent's optionality on the carrier that is actually read, rather than writing a second edge into origin. That change shipped in this epic's A+B batch.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
