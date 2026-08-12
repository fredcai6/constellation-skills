<!-- episode-state: schema=1 id=epic-559-c2-generate-the-spine-001 status=retired -->

# episode: epic-559-c2-generate-the-spine-001

## Mechanical
- run: epic-559-c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: plan
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/crew-handoffs/plan-critic-intent-fit-result.md
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/plan-critic.md
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md

## Agent-supplied

### assertion:epic-559-c2-generate-the-spine-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Give every generated gate a place to record beliefs, concerns and open questions, riding in the `directives` substrate the engine already renders on the active gate.

### assertion:epic-559-c2-generate-the-spine-001.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A `directives.handback` block carrying `beliefs`/`concerns`/`open_questions` arrays would be a place a crew could write into, and `current` would render what it wrote.

### assertion:epic-559-c2-generate-the-spine-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: A cold critic searched the engine, the CLI and the MCP surface for any verb that appends to a `directives` field on the gate a crew is actively working, and found none: `amend`'s `rescope` op is restricted to PENDING gates and demands --authority/--reason, so it categorically cannot touch the active gate. It then rendered the exact designed shape through `render_human` and pasted the output -- three labels each followed by a colon and nothing else, on every gate, permanently. The design was caught before any crew implemented it.

### assertion:epic-559-c2-generate-the-spine-001.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: Zero implementation cost, because it was caught at the plan step by a critic that ran the renderer instead of reading the plan. Had it shipped, every generated gate would have carried three permanently empty fields that looked like a working handback channel.

### assertion:epic-559-c2-generate-the-spine-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The arrays were deleted. The contract now names the three verbs that do persist -- `attach` to the gate's evidence, `flag-candidate` to top-level triage_candidates, `block` to top-level blockers and the recorded parent -- and a test drives each verb against a generated spine and asserts where the record lands.

## Retirement
- status: retired
- retired-reason: Mechanical field written wrong at capture: `run` was recorded as the kebab-cased 'epic-559-c2-generate-the-spine' rather than the work-id verbatim, 'epic-559/c2-generate-the-spine'. The store's own capture gate (verify_episode_captured.py) matches `- run: <work-id>` exactly, so these eight record a run no reader can resolve. Superseded by re-created equivalents in the same delta; retired rather than hand-edited because this writer is the only write path into the store.
- retired-at: 
- consolidated-into: 
- superseded-by: 
