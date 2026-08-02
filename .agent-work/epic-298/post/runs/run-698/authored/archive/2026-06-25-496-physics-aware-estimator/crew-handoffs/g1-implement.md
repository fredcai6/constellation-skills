# Implementer Handoff — G1 Common Scoreboard Harness

## Gate
g1-implement (work-id 496-physics-aware-estimator, branch `feat/physics-aware-estimator-496`, MAIN checkout — NOT a worktree)

## Task
Build the **common scoreboard** that every subsequent spike (#496/#507 filter-rebuild
exploration) is measured against. Two pieces:
1. A reusable, unit-tested **pure-metric core** at `src/physics/layer2/scoreboard.py`.
2. A thin **orchestrator**: refactor `scripts/validate_refine_505.py` to call that core
   (do not duplicate metric logic), and record the **current-smoother baseline** to a JSON
   under `reports/physics/`, verifying it reproduces the #505 numbers within tolerance.

## Protected Intent
The scoreboard is the TRUST ANCHOR: five independent spikes will each plug in a different
trajectory-estimation variant and be compared head-to-head. Therefore the metric core must
(a) be pure and deterministic, (b) hold the per-lap regime masks + raw-sensor reference
FIXED across variants (only the variant's smoothed `a_long` changes), and (c) expose an
injected-variant seam so an arbitrary estimator can be scored without touching the core.

## Test Mode
TDD required for the pure-metric core (it is small, pure, and L1/L2-checkable with synthetic
arrays). Integration baseline-reproduction is test-after (needs real cached sessions; capture
as command evidence, not a unit test).

## Close Criteria (each must be proven)
- `src/physics/layer2/scoreboard.py` exists with:
  - Pure metric fns operating on numpy arrays + boolean masks:
    - `braking_knee(a_long, brake_mask) -> float` = `min(a_long[brake])` (deepest signed decel; NaN if no brake samples).
    - `non_throttle_ringing(a_long, non_throttle_mask) -> float` = `max(a_long[non_throttle])` (max spurious positive accel where NOT on throttle; NaN if empty).
  - A `VariantScore` dataclass: `knee, ringing, raw_knee, raw_ring, knee_gap_vs_raw (=knee-raw_knee), ringing_over_ceiling (=ringing-raw_ring), ringing_ok (=ringing <= raw_ring + eps)`.
  - A `score_variant(a_long_variant, raw_a_long, brake_mask, non_throttle_mask) -> VariantScore` pure fn.
  - An **injected-variant seam**: `VariantFn = Callable[[CaseInputs], np.ndarray]` returning the variant's `a_long` aligned to the lap time grid; the core owns masks + raw reference + metrics.
  - `run_case(year, gp, driver, variant_fns: dict[str, VariantFn], *, cache) -> CaseResult` — loads the session ONCE, builds the fixed lap inputs (masks + raw a_long), scores each variant.
  - `run_scoreboard(cases, variant_fns, *, cache) -> ScoreboardTable` over the fixed case set, plus a `to_json()` / markdown table emitter.
  - Two built-in baseline variants: `"gaussian"` (`nu_proc=None`, no kind=3 — the blind baseline) and `"kind3"` (the current production two-cycle `refine_trajectory`).
- `tests/unit/physics/layer2/test_scoreboard.py` — synthetic-array unit tests (no real session): known-min in brake → knee; injected positive spike in non-throttle → ringing; `ringing_ok` boundary; NaN handling for empty masks; `knee_gap_vs_raw` sign. (L1/L2 truth.)
- `scripts/validate_refine_505.py` refactored to call the core (its existing printed tables/plots may stay, but the knee/ringing numbers come from the core, not its own inline `_knee_and_ringing`).
- Baseline JSON written under `reports/physics/` (e.g. `scoreboard_baseline_2023Q.json`) for the fixed case set, AND a captured run showing the `"gaussian"`/`"kind3"` knee+ringing reproduce `.agent-work/505_validation_findings.md` within ~0.5 m/s² tolerance (Belgium gaussian≈−34.9/kind3≈−37.4/raw≈−38.8; Monaco gaussian≈−38.1 ring≈13.1 raw_ring≈5.6; Bahrain gaussian≈−39.5 raw≈−52.1).

## Allowed Scope
- NEW: `src/physics/layer2/scoreboard.py`, `tests/unit/physics/layer2/test_scoreboard.py`.
- REFACTOR (call the core, remove duplicated metric logic): `scripts/validate_refine_505.py`.
- WRITE (gitignored output): `reports/physics/scoreboard_baseline_2023Q.json`.

## Specific Exclusions
- Do NOT implement any new estimation mechanism (that is G2 — spikes). G1 only measures the
  EXISTING gaussian + kind3 paths.
- Do NOT modify `smoother.py`, `accel_obs.py`, `trajectory_refine.py`, `braking_view.py`,
  `calibration.py`, or any estimator. Consume them read-only.
- Do NOT change the raw-sensor reference definition (`clean_longitudinal_from_raw` is the
  un-biased ground truth per `decision:two_cycle_external_anchor_design`).

## Constraints
- `py` launcher (Python 3.14). Tests run `py -m pytest`.
- `constraint:physics_region_no_evo_import` — import no `src.evo_predictor/latent_power/compound_prior`.
- Metric units/sign explicit: `a_long` signed m/s²; decel is NEGATIVE; knee is the MIN (most
  negative); ringing is the MAX positive in non-throttle.
- `py -m src.utils.simplification_limits` must stay clean on the new/touched files.
- Honest covariance is not required for the scoreboard itself, but do not strip σ where the
  underlying seams already provide it.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — new `src/physics/layer2/scoreboard.py`; consumes
  `accel_obs.py`, `braking_view.py`, `trajectory_refine.py`; `scripts/validate_refine_505.py`.
- **Capability:** trajectory-estimation eval — a comparable, trustworthy scoreboard.
- **Constraints/decisions:** `constraint:physics_region_no_evo_import`;
  `decision:two_cycle_external_anchor_design` (raw `a_long` is the un-biased reference);
  `decision:smoother_rounds_braking_knee` (the defect quantified).
- **Evidence:** scoreboard reproduces the #505 baseline within tolerance.

## Verified Seam Signatures (cite — do not reinvent)
From `scripts/validate_refine_505.py` (working reference) — these are exact:
- `from src.physics.session_fit import load_quali_session` →
  `load_quali_session(year:int, gp:str, "Q", cache:str)`; returns a result whose
  `result[0]` is the FastF1 `session`, `result[1]` is `rho:float`. **4-arg form.**
- `from src.physics.layer2.session_braking import _driver_samples, _to_kinematic_samples` →
  `_driver_samples(session, driver) -> (processed, control, _xyz, spd_d)` (None on failure);
  `_to_kinematic_samples(processed, control) -> list[KinematicSample]` (each has
  `.timestamp_ms`, `.position` (x,y), `.speed`, `.regime`).
- `from src.physics.layer2.braking_view import clean_longitudinal_from_raw` →
  `clean_longitudinal_from_raw(spd_d["t"], spd_d["V"], t) -> (v_at, a_long_raw, sig)` —
  `a_long_raw` is the RAW-sensor reference aligned to `t`.
- `from src.preprocessing.trajectory.calibration import calibrate_session_hp` →
  `calibrate_session_hp(t, x, y, tc, v, order=4) -> hp` with `hp.ell/.sf/.sig_pos/.delta`.
- `from src.preprocessing.trajectory.smoother import StintSmoother, AccelObs` →
  `StintSmoother(ell, sf, sig_pos, delta, order=4, iters=6, nu_proc=None)`;
  `.fit(t, x, y, tc, v, accel_obs=None)`; `.acc_at(t) -> (ax, ay)`; `.vel_at(t) -> (vx, vy)`.
- `from src.physics.layer2.trajectory_refine import RefineInputs, refine_trajectory` →
  `RefineInputs(t, x, y, tc, v, a_long, regime)`; `refine_trajectory(make_factory, inp, nu_proc=4.0) -> StintSmoother`.
- Longitudinal accel projection (reuse this exact formula):
  `a_long(t) = (ax*vx + ay*vy) / max(hypot(vx,vy), 1e-6)` from `.acc_at(t)`/`.vel_at(t)`.
- Masks: `brake = regime == "straight_brake"`, `coast = regime == "straight_coast"`,
  `non_throttle = brake | coast`.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_scoreboard.py -q` output (green).
- A captured run of the refactored `scripts/validate_refine_505.py` (or a small driver)
  showing the gaussian/kind3 knee+ringing for Belgium/Monaco/Bahrain reproducing #505.
- `py -m src.utils.simplification_limits src/physics/layer2/scoreboard.py scripts/validate_refine_505.py tests/unit/physics/layer2/test_scoreboard.py` clean.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_scoreboard.py -q
py scripts/validate_refine_505.py
py -m src.utils.simplification_limits src/physics/layer2/scoreboard.py scripts/validate_refine_505.py tests/unit/physics/layer2/test_scoreboard.py
```

## Suggested Model Tier
simple-bounded (Sonnet) — bounded refactor + pure metric core; seams are all verified above.

## Authority
Plan + scoreboard design are decided (commander). You may choose internal dataclass/function
names and the exact JSON shape. You may NOT: add a new estimation mechanism, alter the raw
reference, or change the fixed case set (Belgium/Monaco/Bahrain 2023 Q VER).

## Data Locations (absolute — main checkout; worktree-untracked-data)
- FastF1 telemetry cache: `C:/Programs/f1Brainz/data/telemetry` (2023 fully cached, all 22 rounds).
- Year 2023, session "Q", driver "VER" for all three cases.

## Stop Conditions
Stop and return if: a seam signature above is wrong in source, the baseline cannot reproduce
#505 within tolerance (report the actual numbers — that is a finding, not a failure to hide),
allowed scope must be exceeded, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/496-physics-aware-estimator/crew-handoffs/g1-implement-result.md`):
completed slice, files changed, test mode satisfied, evidence (command outputs), the baseline
table vs #505 numbers, assumptions, stop conditions hit, out-of-scope observations, and
Workflow Feedback (what in this handoff/workflow made the work harder than needed).
