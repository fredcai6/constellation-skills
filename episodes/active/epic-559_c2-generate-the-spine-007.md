<!-- episode-state: schema=1 id=epic-559_c2-generate-the-spine-007 status=active -->

# episode: epic-559_c2-generate-the-spine-007

## Mechanical
- run: epic-559/c2-generate-the-spine
- project: constellation-skills
- role: commander
- spine-step: execute
- context-manifest-ref: .agent-work/epic-559/c2-generate-the-spine/STATE_NOTE.md
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 1
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/execute.json
- artifact-ref: .agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md

## Agent-supplied

### assertion:epic-559_c2-generate-the-spine-007.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Point the authored execute.json's `config_ref` at the document standing in for the absent docs/agents/engine-config.json.

### assertion:epic-559_c2-generate-the-spine-007.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: A `config_ref` the engine cannot use is either ignored or refused with a message naming the file.

### assertion:epic-559_c2-generate-the-spine-007.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: `checklist_engine.load_config` calls `json.loads` on any `config_ref` whose path EXISTS, so pointing it at a markdown file raised an unhandled JSONDecodeError out of main() before any rail text could print. A MISSING path falls through to `{}` and is harmless -- which is why every shipped template's nonexistent `docs/agents/engine-config.json` has never surfaced this. `validate_spine.py` carries no fault for the crashing shape, so the lint reports such a spine clean.

### assertion:epic-559_c2-generate-the-spine-007.a4
- kind: impact-cost
- strength: strong
- lifecycle-standing: active
- statement: One traceback and one diagnosis before any gate had begun. It became a design input: the generator refuses the shape as a named spec-shape fault.

### assertion:epic-559_c2-generate-the-spine-007.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: `config_ref` was set to `docs/agents/engine-config.json`, the same nonexistent path every shipped template uses, so config falls through to defaults; the oracle's own gap was recorded rather than patched, since moving the oracle was outside latitude.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
