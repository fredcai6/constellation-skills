# Mission Frame — #629 Phase 5: as-of-stamped feature view

## Intent

Build the physics-as-feature-engine (#601) product contract: ONE store + ONE read API
exposing four record types (weekend-state, car-basis posterior, lap evidence, as-of feature
view) so evo can eventually consume physics features leakage-safe. Packaging + contract over
Phases 2-4's already-built machinery — no new estimation/modeling. Two load-bearing gate
tests (append-only contract-freeze; as-of leakage by construction) are the deliverable's
correctness core, not an afterthought.

## Affected Capabilities

- `struct:physics.weekend_state` (Phase 2, #626) — `WeekendStateModel.fit/transform/
  car_signal`; produces the L1-L4 per-axis decomposition this run's weekend-state record
  reads FROM (read-only consumer, not a modifier).
- `struct:physics.layer2` (Phase 3/4, #627/#513) — `estimate_store.EstimateRecord`/
  `EstimateStore` (session_estimates table: 11-axis basis + sigma + `cross_view_covariance`
  sparse blob + per-axis `{axis}_status`), `cross_view.fuse_dual_cda`, `fp_representativeness.
  observation_weight`/`ObservationFeatures`, `fp_lap_latent.FpLapLatent`, `session_race.
  session_cumulative_track_laps`. All read-only consumers this run composes, does not modify.
- New capability this run adds: a feature-view component (store + read API) — the only
  evo-facing physics surface. No existing capability node for it yet (genuinely new).

## Examples / Events

- The #624 Phase-0 integration tracer (`scripts/g3_schema_assert.py`) asserted against the
  CURRENT monolithic `sampled-predict` artifact BECAUSE this contract didn't exist yet — this
  run is what that tracer will eventually round-trip against (Phase 6/#630, out of scope here,
  wires the actual injection).
- `estimate_store.populate_cumulative_track_laps_for_demo` — precedent for a demo-scoped,
  explicitly-named-weekend backfill helper (same pattern this run may reuse for populating
  demo rows without a full historical backfill).

## Structural Anchors

- `struct:physics.weekend_state` (`src/physics/weekend_state/`) — component level, existing.
- `struct:physics.layer2` (`src/physics/layer2/`) — component level, existing; this run's new
  store code is planned as module-leaf additions here (or a new sibling component — see
  Decision Pressure below).
- New: `src/physics/feature_view/` (or `src/physics/layer2/feature_view*.py`) — module-leaf
  or new component, TBD at plan (decision candidate).

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — the new store/read API must not import
  `src.evo_predictor` (verified pattern: every existing physics module is clean; this run's
  code must stay clean too — checked at reconcile).
- DB-only doctrine (ORCHESTRATOR_CONTEXT) — the read API is evo's ONLY reach into this data;
  no bypass path.
- Explicit-unknown contract (launch order, OWNER HARD REQUIREMENT) — reuse `effective_axis_
  sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC` (estimate_store_fields.py:127/139), never drop an
  unmeasurable axis/term.
- Append-only + as-of-by-construction (launch order Gate) — non-negotiable correctness
  properties, tested before wiring.
- DB hygiene (#632) — never commit `data/*.db`; this worktree does not track `data/*.db`
  (lesson:worktree-untracked-data / weekend_state/frame.py's own DB_PATH comment) — new
  store tables land in the SAME untracked physics DB(s), schema/code is what's committed.

## Decision Anchors & Decision Pressure

- No existing decision anchor covers a "Phase-5 feature-view store" shape yet — this run
  creates the first one (structural placement: new component vs. layer2 module-leaf).
- **Decision pressure 1 (structural placement):** new sibling component
  `struct:physics.feature_view` (mirrors the Phase-2 precedent of `weekend_state` getting
  its own component) vs. module-leaf additions under existing `struct:physics.layer2`. Surfaced
  in plan-alternatives below; resolved there, recorded as a decision candidate at reconcile.
- **Decision pressure 2 (car-basis posterior "session-chained" framing):** the launch order
  names an FP1->FP2->FP3->[parc-ferme]->Q process-noise chain but only the parc-ferme step's
  *fitted* distribution is explicitly bounded-deferred per #513. No process-noise LINK fit
  exists anywhere in the codebase (checked: `pooling.fit_drift` is a season-clock trend, not
  an intra-weekend session-to-session link). Resolution: the record carries the CHAIN
  ORDERING/framing (each session's own already-fitted posterior, session-ordered) with BOTH
  the parc-ferme step AND the inter-session process-noise link as reserved/unresolved slots —
  extending the launch order's explicit parc-ferme deferral to the sibling gap it didn't
  separately name, per the same honest-null logic. Not floated to the Admiral: this is a
  scoping judgment squarely inside "if a record type can't yet be honestly composed, carry it
  as an explicit reserved slot" (launch order, binding directive), not a new decision.
- **Decision pressure 3 (lap-evidence "unit-class residuals"):** `fp_gate_real_extractor.
  RealGateExtractor` (the real per-lap telemetry wiring that would produce a genuine
  grip/power-class residual against the fitted car-basis) is itself flagged G7-deferred /
  "machinery proven, powered run compute-deferred" per the base commit. Resolution: the
  lap-evidence record populates representativeness weight + mass/mode posteriors (both live,
  `fp_representativeness`/`fp_lap_latent`) and carries `unit_class_residual` as an explicit
  reserved/unresolved slot — same honest-null logic as pressure 2.

## Claims / Evidence Surfaces

- Append-only: a MODEL_VERSION bump never mutates a prior row — checked by a test that writes
  v1, bumps to v2, and asserts the v1 row is byte-identical (not by convention/docstring).
- As-of leakage: a view queried "as of post-FP1" cannot see FP2/FP3/Q — checked by a test
  that seeds all four sessions with distinct sentinel values and asserts the post-FP1 query's
  SQL/result set structurally never touches the FP2/FP3/Q rows (by construction: the WHERE
  clause enumerates only sessions at-or-before the cutoff in a defined session order, never a
  superset-then-filter).
- DB-only: evo never reaches past the feature view — checked by grep (no `src.evo_predictor`
  import in the new module(s); enforced the same way `constraint:physics_region_no_evo_import`
  is verified elsewhere).

## Map Confidence / Staleness / Disputes

- None disputed. The #624 index entry, DESIGN_SPEC.md Phase 5 section, and the Phase 2/3/4
  source are all mutually consistent and current (index reconciled through 2026-07-18/19,
  base is 72577cef which is after all three).

## Out of Scope

- Phase 6 (#630) injection wiring into evo; the NN consumer (round 2) — per launch order.
- Re-fitting the parc-ferme step or any inter-session process-noise link (reserved slot only).
- Building/wiring the G7 real per-lap telemetry extractor (reserved slot only for unit-class
  residuals).
- Any real historical backfill of `cumulative_track_laps` (#646, already named as deferred) or
  a full-season populate of the new store — a small demo/smoke-scale populate (mirroring
  `populate_cumulative_track_laps_for_demo`'s precedent) is in scope only to prove the gate
  tests against real rows if needed; a bulk backfill is not.
