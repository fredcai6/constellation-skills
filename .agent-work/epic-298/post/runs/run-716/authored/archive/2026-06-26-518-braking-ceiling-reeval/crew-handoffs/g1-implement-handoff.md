# Implementer Handoff

## Gate
g1 — Calibrate the decoupled longitudinal estimator HPs across the full 2023-Q season.

## Task
Build a reproducible **calibration harness** that evaluates the decoupled-longitudinal
estimator's hyperparameters across the **full 2023-Q quali season** (all GPs on the 2023
calendar, both cars per constructor) using the existing scoreboard metrics as the objective,
then **decide and persist a calibrated HP set** with season-wide generalization evidence.

The estimator's current defaults were swept on VER / 3 circuits only (Bahrain, Monaco,
Belgium) — flagged in the physics packet Known Limits. This gate replaces that with a
season-justified calibration.

## Protected Intent
The decoupled estimator must keep recovering the real heavy-braking knee WITHOUT introducing
non-throttle ringing, *across the season* — not just on the 3 tuning circuits. The calibrated
HPs are the filter's noise model; they must not be over-fit to a handful of circuits, and the
report must honestly show where the estimator does NOT improve over the baselines.

## Test Mode
Test-after allowed. The harness + any new HP-config module needs unit coverage
(L1 analytical for the estimator already exists: `synthetic_step_recovery`); add tests for the
calibration-harness pure functions (objective aggregation, HP selection) so they are
reproducible without the FastF1 cache. Physics evidence: re-confirm the scoreboard acceptance
on the calibrated HPs.

## Close Criteria
- A calibration harness (new module under `src/physics/layer2/` and/or `scripts/`) runs the
  scoreboard across the full 2023-Q season and aggregates the per-case scores.
- A calibrated HP set is **persisted in named constants/config** (NOT hidden inline tuning) —
  e.g. promote the `_DEFAULT_*` constants in `decoupled_longitudinal.py` to the calibrated
  values, or a small `decoupled_hp.py` config module the estimator reads. Document the basis.
- A calibration report at `reports/physics/decoupled_hp_calibration_2023Q.{json,md}` (gitignored)
  reporting, per session/driver: braking `knee_gap_vs_raw`, `ringing_ok`, and the chosen-HP vs
  VER/3-circuit-default comparison, plus an aggregate season pass-rate.
- The report states clearly whether a single global HP set generalizes, or whether a
  per-session-class split is needed (and if the latter, that becomes a decision candidate — STOP
  and return it, do not pick a structural split unilaterally).
- `py -m pytest tests/unit/physics/layer2/ -q` green.
- `py -m src.utils.simplification_limits` clean on touched paths.

## Allowed Scope
- `src/physics/layer2/decoupled_longitudinal.py` (promote/parametrize the HP constants).
- New: a calibration-harness module (`src/physics/layer2/decoupled_calibration.py` or similar)
  and/or `scripts/calibrate_decoupled_hp_2023Q.py`.
- `src/physics/layer2/scoreboard.py` — you MAY add a season-enumeration helper that reuses
  `run_case`/`run_scoreboard`, but do NOT change the existing metric core or built-in variants.
- `tests/unit/physics/layer2/` — add harness tests.
- `reports/physics/` (gitignored output).

## Specific Exclusions
- Do NOT wire the estimator into any production view (`session_braking`/`session_traction`/
  `session_coast`) — that is G2/G3. This gate is calibration + evidence only.
- Do NOT change `braking_view.clean_longitudinal_from_raw`, the scoreboard metric definitions
  (`braking_knee`, `non_throttle_ringing`, `score_variant`), or the built-in variants.
- Do NOT touch the `EstimateStore`, `car_prior`, or the utilization layer.

## Constraints
- Python is `py`, never `python`.
- Tunable HPs belong in named constants/config — no hidden inline tuning (project planning invariant).
- `constraint:physics_region_no_evo_import` — no imports from `src.evo_predictor`,
  `src.latent_power`, `src.compound_prior`.
- `decision:two_cycle_external_anchor_design` — the soft-force anchor stays the TV-denoised RAW
  `a_long`; never re-read from a smoothed trajectory.
- Honest covariance is first-class; do not drop `sigma_a`.
- Read-only DB access: open season DBs with `file:<path>?mode=ro` if you need them
  (`lesson:dbmanager-not-readonly`); but this gate is telemetry-driven (FastF1 cache), likely no DB needed.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `decoupled_longitudinal.py`, `scoreboard.py`,
  `session_estimator.py`, `estimate_batch.py`.
