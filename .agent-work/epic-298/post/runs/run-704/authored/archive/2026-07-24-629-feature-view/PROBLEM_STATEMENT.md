# Problem statement — #629 Phase 5: as-of-stamped feature view

## Ask (reconciled against LAUNCH_ORDER)

Build the physics-as-feature-engine epic's (#601) Phase 5: the **product contract** that
packages everything Phases 2-4 built into ONE clean, leakage-safe, DB-only read surface for
evo. Four record types, one store, one read API:

1. Weekend-state record (per event, session) — field-car state, evolution curve, environment
   terms, each with sigma.
2. Car-basis posterior (per constructor, session) — unified basis vector with full covariance
   (Phase 3's cross-view terms), session-chained (FP1->...->Q process-noise links + the
   parc-ferme step — the *fitted* parc-ferme distribution is bounded-deferred per #513; carry
   the framing + a reserved slot, do not refit it here).
3. Lap evidence record (per driver, lap) — representativeness weight (#513
   `fp_representativeness`), inferred mass/mode posteriors, unit-class residuals.
4. As-of-stamped feature view (per event, car) — weekend-relative basis + circuit-conditional
   composite + sigma, as-of stamped. THE ONLY evo-facing surface.

MODEL_VERSION keyed, append-only, constructor grain (named round-1 approximation). This is
packaging + contract, NOT new modeling.

## Baseline reconciliation (order's assumed baseline vs. current code — verified 2026-07-24)

- Confirmed via `docs/architecture/index.md`'s #624 entry: the Phase-0 integration tracer
  (`scripts/g3_schema_assert.py`) explicitly asserts against the CURRENT production
  `sampled-predict` artifact shape (`stage_snapshots`: quali/race_start/race) because
  DESIGN_SPEC's four-record Phase-5 contract is genuinely UNBUILT — matches the launch
  order's framing exactly, no stale premise here.
- Phases 2/3/4 dependencies verified present on base `main` `72577cef` (all merged per
  the launch order): `src/physics/weekend_state/` (Phase 2, `model.py`'s
  `WeekendStateModel.fit/transform/car_signal`, 11-axis `frame.py`), `src/physics/layer2/
  estimate_store.py` + `estimate_store_fields.py` (`effective_axis_sigma`,
  `UNRESOLVED_AXIS_SIGMA_FRAC`, `normalize_axis_status`) + `cross_view.py` (Phase 3,
  `fuse_dual_cda`, the sparse `cross_view_covariance` blob already reserved in
  `EstimateRecord`), `fp_representativeness.py` + `fp_lap_latent.py` (Phase 4,
  `ObservationFeatures`/`observation_weight`/`FpLapLatent`), `session_race.py`'s
  `session_cumulative_track_laps`.
- Genuine gap confirmed: no store or read API composes these into the four Phase-5 record
  types. `fp_gate_real_extractor.py`'s `RealGateExtractor` (the real per-lap telemetry
  wiring) is itself flagged G7-deferred / "machinery proven, powered run compute-deferred"
  (git log `72577cef`) — this bounds what the lap-evidence record can honestly carry today
  (representativeness + mass/mode posteriors are live; a genuine "unit-class residual" against
  a fitted car-basis needs G7's real extractor, which is out of THIS scope per the launch
  order's Phase 6/NN-consumer exclusion — carried as an explicit reserved/unresolved slot,
  not faked).

## Governing sections (LAUNCH_ORDER)

Mission; What to build; Gate; Explicit-unknown contract; Standing directives; Out of scope;
Decision routing. Cited verbatim where each engine checkpoint requires a `user-decision`.
