# Mission frame — issue #305, mechanical episode capture

Map-first input to the gate plan. This repo is a **skill-source repo with no
`docs/architecture/` packet map**, so the map substitute is the frozen design docs the
launch order and the context step named: `docs/EPISODE_STORE.md` (#301),
`docs/CHECKLIST_ENGINE_DESIGN.md` and `docs/CHECKLIST_SCHEMA.md` (#300 + engine). The
substitution is recorded here rather than assumed.

## Intent

Make the mechanical half of an episode record **fall out of driving the engine**, so the
episode store accumulates truthfully in exactly the runs that went worst — the runs where
an agent would have been least likely to remember to record anything. This is not a
capture feature; it is the accumulator that replaces `.agent-work/LESSONS.md` (Tommy's
playbook ruling, relayed in the order).

Frame is **full, not shrunk**: the change lands inside `checklist_engine.py`, shared
machinery three other commanders are concurrently depending on.

## Affected capabilities

- **Context projection** (`scripts/context_manifest.py`) — shipped, complete, and
  **uncalled**. #305 gives it its first caller.
- **Episode store** (`scripts/apply_episode_delta.py` writer, `scripts/query_episodes.py`
  retrieval, `episodes/active|retired/`) — shipped and validated. #305 feeds it.
- **Checklist engine** (`scripts/checklist_engine.py`) — the state source. The only
  component whose *behavior* changes.

## Structural anchors

| Anchor | Address | Why it matters here |
|---|---|---|
| assembly seam | `main()` `current` branch, `checklist_engine.py:2549-2585` | where the engine hands an agent its briefing — the byproduct point |
| refusal path | `except EngineError`, `:2556-2572` | already persists `cl`; records no refusal fact |
| journal | `append_journal_entry`, `:2524-2543` | success-only, by design (`:2469`) |
| check evidence | `_check_condition`, `:747-762` | appends `command-output` `{cmd, exit, shell}` **before** raising |
| step selector | `active_id`, `:184` | THE selector; `build_manifest` already uses it, no second one |
| manifest path | `manifest_path()`, `context_manifest.py:413` | `<root>/<work-id>/context/<step>.json` |
| mechanical allowlist | `_validate_create`, `apply_episode_delta.py:866` | frozen contract; misfiled field is a hard error |
| field group | `_FIELD_READERS`, `query_episodes.py:240` | the eleven fields, already frozen |

## Governing constraints and assumptions

- `decision:manifest-is-a-byproduct` — assembly emits it; nothing *calls* a write step.
  `@grade: settled/human · leans g1`
- `decision:episode-store-is-301s` — write into `episodes/active/` as shipped; no second
  store. `@grade: settled/inherited · leans g3`
- `decision:zero-agent-effort-is-literal` — a field an agent can omit by forgetting is not
  mechanically captured. `@grade: settled/human · leans g2,g4`
- `decision:throwaway-consolidation` — the synthetic consolidation is discarded; a test
  artifact must never become canon. `@grade: settled/inherited · leans g5`
- `decision:drop-run-dirty` — removal, not repair. `@grade: settled/human · leans g1`
- **Windows/CI**: `py` 3.12.13 matches CI's pin but has no pytest; `python` 3.14.3 has
  pytest 9.0.2. Neither reproduces CI — a local green is never the gate.
  `Path.read_text(newline=...)` is 3.13+ and cost PR #320 39 CI failures.
- Explicit `encoding='utf-8', newline='\n'` on every write.
- `command` postconditions: **no `cwd=`** (`:713`) and **stdout discarded** (`:755`). Any
  check I author is an **exit-code vocabulary** with absolute paths. Exit 1 and 2 collide
  with argparse and tracebacks — reserve distinct codes.

## Decision pressure

**One live decision candidate, floated to the Admiral, not decided here:** whether adding
refusal recording to the engine is inside this deliverable or a scope change. The mechanical
field group treats `refusals` as mechanical; engine state has no such fact. Either the
engine gains it or the acceptance criterion is knowingly unmet. Recommendation logged in
the float; the plan is authored so the answer changes **one gate**, not the shape.

## Claims and evidence surfaces

- The negative control is the **primary** evidence surface and the one most at risk of
  being vacuous. It is proven falsifiable **before** any green is trusted.
- `#300 AC1 can now fail` is a distinct, second surface: an assembly must exist for the
  criterion to have a domain at all.
- Cross-run retrieval via `query_episodes.py` over seeded episodes.

## Map confidence, staleness, disputes

- `docs/EPISODE_STORE.md` §1 carries a **stale transcript**: its `git check-ignore
  .agent-work/` evidence was accurate at #301 g1 and was invalidated by #326 making
  `.agent-work/` tracked. issue-309 already hit this. **This is the same fact that causes
  the `run.dirty` defect I am removing** — I treat the doc's §1 conclusion (store lives at
  `episodes/`) as still correct and its transcript as stale, and I re-run the commands
  rather than quoting them.
- The launch order itself is **partly stale**: #321 is fixed at my base. Verified, not
  assumed.
- The **served engine differs from the repo engine** (#344, 120,146 vs 128,889 bytes). All
  engine facts this frame relies on were re-verified in the served copy.

## Out of scope

Ranking, similarity, embeddings, or any judgment that two episodes rhyme (#308). The real
first consolidation (#308). Redesigning the writer, the field group, or the store layout.
Anything that widens the manifest from a record of **delivery** toward proving **use**.
