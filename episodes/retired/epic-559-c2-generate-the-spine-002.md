<!-- episode-state: schema=1 id=epic-559-c2-generate-the-spine-002 status=retired -->

# episode: epic-559-c2-generate-the-spine-002

## Mechanical
- run: epic-559-c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 1
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-review-result.md
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-implement-rework-handoff.md

## Agent-supplied

### assertion:epic-559-c2-generate-the-spine-002.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Make a large claim change what a gate needs to close, so judgment is carried up to a reviewer rather than sitting inside a gate nobody opens.

### assertion:epic-559-c2-generate-the-spine-002.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: An injected artifact postcondition requiring a review-result matching verdict APPROVE would prevent the gate closing until an independent reviewer approved, on any checklist type.

### assertion:epic-559-c2-generate-the-spine-002.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: It holds on `gated` and is inert on `survey`. A cold reviewer copied the generated reviewer survey to scratch, drove every item through `record`, and consolidated: the survey reached verdict APPROVE with the injected postcondition still unsatisfied and no review-result ever attached. Reading the engine explains it -- `record()` on a survey item evaluates only command-kind postconditions (#422/#328) and `consolidate()` reads only each item's `result` field, while `advance()` on a gated gate checks every postcondition with no kind filter. The reviewer reproduced it a second time against bare checklist_engine dicts with no generator in the loop.

### assertion:epic-559-c2-generate-the-spine-002.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One full rework round: the gate was reopened, a fresh implementer and a fresh reviewer were dispatched. It also invalidated a claim in the run's own frozen design note, which had named a narrower residual (a spoofable APPROVE) than the real one (nothing needs to be attached at all).

### assertion:epic-559-c2-generate-the-spine-002.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The generator now injects nothing for a large claim on a survey and instead states the non-enforcement in `directives.claim.enforcement` and the rollup, naming the mechanism. The tempting alternative -- a command-kind check, which `record` does evaluate -- was declined because no artifact in the corpus could honestly satisfy it, which would have turned a gate that cannot fail into one that cannot pass.

## Retirement
- status: retired
- retired-reason: Mechanical field written wrong at capture: `run` was recorded as the kebab-cased 'epic-559-c2-generate-the-spine' rather than the work-id verbatim, 'epic-559/c2-generate-the-spine'. The store's own capture gate (verify_episode_captured.py) matches `- run: <work-id>` exactly, so these eight record a run no reader can resolve. Superseded by re-created equivalents in the same delta; retired rather than hand-edited because this writer is the only write path into the store.
- retired-at: 
- consolidated-into: 
- superseded-by: 
