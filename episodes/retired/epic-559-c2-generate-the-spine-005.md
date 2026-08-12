<!-- episode-state: schema=1 id=epic-559-c2-generate-the-spine-005 status=retired -->

# episode: epic-559-c2-generate-the-spine-005

## Mechanical
- run: epic-559-c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-runs.json
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/triage-candidates/RECOMMENDATIONS.md

## Agent-supplied

### assertion:epic-559-c2-generate-the-spine-005.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Run the crew-recovery check before each dispatch, as doctrine requires, to avoid duplicating a crew whose work is already done.

### assertion:epic-559-c2-generate-the-spine-005.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A crew that `run_crew.py` recorded as completed classifies as complete.

### assertion:epic-559-c2-generate-the-spine-005.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: For a spine-only dispatch it does not. `run_crew.py` judged the crew completed on spine_terminal and wrote status=completed with completed_at set and result=None into crew-runs.json; `recover_crews.py` then reported the same entry as `NEEDS-ABANDON -- not running and no result; require explicit --abandon ... --relaunch`. Its classifier keys on a result artifact, which a spine-only dispatch deliberately never writes -- `--result` is documented as optional when `--spine` is given precisely because such a crew is judged on its spine reaching a terminal state instead.

### assertion:epic-559-c2-generate-the-spine-005.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: No cost in this run, because the Commander read the registry directly and saw status=completed. The advice, if followed, would have relaunched a crew whose work was finished and whose spine was terminal with its lease released -- the exact duplication the recovery check exists to prevent.

### assertion:epic-559-c2-generate-the-spine-005.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The Commander read `crew-runs.json` directly rather than acting on the classification, and recorded the mismatch as a triage candidate.

## Retirement
- status: retired
- retired-reason: Mechanical field written wrong at capture: `run` was recorded as the kebab-cased 'epic-559-c2-generate-the-spine' rather than the work-id verbatim, 'epic-559/c2-generate-the-spine'. The store's own capture gate (verify_episode_captured.py) matches `- run: <work-id>` exactly, so these eight record a run no reader can resolve. Superseded by re-created equivalents in the same delta; retired rather than hand-edited because this writer is the only write path into the store.
- retired-at: 
- consolidated-into: 
- superseded-by: 
