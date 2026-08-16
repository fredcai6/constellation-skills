<!-- episode-state: schema=1 id=cleanup-g-crew-tier-002 status=active -->

# episode: cleanup-g-crew-tier-002

## Mechanical
- run: cleanup-g-crew-tier
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: none
- refusals: 8
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/cleanup-g-crew-tier/spine.json
- artifact-ref: .agent-work/cleanup-g-crew-tier/execute.json

## Agent-supplied

### assertion:cleanup-g-crew-tier-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Drive execute.json's gates through the CLI engine (the MCP door stays bound to the top-level spine, which a child checklist is not), each gate's command-checked postconditions run for real, not attested.

### assertion:cleanup-g-crew-tier-002.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: The gate's own test-command postcondition, authored at plan time from a correct mental model of the launch order's clean-env recipe, would just pass once the implementer's code was correct.

### assertion:cleanup-g-crew-tier-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: g1-integrate's command postcondition (tests/test_crew_launcher.py, cache cleared) failed on a correct, reviewer-APPROVEd implementation, because the check's own environment -- this Commander's OWN CREW_SCRATCH_DIR, bound because the Commander is itself a live crew -- leaked into a fake-child-env assertion the implementer's change never touched. Independently confirmed by both the implementer and reviewer via git-stash-on-baseline (fails identically pre-change) before I found the actual mechanism: unsetting CREW_SCRATCH_DIR alongside the launch order's existing SPINE_FILE/SPINE_SESSION/SPINE_PARENT unset made the same command pass clean (212/212). The scratch-clone main-baseline remeasurement hit an analogous but distinct self-inflicted false failure: a clone directory named /tmp/g3-main-baseline (not 'constellation-skills') made the generated map/INDEX.md's own header text disagree with the committed one, reading as a real staleness regression.

### assertion:cleanup-g-crew-tier-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Both were false failures that would have blocked a genuinely correct, reviewed change from closing its gate, or produced a false positive in a failure-set-difference comparison against main. The gate-plan fix (g1-integrate) required a formal amend (retext-check) rather than a silent JSON edit, since execute.json's postcondition text is engine-owned once authored; the baseline fix required simply re-cloning into a correctly-named directory. Neither is a code defect in this mission's own change -- both are measurement-environment defects a Commander's own process state can introduce.

### assertion:cleanup-g-crew-tier-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: g1-integrate.c1's check command amended via the engine's amend/retext-check verb (authority human, reason recorded) to also unset CREW_SCRATCH_DIR. The main-baseline scratch clone was redone into a directory literally named constellation-skills.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
