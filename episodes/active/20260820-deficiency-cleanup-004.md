<!-- episode-state: schema=1 id=20260820-deficiency-cleanup-004 status=active -->

# episode: 20260820-deficiency-cleanup-004

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
- artifact-ref: .agent-work/20260820-deficiency-cleanup/evidence/LIVED-CLUSTER-EVIDENCE.md

## Agent-supplied

### assertion:20260820-deficiency-cleanup-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Give three architecture candidate lanes a shared evidence base by writing a dossier of what this epic had reproduced on current code.

### assertion:20260820-deficiency-cleanup-004.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The dossier records observations accurately, so three independent lanes reason from the same true ground.

### assertion:20260820-deficiency-cleanup-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: Three of its claims were wrong. E1 said no dispatched crew can be engine-railed; run_crew --backend cli assigns the child its own SPINE_FILE and SPINE_SESSION and its crews are fully railed. E3 said a stranded plan cannot be reclaimed from outside; a plain claim with no --force, an unrelated session id and worktree=/anywhere took one cleanly. E2 attributed the hazard to env-var inheritance; the dispatching shell had SPINE_FILE, SPINE_SESSION and SPINE_PARENT all unset, and the in-harness door binds through a session-keyed file instead. A fourth claim, that the lineage edge is empty on both channels, generalised from a single dispatch: 172 of 545 registry entries carry a real parent.

### assertion:20260820-deficiency-cleanup-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: All three candidate lanes were seeded from the wrong ground, and every one of them produced an authority design partly aimed at a hazard that was not there. Two lanes caught two of the errors unprompted; the experiment caught the third; a fourth lane caught the fourth.

### assertion:20260820-deficiency-cleanup-004.a5
- kind: workaround
- strength: medium
- lifecycle-standing: active
- statement: Corrections were appended to the dossier as they were found rather than the file being rewritten, so the record shows what the lanes were actually seeded with.

## Diagnosis (optional)

### assertion:20260820-deficiency-cleanup-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: Each wrong claim was asserted from reasoning about the system rather than from running it. E3 in particular was falsifiable in two commands and was not tested before being written down.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
