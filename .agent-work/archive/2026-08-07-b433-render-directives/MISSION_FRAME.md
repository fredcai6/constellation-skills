# Mission Frame — issue #433

Cut from the reading this run declared at the `context` step. This repo carries no `docs/architecture`
packet map, so orientation came back DEGRADED and was discharged with four hash-pinned substitutes. This
frame is built from those substitutes, not from code — the source reads that follow confirm it.

Declared reading (the receipt's hash-pinned substitutes, and what each supplied here):

- `docs/CHECKLIST_SCHEMA.md` — the Task field table and the `Rendering` section: the authoritative
  statement of which Task fields exist and which of them `current` projects.
- `docs/CHECKLIST_ENGINE_DESIGN.md` — the engine's model: canonical state, mechanism-not-quality.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project deltas: workflow mechanisms are a *strengthened durable
  system*, so a behaviour change here owes targeted automated tests plus the broader suite.
- `docs/agents/GLOSSARY.md` — `projection` is the engine's rendered view of spine state, what `current`
  prints; agents drive from the projection, never from the JSON file.

## Intent

Make a populated `directives` block reach the agent through the projection, and close the class of
unrendered-field defects so the *next* field added to Task and forgotten in the renderer fails a test by
default rather than shipping invisible.

## Affected Capabilities

- **The projection as the complete state channel.** `docs/agents/GLOSSARY.md` fixes the meaning: agents
  drive from what `current` prints. A Task field that is populated but unprojected is therefore not
  "cosmetically missing" — it is outside the channel the whole fleet reads.
- **The Task field contract.** `docs/CHECKLIST_SCHEMA.md`'s Task table enumerates what a gate may carry.
  It is the enumeration a completeness property must be cut against.

## Examples / Events

- Three shipped spine templates carry a populated `directives` block (commander `execute`, admiral
  `execute`, explorer `confirm`). Every run instantiated from them inherits it — including this run's own
  spine, whose `execute` gate carries the `replan_input` contract that never renders.
- The contract text survives only because each of those gates *also* restates it as prose inside its own
  `imperative`. That duplication is why the invisible block went unnoticed for so long.

## Structural Anchors

Named against the declared reading, since no map anchor ids exist for this run:

- The projection pair described in `docs/CHECKLIST_SCHEMA.md`'s `Rendering` section: the pure state
  projection and the human adapter that formats it. `directives` is read by neither.
- The Task field table in the same document — the enumeration the property loops over.
- The completeness property shipped by #420, which already exists and already names `directives` as a
  stated exclusion.

## Governing Constraints / Assumptions

- The projection's first line is frozen: `ACTIVE {id} [{status}] — {imperative}`. Goldens pin it across
  every shipped template.
- An absent or empty field adds no output. That rule is stated in the `Rendering` section for
  `constraints` and `anchors`; `directives` joins it on the same terms.
- The state projection stays pure — passthrough only, no check re-runs. Stated in the same section.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` rates workflow mechanisms a strengthened durable system: targeted
  automated tests **plus** the relevant broader suite, both named.
- Assert against the projection's behaviour, never against prose describing it.
- **Assumption, and it is the risky one:** `docs/CHECKLIST_SCHEMA.md`'s declared type for `directives`
  (`[string] | null`) is wrong. Eight populated instances in the tree are dicts of nested dicts. The
  renderer must serve the corpus; the document gets corrected.

## Decision Anchors & Decision Pressure

- **render-not-delete** — `directives` is rendered, not deleted. The launch order put deletion on the
  table for a vestigial field; the inventory shows three shipped templates carry it and a test asserts
  its parsed contract, so it is not vestigial.
  `@grade: settled/measured · leans g1 · settle: re-run the tree-wide inventory; a count of 0 populated gates would reopen this`
- **own-helper-not-anchors-helper** — `directives` gets its own line formatter rather than being pushed
  through the anchors normalizer. The two shapes genuinely differ: anchors is category to list-of-string,
  directives is key to nested contract dict. One adapter is a hypothetical seam.
  `@grade: settled/human · leans g1 · (both design-it-twice candidates were compared on exactly this; recorded in PLAN_ALTERNATIVES.md)`
- **per-field-ledger-is-the-class-fix** — the durable part is a per-field record of what the property
  actually asserted, not the flattener. Both independent plan candidates converged here: a recursive
  flattener alone still reports green when a future field yields no text, because the existing guard is
  one flag for the whole loop.
  `@grade: settled/measured · leans g2 · settle: the R4 red-proof — a field whose value flattens to nothing must fail by name`
- **independent-extractor** — the test's leaf extractor is NOT shared with the renderer's. A shared bug
  would render nothing and assert nothing, in agreement.
  `@grade: settled/human · leans g2`
- *Decision pressure:* whether the property is also driven over the live shipped templates, or only over a
  fixture shaped like them. Surfaced to the Admiral in the return rather than silently chosen wide.

## Claims / Evidence Surfaces

- **A populated `directives` block appears in `current`.** Checked by a golden over the real shipped
  commander spine gate, plus the before/after projection capture in the return.
- **The completeness property fails when a populated field is unrendered.** Checked by an in-suite
  negative self-test, and by a recorded manual mutation of the renderer. A property only ever observed
  passing is a check that cannot fail.
- **Nothing else in the projection moved.** Checked by the existing golden classes staying green plus the
  full suite against the recorded baseline.

## Map Confidence / Staleness / Disputes

- **No map exists.** Orientation is DEGRADED for every run in this repo — a standing condition, escalated
  to the Admiral as context, not filed as a new defect.
- **`docs/CHECKLIST_SCHEMA.md` is partly stale and this run depends on it.** Two known drifts: the
  `directives` type, and the `Rendering` section's "Known gap, not yet closed" sentence. The plan does not
  silently trust it — a gate corrects both, and the property is cut against the field set the code really
  carries rather than against the table alone.

## Out of Scope

- The other stated exclusions in the completeness property (identity, bookkeeping, survey-only and pointer
  fields). Each keeps its written reason; none is silently dropped.
- Any change to the gate schema itself — a load-bearing interface shape, which floats to the Admiral.
- The spine rail, the trip bands, and `scripts/collect_feedback.py`, `episodes/`, and
  `scripts/verify_worktree_precondition_coverage.py`, which concurrent siblings own this wave.
