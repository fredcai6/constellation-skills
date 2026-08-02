# Mission Frame — issue #624 Phase 0 probes

## Intent

Run five read-mostly/analysis probes on EXISTING data (physics `session_estimates`, evo's own feature/model code, one real weekend's records) to de-risk the physics-as-feature-engine seam before Phases 1-6 are built: where physics signal lives (partial correlation), whether the injection seam wires (wide-σ A/B), whether the real four-record contract round-trips (integration tracer), whether SQ is compatible with the Q estimator, and a frozen baseline-lock artifact. No production behavior changes; no new estimator modeling.

## Affected Capabilities

- `struct:physics.layer2` — `session_estimator.estimate_session` (Q-only, `quali_mass()` unconditional — probed by SQ coverage), `session_estimates` store schema (11 axes — read by correlation screen only; baseline lock transcribes from the already-archived x4/x7 excursion RESULT files, no independent re-query).
- `struct:evo.module_adapters` / `driver_residual_history_adapter.py` — the neutral injectable-field prototype seam (probed by wide-σ A/B).
- `struct:evo.sampled_runtime` — the live 3-stage sampled predictor and its four-record contract (probed by the integration tracer).
- `struct:evo.data_adapter` / `quali_recent_history_adapter.py` — the existing recent-history feature the correlation screen residualizes against.

## Examples / Events

- One real weekend (year/race TBD at g3, likely 2025 Japan per the verified working headless invocation in the launch order) run end-to-end through `sampled-predict` to produce the four-record contract artifacts.

## Structural Anchors

- `src/physics/layer2/session_estimator.py:86-135` (`estimate_session`, `quali_mass` call at :125) — level: module.
- `src/evo_predictor/driver_residual_history_adapter.py:32-115` (`build_neutral_driver_residual_history_field`) — level: module.
- `src/evo_predictor/module_context.py:25` (`RuntimeModuleContext.driver_residual_states` default empty) — level: field.
- `src/evo_predictor/module_adapters/_runtime_builders.py:536-581` (`_make_runtime_driver_residual_history`) — level: function.
- `src/evo_predictor/quali_recent_history_adapter.py:57-163` (recent-history feature builders) — level: module.
- `src/evo_predictor/data_adapter/_build.py:429-456` (SQ classification load, already live) — level: function.
- `src/evo_predictor/sampled_runtime.py` (`SampledEvoRuntime.predict_from_features`, the 3-stage sim) — level: module.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — physics probes (SQ, baseline lock) must not add an evo-region import into `src/physics/`.
- DB-only constraint (`docs/agents/ORCHESTRATOR_CONTEXT.md`) — no direct FastF1 calls from analysis code; the correlation screen reads `physics_estimates.db` + the season DBs only.
- Pre-Ruling #1 (mandatory partial correlation, pre-registered axis) — satisfied via `PRE_REGISTRATION.md` (timestamped 2026-07-18T01:39:24Z, before any correlation code existed).
- Pre-Ruling #3 (no new estimator modeling; float if machinery is missing) — governs the "evo's own quali error" gap resolution in `PROBLEM_STATEMENT.md` (chose the sampler-free DB/pandas construction, not NN-inference).
- Known stale-artifact note (`docs/architecture/index.md` Open Structural Questions, "#575 g4"): `physics_estimates.db` was built with the OLD flat burn-rate model, now stale vs the wired burn rate. This affects the RACE-mass path; `session_estimates` (Q-only, `quali_mass()`) is a separate mass function untouched by that staleness — verified not to confound this run's Q-only probes, but flagged for the verdict since it is exactly the kind of "map area that alters the plan" doctrine calls out.

## Decision Anchors & Decision Pressure

- `decision:regime_readiness_rubric` (#512) — prior finding that the regime-capability vector is circuit-conditional/fine-margin (`frac_team` ~0-4%), not a clean car axis. Sets expectation: a NULL or weak partial correlation in g1 would be consistent with this prior finding, not a surprise.
- Decision pressure: none created by this run — Phase 0 is explicitly informational (F1/F11), no go/no-go choice is forced.

## Claims / Evidence Surfaces

- `claim:lateral_car_prior_boundary_conversion` (g-unit → m/s² conversion at `car_prior` boundary) — NOT touched by this run (`session_estimates` columns are read as-is, in g-units, no unit conversion needed for a same-units-only correlation).

## Map Confidence / Staleness / Disputes

- The burn-rate staleness note above is the one live disputed/stale area this run's data source touches; resolved as non-confounding for Q-only axes (documented, not silently trusted).
- `docs/architecture/index.md` "Evo packet module-coverage tail" — several internal evo helper modules (this run touches `driver_residual_history_adapter.py`, `module_context.py`) carry packet prose but are implementation helpers; low risk, no plan change needed.

## Out of Scope

Phases 1-6 machinery (segmentation substrate, four-layer state model, unified-basis refit, FP extension, feature-view contract, real BT injection). No production-default changes. No merge (Admiral's call). Building a full trained-model-based "quali error" artifact (the heavier alternative construction named in `PROBLEM_STATEMENT.md`) is explicitly out of scope for Phase 0.
