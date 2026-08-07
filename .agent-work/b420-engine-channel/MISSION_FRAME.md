# Mission Frame

Shrunk frame. This repo has no `docs/architecture` map at all (`docs/CHECKLIST_ENGINE_DESIGN.md` /
`docs/CHECKLIST_SCHEMA.md` back this instead — the design doc is the actual entrypoint the change
belongs against). Map orientation returned DEGRADED-NO-MAP and was discharged with those two files
as hash-pinned substitutes (`.agent-work/b420-engine-channel/map-orientation.json`). The change is
one file's rendering path, not a structural change, so a full frame adds little beyond those two
docs.

## Intent
Fix two defects in the engine's `current` projection so the channel every agent drives from stops
lying: the RAIL echo repeats the active gate's full imperative a second time (measured, exact
doubling), and populated `anchors`/`constraints` gate fields never reach `current` at all. Add a
completeness property test so a future field-add-and-forget-to-render regression fails loud. Per
`docs/CHECKLIST_SCHEMA.md`, `current` is documented as answering "what is true about this
checklist's progress" via a pure `state()` projection rendered by `render_human()` — the contract
already promises completeness; this run makes the code meet it (issue #420, `DESIGN_SPEC.md`
workstream B).

## Affected Capabilities
- `scripts/checklist_engine.py`'s `state()` (around line 1548) and `render_human()` (around line
  1587) — the pure state projection and its human-readable adapter, together the whole `current`
  surface.
- `scripts/checklist_engine.py`'s `_rail_position()` / `_RAIL_STRINGS["mid-flight"]` (around line
  225-263) — the doctrine rail appended to `current`/`claim`/`start`/`advance`/`attest`/`attach`.

## Examples / Events
- Live reproduction this run: every `current` call against this very spine while mid-flight showed
  the active gate's full multi-hundred-word imperative twice — once on the `ACTIVE ... —
  <imperative>` line, once inside `RAIL: ... Next: <imperative>. Run it.`
- Corpus inventory this run (grep across `skills/**/*.json` and `.agent-work/**/execute.json`):
  `anchors` and `constraints` are genuinely populated on ~20+ real archived gates (issue-58, 99,
  102-107, 87, 299, 304-310, epic-298 runs) with real structured content — not vestigial.

## Structural Anchors
No map-native `struct:` ids exist for this repo. The two backing documents:
- `docs/CHECKLIST_ENGINE_DESIGN.md` — "Answerability: current as a complete briefing" section
  states the completeness invariant (INV-1) this fix implements, and documents the RAIL mechanism.
- `docs/CHECKLIST_SCHEMA.md` — the Task field table defines `constraints`; `anchors` is documented
  only in `commander-core.md`'s prose (per-gate `anchors` block in `execute.json`), not in the
  schema's own Task table — a real doc gap this run's evidence does not extend the schema to close
  (out of scope, noted below).

## Governing Constraints / Assumptions
- The five RAIL strings (`_RAIL_STRINGS`) are frozen verbatim — a measurement precondition for
  issue #145 — per `docs/CHECKLIST_ENGINE_DESIGN.md`'s rail section and the launch order. The fix
  must change what value fills the `{imperative}` token, not reword the surrounding template text.
- `state()` is a pure projection (INV-2): it reports recorded condition state and must not gain any
  side effect or re-run of a check while adding the anchors/constraints read.
- Shared-file fence with workstream D (#422): I own `checklist_engine.py`'s rendering path this
  wave; D owns the invariant-check path. My change is confined to `state()`/`render_human()`/
  `_rail_position()` — no touch to `_check_condition`/postcondition evaluation.
- `render_human`'s first line (`ACTIVE {id} [{status}] — {imperative}`) is pinned by
  `tests/test_checklist_engine.py:818` across every shipped template — must stay exact.

## Decision Anchors & Decision Pressure
- Vestigial-fields branch (launch order pre-ruling) resolved by inventory, not guess: anchors and
  constraints are real, populated corpus content. Renderer gets built; fields are not deleted.
  Grade: settled/measured (leans g1-implement) — settled by the grep inventory above, this run.
- RAIL fix shape (revised after cold-critic review, see below): keep the frozen
  `_RAIL_STRINGS["mid-flight"]` text unchanged; the duplication is real ONLY on the `current` verb,
  where `render_human()`'s ACTIVE line already prints the imperative — the other five RAIL_VERBS
  (claim/start/advance/attest/attach) have no ACTIVE line in their output, so the RAIL's imperative
  mention is their only carrier of "what's next" and must stay full-text there. Fix is verb-aware:
  substitute a short pointer only when `point == "current"`. Grade: guess (leans g1-implement,
  settle: land it, confirm the pinned rail tests plus a new per-verb no-duplication/duplication-
  still-present assertion pass) — exact pointer wording is an implementation-slice call.
- Decision pressure: whether `anchors` also belongs in `docs/CHECKLIST_SCHEMA.md`'s Task field
  table (currently only documented in `commander-core.md` prose) is a real doc gap this run's
  evidence surfaces but does not fix — out of scope, noted below, triage candidate at review.

## Claims / Evidence Surfaces
- Claim: the RAIL echoes the gate imperative twice today. Checked by: a golden `current` call
  against a mid-flight fixture, asserting the imperative text appears exactly once in the combined
  output (new test).
- Claim: `anchors`/`constraints`, when populated on the active gate, do not appear anywhere in
  `current`'s output today. Checked by: a golden `current` call against a fixture gate carrying
  both fields, before the fix (red) and after (green).
- Claim: every field a gate may carry that is populated renders in the projection. Checked by: the
  new completeness property test enumerating Task fields and asserting each populated one appears.

## Map Confidence / Staleness / Disputes
No map exists for this repo (by design — a skill-source repo, not a packet-mapped product repo);
nothing here is stale or disputed relative to a map, because there is no map to be stale against.
The two backing docs were read in full this run and are current as of this session.

## Out of Scope
- The DIGEST-staleness-after-HARD-trip observation from the Admiral's live run (`why_trail`/Trip
  interaction) — judged separate from "the channel must not lie" under this issue's scope; routes
  to workstream G (#425) per the launch order's default reading, not absorbed here.
- Extending `docs/CHECKLIST_SCHEMA.md`'s Task table to formally document `anchors` (currently
  prose-only in `commander-core.md`) — real gap, flagged as a triage candidate, not fixed here.
- Workstream C's relocation work and workstream D's invariant-check path — separate workstreams,
  separate worktrees.
