<!-- episode-state: schema=1 id=epic-559_c2-generate-the-spine-003 status=active -->

# episode: epic-559_c2-generate-the-spine-003

## Mechanical
- run: epic-559/c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 1
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/dispatch-proof/spine.json
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/dispatch-proof/probe.spine.toml
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/COMMANDER_RETURN.md

## Agent-supplied

### assertion:epic-559_c2-generate-the-spine-003.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Author a `script`-kind check in the dispatch-proof spec that runs the generator over the reviewer spec in check-only mode, to prove the reviewer spec still generates after a probe change.

### assertion:epic-559_c2-generate-the-spine-003.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: The generator's script probe validates the check before emitting it, so an unusable check would be refused at generation time rather than reaching a driven spine.

### assertion:epic-559_c2-generate-the-spine-003.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: The check omitted `--out`, which argparse marks required=True unconditionally -- `--check-only` skips the WRITE step, not the CLI's own argument parsing. The generator emitted the check and `validate_spine.py` accepted the resulting spine. Run verbatim it exits 2 on `the following arguments are required: --out`, before any spec is opened, so it could never have passed. The probe checks that every flag an author NAMED exists in the target's add_argument literals; it has no view of a required flag the author FAILED to name. The defect was authored by the Commander who wrote the mission's own design note.

### assertion:epic-559_c2-generate-the-spine-003.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: The driven crew blocked its gate rather than completing the run, costing a resume, an amendment and a relaunch. It also changed the run's headline answer: the wrong-invocation class of defect is narrowed, not closed, and the report says so.

### assertion:epic-559_c2-generate-the-spine-003.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The crew blocked with the parent named; the Commander resumed the gate, repaired the check text through `amend --delta` with a single `retext-check` op under its own authority, and relaunched a fresh crew into the same job file, which drove it to terminal.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