- **Capability:** physics capability-frontier measurement — the estimator's HP noise model.
- **Constraints:** `constraint:physics_region_no_evo_import`; `decision:two_cycle_external_anchor_design`.
- **Decision anchors:** `decision:decoupled_1d_longitudinal` — this gate records the HP
  calibration basis; surface per-session-vs-global as a candidate if material.
- **Evidence:** scoreboard `braking_knee` + `non_throttle_ringing` pass-rate across the season.
- **Map confidence:** the HP defaults are explicitly flagged VER/3-circuit in the packet Known
  Limits — this gate addresses that flagged limitation.

## Exact seams (verified from source — cite these, do not reinvent)
- `src/physics/layer2/decoupled_longitudinal.py`:
  - `estimate_longitudinal(t, v, a_long_raw, regime, *, theta=None, z=None, mass_kg=MASS_KG, tv_lambda=0.10, sig_v=0.15, sig_a_brake=35.0, sig_a_other=4.0, sig_a_soft_brake=0.10, sig_a_soft_other=30.0) -> DecoupledLongitudinalResult(a_long, sigma_a, f_vehicle, a_soft_obs, is_brake, altitude_assumed_flat)`.
  - `variant_synthesis(inp) -> np.ndarray` — the VariantFn for the scoreboard (FLAT terrain; calls `estimate_longitudinal`). Parametrize a variant factory `make_synthesis_variant(**hp)` so the sweep can vary HPs.
  - The HP constants to calibrate: `_DEFAULT_TV_LAMBDA=0.10`, `_DEFAULT_SIG_V=0.15`, `_DEFAULT_SIG_A_BRAKE=35.0`, `_DEFAULT_SIG_A_OTHER=4.0`, `_DEFAULT_SIG_A_SOFT_BRAKE=0.10`, `_DEFAULT_SIG_A_SOFT_OTHER=30.0`.
- `src/physics/layer2/scoreboard.py`:
  - `run_case(year, gp, driver, variant_fns: dict[str, VariantFn], *, cache) -> CaseResult` — loads `(year, gp, "Q")` once, scores each variant on the fastest flying lap. `CaseResult.scores[name]` is a `VariantScore(knee, ringing, raw_knee, raw_ring, knee_gap_vs_raw, ringing_over_ceiling, ringing_ok)`.
  - `run_scoreboard(...)` and `ScoreboardTable` collect/serialise; reuse them.
  - `BUILTIN_VARIANTS = {"gaussian": ..., "kind3": ...}` — include these as baselines in each run for the comparison.
  - `CaseInputs(t,x,y,v,regime,a_long_raw,make_smoother)` with derived `brake_mask`/`non_throttle_mask`.
- `src/physics/session_fit.py`: `load_quali_session(year, gp, session_type, cache="data/telemetry", offline=True)` — 4-arg form `load_quali_session(year, gp, "Q", cache)`. Returns a tuple; `result[0]` is the session, `result[1]` is rho.
- `src/utils/constants.py`: `get_calendar(year) -> List[str]` (the 2023 GP names; note 2026 dropped Bahrain/Saudi but 2023 is full).
- `MASS_KG` lives at `src.physics.longitudinal_fit.MASS_KG` (= 808.0).

## Data Locations (absolute — this runs in the main checkout)
- Season DB: `C:/Programs/f1Brainz/data/f1_data_2023.db` (read-only via `file:?mode=ro` if needed).
- FastF1 offline cache: `C:/Programs/f1Brainz/data/telemetry` (`DEFAULT_CACHE`). Offline; do not hit live FastF1.
- Report output dir: `C:/Programs/f1Brainz/reports/physics/` (gitignored).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/ -q` output (green).
- `py -m src.utils.simplification_limits` on touched paths (clean).
- The calibration report (`reports/physics/decoupled_hp_calibration_2023Q.{json,md}`) with the
  season-wide pass-rate table and the chosen-vs-default comparison.
- A short note on whether a single global HP set generalizes (and the decision candidate if not).

## Suggested Model Tier
Stronger-bounded — the work is well-scoped against existing seams, but the HP-selection
judgment (generalization, no over-fit, honest reporting) benefits from care.

## Authority
- Scope, sequencing, and "verdict-producing not GO-guaranteed" are the user's decisions (already made).
- You decide the calibration mechanics (sweep grid, objective aggregation) within scope.
- You do NOT decide a per-session-class structural HP split alone — surface it as a candidate and STOP.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a structural per-session HP split looks
necessary (return it as a decision candidate); the season calibration cannot run from the
offline cache; required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g1-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence produced (with the key numbers:
season pass-rate, chosen HP set, where it does/doesn't beat defaults), assumptions used, stop
conditions hit, out-of-scope observations, and **Workflow Feedback** (what in this handoff or
the workflow made the work harder than needed).
