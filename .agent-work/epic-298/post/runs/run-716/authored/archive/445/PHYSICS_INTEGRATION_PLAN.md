# #445 — Physics engine integration plan: ideal lap as a product (2026-06-16)

Rigorous review of `src/physics/` against this session's envelope learnings, and a unified test-driven
plan toward a SINGLE execution pathway. Verdict: **~75% aligned** — the engine architecture is right;
our work *completes and corrects* it, does not replace it.

## What `src/physics/` already is (1,883 LoC, 28 test files, blessed fixtures)
A well-structured, tested estimator→simulator engine, but **orphaned** (only `src/physics` imports it;
the prediction pipeline does not) and **not exercised end-to-end for uncertainty**:
- `ParameterEstimator`: telemetry+controls → segment (throttle/coast/brake/corner) → fit forces.
- `LongitudinalFit`: **drag from COAST** `−a = θ_R + θ_D·ρ·v²` (2×2 covariance) + **power as a monotone
  time-trajectory** from throttle given (θ_D,θ_R). Sidesteps the full-throttle P↔CdA degeneracy by
  construction (different decomposition than our envelope joint-fit).
- `LateralEnvelopeFit`: **grip envelope** `a_lat = A0 + A2·ρ·v²` (2×2 covariance) — i.e. our
  "frontier-B = downforce ceiling" axis.
- `FrictionCoupling`, `PhysicsSimulator` (forward-backward quasi-static), `LapTimeDistribution`, config,
  data models, plausibility fallbacks, per-sample weighting from preprocessor kinematic covariance.

## ALIGNED (already there — keep)
- Quasi-static forward-backward ideal-lap sim (same family as our envelope sim).
- Density AS A PARAMETER in the fits; **honest covariance σ from the fits** (drag θ_D↔θ_R, lateral
  A0↔A2) — our "covariance over bootstrap" lesson is already the house style here.
- Drag/power SEPARATION via coast-vs-throttle regimes (avoids the degeneracy we fought).
- Segment classification, friction ellipse, fallback/plausibility, input-covariance weighting.

## GAPS (our work adds)
1. **The Monte-Carlo is a STUB and untested.** `simulate_lap(sample=True)` never uses `sample`;
   `monte_carlo_laps` runs the deterministic sim n times → zero variance. **Our covariance-aware
   sampling is exactly the missing implementation** (joint draws from the stored fit covariances;
   the 3–4× tightening result; cornering↔braking tied via the friction circle). THE headline.
2. **Simulator hardcodes `reference_density_kg_m3` (1.225)** (`physics_simulator.simulate_lap`), even
   though the fit can take a measured density. Fit/sim density must match (ρ cancels in the sim only
   if equal) → wire ONE measured per-session density through both.
3. **No apex-speed cornering observable** — cornering is grip-envelope CEILING only. Our −0.89 apex
   pace signal is absent (it's a complementary PACE feature, not an ideal-lap input — see decision D2).

## CORRECTIONS (our work fixes / must validate)
- **A. Coast-drag regen confound.** θ_D is fit from the coast regime (throttle≤0.1 & brake≤0.2) — the
  exact regime our `coast_decouple` proved is MGU-K-regen-dominated (validation corr −0.12 vs real
  drag). θ_D may be systematically biased (within plausibility bounds, so the fallback won't catch
  it), and power inherits it (P = a+roll+drag). **Must validate on real sessions and decide the drag
  source.** This is the riskiest physics question in the integration.
- **B. Simulator density** = fixed (see Gap 2).
- **C. Density VALUE source**: `_get_air_density` trusts a passed weather object; ensure it's our
  measured-barometric-pressure density (the altitude lookup is buggy for Mexico/US — see
  [density-cda-fix] memory), not the ISA-altitude path.

## Decisions to settle (recommendations in **bold**)
- **D1 Drag source — RESOLVED 2026-06-16 (Phase 0):** coast-drag is regen-junk. On 3 real sessions
  the src/physics coast `theta_D`→CdA correlated only **+0.13 pooled (Spearman)** with the trusted
  full-throttle joint-DRS CdA (within the ±0.33 N=10 null), and the `theta_R` intercept came out
  **2.71 m/s² — 77× physical rolling resistance** (absorbing regen; doesn't rescue `theta_D` because
  constant-power regen is ~1/v, not constant). **DECISION: drag source = the full-throttle joint DRS
  fit `CdA_closed` (with identifiability σ), used as a Bayesian prior on `theta_D`; keep coast only for
  a `theta_R` diagnostic.** Enlarges Phase 3 from "tweak" to "swap the drag source." Evidence:
  `.agent-work/445/PHASE0_DRAG_DENSITY_VALIDATION.md`.
- **D1b Density bug — CONFIRMED real (Phase 0):** simulator hardcodes 1.225 and can't take a per-
  session density; the fit defaults to 1.225 unless a weather object is wired. ρ does NOT cancel
  across fit and sim in src/physics (they use different ρ) — at Mexico the sim drag force is off ~1.35×.
  Phase 1 must wire ONE measured density (barometric pressure) through both.
- **D2 Ideal-lap definition** — the engine's ideal lap is the CAPABILITY CEILING (grip envelope). Our
  apex-speed is the REALISTIC/pace observable. *Rec:* **keep the grip-envelope ceiling as the ideal
  lap; add apex-speed as a separate per-car pace feature** (the gap between them = execution/setup —
  itself a useful output). Optionally a second "realistic lap" mode later.
- **D3 Braking** — fixed 6 g constant, friction-circle braking OFF by default. *Rec:* **per-car
  measured braking frontier + friction-circle ON, but LOW priority** (braking is marginal per-team;
  FER the only standout). Sequence it last.
- **D4 Separate package?** *Rec:* **No.** Keep everything in `src/physics`; expose a thin
  `capability` API (per-car force params + covariance + ideal-lap distribution + pace features). A
  separate package would re-create the two-pathway split we're trying to eliminate. If structure is
  needed, a `src/physics/capability.py` facade, not a new package.

## Unified TDD plan — one pathway, test-first, each phase shippable
Target single pathway: **FastF1 cache → calibrated trajectory smoother (port envelope calibration) →
`ParameterEstimator` (forces + covariance) → `PhysicsSimulator.monte_carlo_laps` (covariance-sampled
ideal-lap distribution) → capability API**. Envelope archived. evo_predictor consumes the API later.

- **Phase 0 — Reconcile & validate (spikes, no prod code).** On 2–3 real sessions: compare `src/physics`
  θ_D (coast) to a full-throttle drag cross-check (quantify regen bias); confirm density path end to
  end; freeze D1–D4. Output: decisions locked.
- **Phase 1 — Density correctness.** Tests first: measured-pressure density helper (reuse
  `estimate_air_density` + measured pressure), simulator takes density, **fit↔sim density consistency**
  property, altitude regression (Mexico no longer mis-scales). Implement. Small, high-confidence PR.
- **Phase 2 — Covariance Monte-Carlo (headline).** Tests first: `monte_carlo_laps` variance > 0; draws
  (θ_D,θ_R) and (A0,A2) jointly from the stored covariances; **σ_joint < σ_independent** property (the
  collinearity-abatement result); cornering↔braking share the lateral grip draw; physical clips +
  divergence filter; percentiles sane. Implement `simulate_lap(sample=True)`. This makes the ideal lap
  a real *distribution* — the product.
- **Phase 3 — Drag source / regen correction (per D1).** Tests on synthetic + blessed fixtures; apply
  the chosen correction; re-bless fixtures if θ_D shifts (with documented rationale).
- **Phase 4 — Apex-speed pace feature (per D2).** Port apex extraction as a per-car pace feature in the
  capability API; keep the ceiling ideal lap unchanged. Tests: −0.89-to-pace regression on 2023.
- **Phase 5 — Braking frontier + friction-circle ON (per D3, low priority).** Replace constant braking
  with measured A_b+B_b·v² + honest σ; friction-circle braking on. Tests + fixtures.
- **Phase 6 — Wire pipeline + archive envelope.** Expose capability API; integrate; sweep
  `.agent-work/445/envelope` to archive. Single pathway achieved; no parallel implementations.

## Guardrails
- The fits are locked by unit tests + blessed fixtures (Spain/Monza/Monaco) + known-answer — do not
  regress them; re-bless only with explicit rationale (Phase 3).
- The MC is greenfield (no tests) — pure TDD, we define the contract.
- Physics reads telemetry from the FastF1 cache (sanctioned exception); the DB stays the data SoT for
  the rest of the system.

## Phase 1 — done

**Goal:** Make fit and simulator use one consistent per-session air density.

### Files changed
- `src/utils/environment.py` — Added `moist_air_density_from_pressure(pressure_pa, air_temp_c, humidity_pct)`. Uses the same moist-air formula as the existing `estimate_air_density_kg_m3`, but takes a measured barometric pressure directly instead of deriving it via the ISA altitude model. The existing function is refactored to delegate to this new helper. Exports `ISA_SEA_LEVEL_PRESSURE_PA` for use in tests.
- `src/physics/physics_data_models.py` — Added `fit_air_density: Optional[float] = None` field to `PhysicsParameterSet`. Optional with `None` default preserves backward compatibility. Docstring explains the invariant.
- `src/physics/parameter_estimator.py` — `estimate_parameters` now passes `air_density` (the density it fits at) as `fit_air_density` into the returned `PhysicsParameterSet`.
- `src/physics/physics_simulator.py` — `simulate_lap` reads density as `parameters.fit_air_density if parameters.fit_air_density is not None else self.config.reference_density_kg_m3`. All internal passes (`_forward_pass`, `_backward_pass`, `_compute_speed_caps`) already receive `air_density` as a parameter — no further changes needed.

### Design choice: fit_air_density on PhysicsParameterSet
Attaching `fit_air_density` to the parameter set (rather than threading it as an argument to `simulate_lap`) means the parameter set is self-describing: anyone holding a `PhysicsParameterSet` knows what density the parameters are valid at, without needing a separate out-of-band value. The simulator falls back to `config.reference_density_kg_m3` when unset — preserving backward compatibility for test code that builds parameter sets directly.

### Tests added
- `tests/unit/utils/test_environment.py` (`TestMoistAirDensityFromPressure`, 7 tests): sea-level standard atmosphere (~1.225 kg/m³), plausible range check, Mexico City low-pressure (~0.90 kg/m³ at 78 kPa), monotonicity in pressure and temperature, agreement with dry-air ideal gas at 0% humidity, consistency with `estimate_air_density_kg_m3` at sea level.
- `tests/unit/physics/test_density_consistency.py` (`TestFitAirDensityField` + `TestDensityConsistencyProperty`, 8 tests):
  - `fit_air_density` field is optional (None by default) and stores the value when set.
  - Simulator falls back to config when field is unset.
  - Simulator uses fit density over config (verified by showing two different config densities give identical lap times when `fit_air_density` overrides both).
  - **Consistency property (straight track):** same physical car (same CdA) fitted at sea-level ρ and at Mexico ρ produces the same lap time when fit==sim density (ρ cancels through theta_D). Rel diff < 0.1%.
  - **Bug documentation:** params fitted at Mexico ρ but simulated at sea-level ρ (36% mismatch) produces a lap time diff > 0.5% — confirming drag force is wrong when densities disagree.
  - `ParameterEstimator.estimate_parameters` populates `fit_air_density` on the returned parameter set.

### Regression check
Before: 179 passed, 13 skipped. After: 194 passed, 13 skipped. No regressions in the existing suite. Blessed fixtures (Spain/Monza/Monaco) unchanged — the default-density path (`reference_density_kg_m3=1.225`) is unaffected because the fallback is preserved.

## Phase 2 — done

**Goal:** Implement the covariance-sampled Monte Carlo ideal lap — turning `LapTimeDistribution` from a stub (all lap times identical, std = 0) into a real distribution that propagates the fitted parameters' covariance.

### Files changed
- `src/physics/physics_data_models.py` — Added `valid_fraction: float = 1.0` field to `LapTimeDistribution`. Documents the fraction of Monte Carlo draws that survived the finite/plausibility filter (diverged draws are discarded, not included in the distribution). Default 1.0 preserves backward compatibility.
- `src/physics/physics_simulator.py` — Three changes:
  1. `monte_carlo_laps` completely rewritten: accepts `seed`, `rng`, and `joint` parameters; draws a fresh perturbed parameter set per lap via `_sample_parameters`; runs the existing deterministic `simulate_lap(sample=False)` on the perturbed copy; filters diverged draws (outside [0.5×, 2.0×] the nominal lap time) and reports `valid_fraction`; returns `LapTimeDistribution` with real mean/std/percentiles.
  2. `_sample_parameters(parameters, rng, joint=True)` added — new internal method. Draws perturbed `(theta_D, theta_R)` from `drag_rolling_covariance` (2×2 joint draw when `joint=True`, independent marginals when `joint=False`), draws `(A0, A2)` from `lateral.covariance` (same joint/independent toggle), optionally perturbs the power scale from `theta_P_covariance` (only when the covariance matrix is actually present — no fallback noise). Clips all draws to config plausibility bounds. Returns a new `PhysicsParameterSet`.
  3. Power perturbation: only applied when `theta_P_covariance is not None`. Injecting ad-hoc fallback noise without an empirical covariance would spuriously inflate the distribution; when no power covariance is available, power is left at its nominal value.
- `tests/unit/physics/test_monte_carlo.py` — New test file (9 tests, all greenfield).

### Sampling design
**Joint vs independent.** The lateral parameters (A0, A2) and longitudinal parameters (theta_D, theta_R) are both anti-correlated in typical fits (A0↔A2 corr ≈ −0.9 in real grip fits; theta_D↔theta_R mildly correlated from the coast fit). Drawing jointly from the 2×2 covariance matrix keeps the grip envelope `G(v) = A0 + A2·ρ·v²` tight in the measured speed range — when A0 is drawn high, A2 is drawn low, partially cancelling in the speed-cap formula `v² = A0 / (κ − A2·ρ)`. Independent marginal draws let both parameters wander freely, spuriously inflating the grip variance and thus the lap-time variance. This is the same collinearity-abatement principle from the reference implementation (`.agent-work/445/envelope/ideal_lap_uncertainty.py`).

**Power perturbation.** Only applied when `theta_P_covariance` is present. Perturbation is expressed as a fractional scale `~ Normal(1, σ_frac)` clipped to [0.5, 2.0], where `σ_frac = sqrt(mean(diag(theta_P_covariance))) / mean(theta_P_values)`.

**Divergence filter.** Draws outside the window `[0.5 × t_nominal, 2.0 × t_nominal]` are discarded. A very tight covariance with minor physical perturbations rarely triggers this; a pathological covariance (e.g. the diverged-draw test) may clip significantly. `valid_fraction` is always reported.

### σ_joint < σ_indep test result (headline property confirmed)
Test parameters: track with a single 100 m cornering section (κ = 0.02 m⁻¹); A0 = 30.0 m/s², A2 = 0.001 m²/kg; σ_A0 = 5.0 m/s², σ_A2 = 0.001 m²/kg; corr(A0, A2) = −0.9; longitudinal covariance = 0 (isolates the lateral anti-correlation signal); N = 500 draws; seed = 42.

**σ_joint = 0.2819 s, σ_indep = 0.4375 s, ratio = 1.55.**

The anti-correlation (corr = −0.9) suppresses spurious grip-envelope variance by 35% at the lap-time level, matching the theoretical expectation (the grip frontier `G(v)` is far better determined than either A0 or A2 alone). The joint<independent property held consistently across repeated seeds.

### valid_fraction behavior
- Zero covariance → all draws identical → valid_fraction = 1.0.
- Typical real covariance (σ_A0=5, σ_A2=0.001) → valid_fraction = 1.0 (draws stay within 2× nominal).
- Pathological covariance (σ_A0=10, large off-diagonal) → valid_fraction < 1.0; function still returns finite distribution (falls back to nominal if all diverge).

### Regression check
Before: 187 passed, 13 skipped. After: 196 passed, 13 skipped (+9 new tests). No regressions. Existing `test_simulate_lap_basic` (uses `sample=False`) unchanged and still passes.

## Review nits fixed (2026-06-16)

Addressed all non-blocking nits from PHASE1_REVIEW.md and PHASE2_REVIEW.md.

| # | Nit | File(s) changed | What was done |
|---|-----|-----------------|---------------|
| 1 | **mbar/Pa landmine** | `src/utils/environment.py` | Extended `moist_air_density_from_pressure` docstring with an explicit unit warning (FastF1 `Pressure` is mbar → multiply by 100); added `ValueError` guard for `pressure_pa < 10_000`; added two unit tests (`test_mbar_input_raises_value_error`, `test_pa_input_does_not_raise`). |
| 2 | **theta_R upper clip** | `src/physics/physics_simulator.py` | Changed `max(theta_R_nom, 0.0)` to `np.clip(theta_R_nom, 0.0, cfg.theta_R_max_plausible)` — symmetric with theta_D clipping. |
| 3 | **Invalid test covariance** | `tests/unit/physics/test_monte_carlo.py` | Replaced the non-PSD `[[100,-9],[-9,0.1]]` matrix (det < 0, |corr|=2.85) with a valid PSD covariance built via `_anti_corr_lateral_cov(sigma_A0=10.0, sigma_A2=0.3, corr=-0.9)`. Divergence-filter intent preserved; `RuntimeWarning: covariance is not symmetric positive-semidefinite` eliminated. |
| 4 | **Untested all-diverged path** | `tests/unit/physics/test_monte_carlo.py` | Added `test_all_diverged_returns_nominal_fallback`. Uses `monkeypatch` to guarantee 100% draw divergence (injects A0=1e-9 post-sampling, making all lap times >> 2×nominal). Asserts contract: `valid_fraction=0.0`, `std_lap_time=0.0`, `mean_lap_time==nominal_t`. No code fix needed — the existing fallback (`lap_times=[nominal_t], valid_fraction=0.0`) was already correct. |
| 5 | **theta_P perturbation path untested** | `tests/unit/physics/test_monte_carlo.py` | Added `test_theta_P_covariance_perturbs_power_scale`. Passes a 3×3 diagonal `theta_P_covariance` (σ=50) and asserts that the power scale varies across 200 draws (std > 0.01). Also asserts scales stay within the [0.5, 2.0] clip bounds. |
| 6 | **Dead `sample` docstring** | `src/physics/physics_simulator.py` | Updated `PhysicsSimulator` class docstring: removed the stale "stochastic path (`sample=True`) used by `monte_carlo_laps`" claim; added a clear note that `sample` is retained for API back-compat only and perturbation now happens in `_sample_parameters`. |

**Before:** 176 passed, 13 skipped, 4 warnings.
**After:** 180 passed, 13 skipped, 3 warnings (non-PSD `RuntimeWarning` eliminated).

## Phase 3 — done

**Goal (D1):** Swap the per-car drag source. `theta_D` is now sourced from a
FULL-THROTTLE joint DRS fit; the coast fit is retained ONLY for the `theta_R`
rolling diagnostic (Phase 0 proved coast drag is MGU-K-regen junk).

### Files changed
- `src/physics/longitudinal_fit.py` —
  - Added `MASS_KG = 808.0` (the mass the envelope joint fit used; documents the
    `theta_D = CdA_closed / (2 * MASS_KG)` relationship in the module docstring).
  - Added `DragThrottleFit` dataclass (theta_D + std, CdA_closed/open, shared P,
    3×3 identifiability covariance, bin counts, condition number).
  - Added `fit_drag_throttle(...)` — ports the envelope `drs_joint_fit.fit_drs_joint`:
    upper-edge (p90) frontier bins by speed, DRS-split via `control.drs`, joint
    lstsq for shared `P` + `CdA_closed` + `CdA_open`, honest `s²·(XᵀX)⁻¹`
    covariance. Returns `None` when there is no DRS-open high-speed lever (P/CdA
    degenerate) or too few high-throttle samples — the estimator then falls back.
  - `fit_drag_rolling` (coast) kept unchanged; its `theta_D` output is no longer
    consumed.
- `src/physics/control_alignment.py` — Added `_drs_is_open()` decoding the FastF1
  DRS *status code* correctly: 10/12/14 = open (active), 0/1/8 = closed. The old
  `bool(drs_val)` wrongly reported the common `8` ("available") as open, which
  would have mis-split the joint fit. `control.drs` now means "DRS truly open".
- `src/physics/parameter_estimator.py` — Rewrote the longitudinal block per D1:
  (1) coast fit → `theta_R` diagnostic only (plausibility-checked; dropped to the
  prior if implausible — it no longer triggers *longitudinal* fallback);
  (2) throttle fit → `theta_D` (dominant, and the only vote); (3) plausibility gate
  on the throttle `theta_D` (negative / too-large / non-finite-std → fallback);
  (4) `drag_rolling_covariance = diag(theta_D_var_throttle, theta_R_var_coast)`
  (block-diagonal: the two come from independent regimes), so the Phase-2 MC
  samples the throttle `theta_D` uncertainty correctly; (5) records
  `fit_quality_metrics["theta_D_source"] ∈ {throttle_drs_joint, fallback}`.
  Power trajectory fitting is unchanged but now receives the better `theta_D`.

### Tests (TDD)
- `tests/fixtures/physics/synthetic_straight.py` — added `create_drs_throttle_samples`
  (clean DRS-split full-throttle data with a known CdA_closed/open).
- `tests/unit/physics/test_longitudinal_fit.py` — 6 new `fit_drag_throttle` tests:
  recovers a known CdA → theta_D (<3%) and power (<5%); the `theta_D = CdA/(2·MASS_KG)`
  identity; ignores low-throttle samples; covariance populated & finite; returns
  `None` without a DRS-open lever; returns `None` with too few samples.
- `tests/unit/physics/test_drag_source_throttle.py` — 5 new estimator tests on a
  synthetic session with *regen-inflated coast* + *clean throttle* data: `theta_D`
  comes from the throttle fit (not the 6×-inflated coast value); `theta_R` still
  comes from coast; throttle `theta_D` std feeds `drag_rolling_covariance[0,0]`;
  fallback when no DRS lever; fallback on implausible throttle drag.
- `tests/unit/physics/test_plausibility_fallback.py` — retargeted the longitudinal
  plausibility tests at the new drag source (`fit_drag_throttle`); added a test
  that an implausible *coast* `theta_R` no longer fails the longitudinal fit.
- `tests/unit/physics/test_control_alignment.py` — added DRS-code decode test.

### Blessed fixtures — NO re-bless required
All three fixtures (Spain/Monza/Monaco) were already on the longitudinal fallback
(coast drag was failing plausibility) and **remain on fallback** under the new
throttle source — so every blessed field is byte-identical and the suite is green
with the untouched JSONs. On these fixtures the throttle fit either has no DRS
lever (Spain: VER never opened DRS) or returns a *negative* CdA (Monza −7.5 m²,
Monaco −11.2 m²) because the fixtures' **uncalibrated** kinematics are corrupted
at high speed (speeds to 529 km/h, |ax| to 236 m/s²); the plausibility gate
correctly discards those. The drag swap is proven on clean synthetic data but
cannot be *validated as an improvement* on these fixtures until the calibrated
smoother is wired in and the fixtures are regenerated. Full detail (incl. the
data-quality flag) in `PHASE3_FIXTURE_REBLESS_PROPOSAL.md`.

### Regression check
Guardrail suite (`tests/unit/physics tests/regression/test_physics_regression.py
tests/integration/test_physics_pipeline.py`):
**Before:** 198 passed, 13 skipped. **After:** 210 passed, 13 skipped (+12 net new
tests). No fixtures re-blessed; no other test regressed (the only changed-then-
updated unit tests are the longitudinal plausibility tests, retargeted at the new
drag source as that is the contract D1 deliberately changes).

## Calibration port — done

**Goal (closes the Phase 3 validation gap):** feed the engine CLEAN, calibrated
telemetry. The blessed fixtures' `processed_telemetry` came from an old windowed
estimator with a speed-inflation bug (speeds to 529 km/h); the force fits hit the
plausibility fallback on garbage and could not be validated. This ports the
calibrated, windowless `StintSmoother` into the engine input path and regenerates
the fixtures. Full detail: `CALIBRATION_PORT_RESULTS.md` (re-bless is a PROPOSAL).

### Files
- `src/preprocessing/trajectory/physics_adapter.py` — `smoother_to_processed_telemetry`:
  fitted `StintSmoother` (6-state `[X,Xd,Xdd,Y,Yd,Ydd]`) → `processed_telemetry`
  DataFrame (state cols `px..az` z=0, `speed_ms`, 45 `cov_i_j` upper-triangle
  cols, optional `driver_id`/`lap_number`). Reads `_state_at` mean+cov, adds back
  the linear detrend, densifies >0.5 s gaps with exact Gauss-Markov bridge nodes.
- `scripts/regenerate_physics_fixtures.py` — per fixture: load `raw_telemetry.parquet`
  (no FastF1), extract position (x,y **decimetres→metres ×0.1**) + speed streams,
  calibrate (`session_offset`+`fit_stint_hp`, χ²≈1), fit smoother, run adapter,
  overwrite `processed_telemetry.parquet`. STOP-guards p99 speed ≥ 120 m/s.
- Tests: `tests/unit/preprocessing/trajectory/test_physics_adapter.py` (18, TDD).
- `tests/integration/test_preprocessor_physics_interface.py` — removed the Monza
  speed-inflation xfail (now passes clean). `tests/integration/test_physics_pipeline.py`
  — relaxed an over-strict coast-samples assertion (Monza FP1 has 0 coast, already
  acknowledged by that file's own `test_fallback_status_documented`).

### Result — smoother works, but a DEEPER engine defect remains (STOP reported)
- **Speed-inflation gone.** p99 speed OLD→NEW: spain 112→81, monza 130→95, monaco
  106→78 m/s; χ²_pos≈χ²_spd≈1 on all three. Speed-range interface tests all pass.
- **Drag fit STILL falls back on clean data** (the brief's STOP condition).
  Traced: Spain has **no DRS-open samples** (data limit); Monza/Monaco return
  `negative_theta_D` because the engine derives `a_long` as the noisy per-axis
  acceleration STATE projected on velocity (`a·v̂`), not the smoother's clean
  speed channel. **Proof the drag swap is valid:** re-running the identical joint
  DRS fit with `a_long = d/dt(speed_ms)` gives **Monza theta_D = 0.000634
  (CdA 1.03 m²)** — squarely plausible, DRS-open CdA 0.365 < closed (correct sign).
  So **Phase 3's drag swap is validated on real data at Monza**, conditional on a
  follow-up fixing the engine's `a_long` source. Monaco (street, low-speed) and
  Spain (no DRS) cannot validate drag regardless. → recommend a follow-up issue:
  "engine `a_long` from the speed channel; re-bless Monza drag to fitted."

### Regression check
`tests/regression/test_physics_regression.py
tests/integration/test_preprocessor_physics_interface.py
tests/integration/test_physics_pipeline.py tests/unit/physics`:
**After:** 270 passed, 13 skipped. New adapter suite 18 passed; existing
`tests/unit/preprocessing/trajectory` (17) stay green. Blessed JSONs re-blessed
(Spain lateral + per-fixture metrics changed; theta_D/fallback flags byte-identical
since all three still fall back under the current engine).

## a_long fix — done

**Goal:** Fix the engine's longitudinal acceleration source from the noisy
per-axis Matérn acceleration state (`a·v̂`) to the clean speed channel
(`d/dt(speed_ms)`). This is the single change that unlocks the Monza drag fit.
Full detail: `ALONG_FIX_REBLESS.md`.

### Files changed
- `src/physics/segment_classifier.py` — Added static method `_compute_a_long_series(df)`
  that computes longitudinal acceleration as `np.gradient(speed_ms, t_s)` using the
  `speed_ms` column (derived from the adapter's joint `(vx, vy)` posterior) and the
  monotonic `session_time_ms` time axis (converted ms → s). `classify_samples` calls
  this once before the row loop; each `KinematicSample.a_longitudinal` is set from
  this series. `_compute_long_lat` is unchanged (still provides `a_lat`).
  Backward-compat: if `speed_ms` column or `session_time_ms` is absent, or fewer
  than 2 rows, returns zero array (degenerate-input guard).
- `tests/unit/physics/test_segment_classifier.py` — Added `TestALongSource` class
  with 2 TDD tests: `test_clean_case_both_sources_agree` (zero noise → both sources
  agree ±0.5 m/s²) and `test_noisy_accel_state_speed_derivative_wins` (15 m/s² ax
  noise → old path error 29 m/s², new path error <2 m/s²).
- `tests/unit/physics/test_drag_source_throttle.py` — Updated `_build_session`:
  synthetic telemetry now uses continuous speed integration (each segment is a
  single monotonic run) so `d/dt(speed_ms)` matches the intended physics. All 5
  tests pass unmodified.
- `tests/regression/test_physics_regression.py` — Fixed `_compute_raw_vs_preprocessor_residuals`:
  applied `× 0.1` (dm→m) to raw `x, y` before computing position residuals.
  This corrects the spurious ~4847/9803/6710 "m" RMSE baseline (was decimetres)
  to the physically correct ~3–5 m.
- `tests/unit/preprocessing/trajectory/test_physics_adapter.py` — Two nit fixes:
  (1) `TestCovarianceValidity::test_covariance_symmetric` tightened to assert
  numerical equality against the smoother posterior (not just finiteness);
  (2) `TestErrors::test_unfitted_smoother_raises` tightened to accept only
  `ValueError` (not `AttributeError`).
- `tests/fixtures/physics/regression/*/blessed_params.json` — Re-blessed all three.
  See ALONG_FIX_REBLESS.md for changed fields per fixture.

### Phase 3 milestone: Monza drag swap VALIDATED on real data

| fixture | theta_D | fallback_long | CdA implied | status |
|---|---|---|---|---|
| **monza** | **0.000627** | **0.0 (fitted)** | **1.02 m²** | **milestone** |
| monaco | 0.000148 | 0.0 (fitted) | 0.24 m² | low-speed lever; plausible |
| spain | 0.001 (default) | 1.0 (fallback) | 1.62 (default) | no DRS-open samples |

Monza CdA = 1.02 m² is in the expected 1.0–1.5 m² band. DRS-open < closed
(correct sign). Spain's fallback is a data property (zero DRS-open samples in
the stored FP1 lap), not an engine defect.

### Regression check
Before: 305 passed, 13 skipped.
After: **313 passed, 7 skipped** (+2 a_long TDD tests; 6 formerly-skipped
theta_D/theta_R/theta_P stability tests now run because Monza + Monaco
fallback_longitudinal flipped 1→0).

## SNR gate + hardening — done

**Goal (foundation hardening):** Honest-σ identifiability gate on the drag fit,
docstring correction for `_compute_a_long_series`, two Phase-3 nits.
Full detail: `SNR_GATE_REBLESS.md`.

### Files changed

- `src/physics/physics_config.py` — Added `theta_D_rel_sigma_max: float = 2.0`.
  When `theta_D_std / |theta_D| >= theta_D_rel_sigma_max`, the drag fit self-rejects
  with `fallback_longitudinal = True`, reason `"low_drag_snr"`.  The threshold is
  justified by the Monza / Monaco gap: Monza rel-σ = 0.274, Monaco rel-σ = 3.34.
  Any value in (0.274, 3.34) would discriminate them; 2.0 is chosen conservatively
  to allow fits with up to 2x relative uncertainty.

- `src/physics/parameter_estimator.py` — Extended the longitudinal plausibility
  block with the SNR gate check after existing sign/magnitude/finite-std checks.
  Also updated the throttle-fit call to pass `_out_reason=_throttle_fit_reason` so
  the `"no_drs_lever"` / `"insufficient_throttle_bins"` distinction is propagated.

- `src/physics/longitudinal_fit.py` —
  - Removed dead `drag_rolling_covariance` attribute from `DragThrottleFit` docstring
    (the field was described but never existed on this dataclass; it lives on
    `LongitudinalParameters`).  Added a clarifying Note directing readers to
    `ParameterEstimator`'s cross-regime assembly.
  - `fit_drag_throttle` accepts optional `_out_reason: Optional[list] = None`
    (non-breaking) and now distinguishes two None-return cases:
    `"no_drs_lever"` (zero DRS-open frontier bins) vs
    `"insufficient_throttle_bins"` (some open bins but total < 5).

- `src/physics/segment_classifier.py` — Fixed `_compute_a_long_series` docstring:
  removed the false claim "caller falls back to old `a·v̂` approximation instead";
  corrected to "returns zeros; `a_longitudinal` will be 0.0 for all samples."
  Explains why the `a·v̂` path was not reinstated.  No behavior change.

- `tests/unit/physics/test_plausibility_fallback.py` — 4 new TDD tests for the SNR gate:
  - `test_high_relative_sigma_triggers_fallback`: Monaco numbers (rel-σ = 3.34) → fallback
    with reason `"low_drag_snr"`.
  - `test_low_relative_sigma_keeps_fit`: Monza numbers (rel-σ = 0.27) → fit kept.
  - `test_snr_gate_default_threshold_is_2`: default config value is 2.0.
  - `test_snr_gate_exactly_at_threshold_is_fallback`: rel-σ == 2.0 exactly → fallback.

- `tests/fixtures/physics/regression/monaco_2024_fp1_ver/blessed_params.json` — Re-blessed.
  Monaco reverts to full fallback (theta_D = 0.001, fallback_longitudinal = 1.0,
  fallback_power = 1.0, mean_theta_P = 300.0, theta_D_std = 0.001,
  simulated_lap_time_s = 112.56, max_speed_ms = 58.81).
  Monza and Spain are byte-identical.

### SNR threshold validation

| fixture | theta_D | theta_D_std | rel-sigma | gate result |
|---|---|---|---|---|
| **Monza** | 0.000627 | 0.000172 | **0.274** | PASS — fit kept |
| **Monaco** | 0.000148 | 0.000493 | **3.34** | FAIL — fallback (`"low_drag_snr"`) |

Monaco's 1-σ CdA interval was [−0.55, 1.03] m² (spans negative values).  The gate
correctly self-rejects on SNR < 0.5 (rel-σ > 2).  Monza's CdA = 1.02 m² with
rel-σ = 0.27 is validated: the gate does NOT wrongly reject it.

### Regression check
Before (a_long bless): 313 passed, 7 skipped.
After (SNR gate bless): **314 passed, 10 skipped.**

Delta: +4 new SNR TDD tests pass; Monaco's 3 stability tests re-skip (correct —
comparing fallback defaults against themselves is not a meaningful stability test).
Net: +1 pass, +3 skipped.

## All-seasons era-aware drag — done

**Goal (#445 all-seasons):** Make drag-source selection ALL-SEASONS aware and introduce
a reusable **regulation-era context** as the engine's first piece of era-dependent
input handling.  Drag is the first consumer; braking/power/aero-reg fits may follow.

### RegulationEra abstraction (`src/physics/regulation_era.py`)

`RegulationEra(season)` is a frozen dataclass built via `RegulationEra.for_season(season)`.
All flags are derived from `season` in `__post_init__`; the object is immutable.

| Flag | Meaning | Boundary |
|---|---|---|
| `drs_enabled` | DRS system available | season ≥ 2011 |
| `mguk_regen` | MGU-K harvests energy off-throttle | season ≥ 2014 |
| `coast_drag_trustworthy` (property) | coast decel is pure aero + rolling | `not mguk_regen` |

**Extension pattern** — future flags are added as derived fields in `__post_init__`:

```python
# In __post_init__:
object.__setattr__(self, "ground_effect", self.season >= 2022)
object.__setattr__(self, "kers", self.season in (2009, 2011, 2012, 2013))
```

Then consume in the relevant fitter (e.g. braking frontier in `parameter_estimator.py`):

```python
if era is not None and era.kers:
    # KERS cars have 0.3s bursts under braking; constant model needs adjustment
    ...
```

`RegulationEra` is exported from `src/physics/__init__.py` and its docstring
lists `ground_effect`, `kers`, and braking/power examples explicitly.

### Era-aware drag selection logic

`ParameterEstimator.estimate_parameters` gains an optional `era: Optional[RegulationEra] = None`
parameter.  **`era=None` preserves current behaviour** (treated as modern → throttle path).

Selection logic (in order):

1. **Throttle fit succeeds** (`fit_drag_throttle` returns non-None):
   Apply plausibility + SNR gate.  If it passes → `theta_D_source = "throttle_drs_joint"`.
   If implausible → full fallback (both eras; throttle result is rejected regardless of era).

2. **Throttle fit returns None AND `era.coast_drag_trustworthy`** (≤ 2013):
   Use coast-drag for `theta_D` via `fit_drag_rolling` (already run for `theta_R`).
   Apply the **same** plausibility + SNR gate (`theta_D_rel_sigma_max`).
   If it passes → `theta_D_source = "coast"`.  If implausible → full fallback.

3. **Throttle fit None AND era is None or `era.mguk_regen`** (modern default):
   Full fallback (`theta_D_source = "fallback"`).  This is the existing behaviour.

The `drag_rolling_covariance` assembly is the same in all paths: block-diagonal
`diag(theta_D_std², theta_R_std²)`.  In the coast path, `theta_D_std` comes from
`fit_drag_rolling`'s covariance; `theta_R_std` from the same fit.

`theta_D_source` is now one of `"throttle_drs_joint" | "coast" | "fallback"`.

### Synthetic-only coast validation (pre-2014)

The coast path is validated on **synthetic data only** (no pre-2014 real fixtures in
the engine).  A clean coast session for a 2012-era car (physics-integrated speed,
pure aero + rolling, no regen) recovers the known `theta_D` to < 0.3% error and
`theta_R` to < 1% error.  Real pre-2014 validation requires historical telemetry
not yet in the repository.

### Tests (`tests/unit/physics/test_regulation_era.py`, 16 TDD tests)

- `TestRegulationEraFlags` (9 tests): flag derivation for 2010/2011/2012/2013/2014/2024;
  frozen dataclass; `coast_drag_trustworthy == not mguk_regen` for all seasons 2005–2026.
- `TestEraAwareDragRouting` (3 tests): ≤2013 era routes to coast path; ≥2014 routes to
  throttle path; `era=None` produces identical result to `era=RegulationEra.for_season(2024)`.
- `TestCoastPathKnownAnswer` (2 tests): coast path recovers known CdA and theta_R
  (synthetic-only; documented as such in test docstrings).
- `TestSNRGateBothPaths` (2 tests): high-rel-sigma coast fit triggers `"low_drag_snr"`
  fallback; clean fit passes.

### Regression check
Before: 279 passed, 10 skipped.
After: **295 passed, 10 skipped** (+16 new tests).
2024 blessed fixtures (Spain/Monza/Monaco) byte-identical — `era=None` default path
is unchanged.

## Phase 4 — apex pace feature + capability API — done

**Goal (D2 + D4):** Add the **apex-speed cornering PACE feature** — the dominant
pace-relevant cornering observable (envelope cross-sectional Spearman **−0.89 vs
quali pace**, vs frontier-grip's −0.15) — and expose it through a new
**`capability` API facade** in `src/physics`. The ideal-lap ceiling is left
UNCHANGED (the simulator and grip envelope are not touched); apex-pace is a
SEPARATE per-car relative pace product, not an ideal-lap input.

### Files added
- `src/physics/apex_extract.py` — per-session apex extraction.
- `src/physics/capability.py` — the per-car capability/pace facade (D4).
- `tests/unit/physics/test_apex_extract.py` (12 tests, TDD).
- `tests/unit/physics/test_capability.py` (9 tests, TDD).
- `src/physics/__init__.py` — exports `ApexObservation`, `extract_apex_observations`,
  `ApexPace`, `apex_pace`.

### Per-session apex extraction (`apex_extract.py`)
`extract_apex_observations(lap, ...)` takes a `SegmentedLap` (or a
`processed_telemetry` DataFrame, which it segments on the fly via
`ControlAlignment` + `SegmentClassifier`) and returns a list of frozen
`ApexObservation(v_apex, radius_m, a_lat, on_limit, corner_index)`.

Design (ported from the envelope `apex_extract.py`, working from the engine's
already-classified `corner` regime rather than re-detecting a_lat peaks):
1. Group contiguous runs of `corner`-regime samples; each run = one corner
   traversal (runs shorter than 3 samples are classification flicker, dropped).
2. The apex is the local **speed minimum** within the run (the true on-limit
   apex — matches the envelope's `argmin(v)`), giving `v_apex`.
3. `radius_m = 1/|curvature|` at the apex (falls back to the run's median finite
   radius if curvature is ~0 exactly at the apex node); clipped to a physical
   [8 m, 3000 m] band, with a 5 m/s speed floor to reject pit/slow samples.
4. `on_limit` = apex `a_lat` ≥ a threshold (default 5 m/s², the envelope's
   `A_THR`); OPTIONALLY, when a fitted `LateralParameters` envelope is supplied,
   additionally requires the apex `a_lat` to reach a fraction (default 0.9) of
   that car's `lateral_capability(v_apex)` — reusing the existing grip envelope.

This layer is PER-SESSION/per-driver and is tested directly on the 3 real
fixtures: Spain 15 apexes (v 27–78 m/s, R 31–192 m), Monza 12 (v 14–63 m/s,
R 24–171 m), Monaco 29 (v 11–77 m/s, R 10–196 m) — physically sane, several per
lap, and each with a non-empty on-limit subset. Synthetic single-/two-corner
laps recover the known `v_apex`/`R` (radius rel<5%) and the on-limit flag.

### Capability API facade (`capability.py`)
The module docstring establishes `capability.py` as the integration point where
the engine's three products come together for a car-weekend: (1) ABSOLUTE force
params + covariance (`PhysicsParameterSet`); (2) the covariance-sampled ideal-lap
DISTRIBUTION (the grip-envelope ceiling, `monte_carlo_laps` — unchanged); and
(3) per-car RELATIVE pace features. It documents the extension pattern — future
products (`corner_traversal_pace`, `drag_capability`/`power_capability`,
`ideal_lap_capability`) plug in as sibling functions, keeping cross-car RELATIVE
pace and per-session ABSOLUTE force/ceiling as distinct return types so callers
never confuse the two. (D4: NO separate package — a single facade module.)

First feature: `apex_pace(weekend: Mapping[str, Sequence[ApexObservation]]) ->
dict[str, ApexPace]`. It fits the per-weekend pooled regression
`log v_apex = beta·log R + alpha_car` (shared corner-radius slope `beta`,
per-car intercept dummies, no global intercept — the envelope's design) over the
**on-limit apexes only**, then returns each car's **90th-percentile on-limit
residual** `log v_apex − beta·log R`, **centred to zero mean across the field
that weekend**. `ApexPace(pace, beta, alpha, n_on_limit)`.

### Apex-pace semantics — RELATIVE, not absolute
`pace` is higher = faster cornering. Because the field is centred per weekend
(removing the shared track/grip level), it is a per-car RELATIVE cross-car pace,
NOT an absolute per-session force like drag CdA or the grip envelope, and NOT
the ideal-lap ceiling. `beta ≈ 0.5` recovers the physics `v_apex = sqrt(a_lat·R)`.
The ceiling stays grip-envelope-based; the gap between ceiling and apex-pace is
itself a future execution/setup signal.

### Validation + honest limitation
- **Cross-car aggregation (synthetic, known answer):** a multi-car weekend with
  known per-car α offsets and known β=0.5 → `apex_pace` recovers β (±0.05), the
  per-car ordering, and the centred offsets (±0.03); off-limit apexes are
  correctly filtered out (a car fed slow off-limit junk stays fast); cars below
  `min_apexes` on-limit apexes, or with none, are dropped.
- **Envelope method cross-check (rigor):** feeding the envelope's VALIDATED
  per-team `apex_speed_q90` offsets as a synthetic field reproduces the EXACT
  team ordering and correlates >0.99 with the input offsets — i.e. this code
  reproduces the regression FORM + 90th-pct-on-limit + weekend-centring of the
  validated method. The persisted envelope outcome (`apexq90_sp = −0.89`) is
  asserted as documentation.
- **HONEST LIMITATION:** the validated −0.89 was measured on a full 2023
  **multi-driver SEASON**. The blessed fixtures are **single-driver (VER only)**,
  so the −0.89 itself **cannot be reproduced from the fixtures** — the per-car
  cross-sectional regression needs a field of cars per weekend. Real
  multi-driver SEASON validation (porting the season collection + season-median
  aggregation) is a follow-up; this phase delivers and tests the per-session
  extraction and the per-weekend cross-car fit, the two layers the fixtures CAN
  exercise.

### Guardrails
- The ideal lap / simulator is UNCHANGED: `src/physics` simulator and
  Monte-Carlo tests pass byte-for-byte; no fixture re-blessed by this phase
  (the only fixture/`synthetic_straight.py` deltas in the working tree pre-date
  Phase 4). This phase ADDS modules and tests only.

### Regression check
Guardrail suite (`tests/unit/physics tests/regression/test_physics_regression.py
tests/integration/test_physics_pipeline.py`):
**Before:** 238 passed, 10 skipped. **After:** 259 passed, 10 skipped
(+21 new tests: 12 apex-extract + 9 capability). No regressions.

## Phase 5 — braking frontier + friction circle — done

**Goal (D3):** Replace the constant braking (`max_braking_ms2` = 60 m/s², `apply_braking_friction=False`)
with a per-car MEASURED braking frontier, and turn the friction-circle braking ON when a frontier is
fitted.

**HONEST CAVEAT (baked in):** braking is MARGINAL per-team (~0 Spearman with quali pace; FER the lone
standout).  A_b (the v→0 intercept) is EXTRAPOLATION-LIMITED (brake samples stop ~99 km/h; σ_Ab≈29%;
A_b↔B_b corr ≈−0.85).  This improves ideal-lap REALISM but is a WEAK per-car discriminator, and the
SNR gate ensures it self-rejects when poorly identified.

### Files added
- `src/physics/braking_fit.py` — `fit_braking_frontier(brake_samples, ...)` → optional
  `BrakingFrontier(a_b, b_b, a_b_std, b_b_std, covariance, n_bins, n_samples, v_lo_ms)`.
  Model `a_brake(v) = A_b + B_b·v²` in m/s². p95 upper-edge frontier bins, honest
  covariance `s²·(XᵀX)⁻¹` (mirrors `LongitudinalFit.fit_drag_throttle` pattern).
  Returns `None` when fewer than `min_bins=4` speed bins have ≥`min_pts_per_bin=8` samples.
- `tests/unit/physics/test_braking_fit.py` — 20 TDD tests: known-answer recovery (<20%
  error on A_b, B_b), covariance 2×2/PSD/finite, SNR gate passes/fails appropriately,
  `BrakingFrontier.a_brake()` helper.
- `tests/unit/physics/test_braking_simulator.py` — 14 TDD tests: null-path byte-identity,
  frontier-mode lap-time change, friction-circle formula, MC variance contribution.

### Files changed
- `src/physics/physics_data_models.py` — Added `BrakingParameters(a_b, b_b, covariance)`
  frozen dataclass; added `braking: Optional[BrakingParameters] = None` field to
  `PhysicsParameterSet` (default None → backward compatible).
- `src/physics/physics_config.py` — Added `a_b_rel_sigma_max: float = 2.0` (SNR gate
  threshold for the braking frontier, mirrors `theta_D_rel_sigma_max`).
- `src/physics/parameter_estimator.py` — Fits braking frontier from `straight_brake`
  regime; applies SNR gate (`a_b_std / max(|a_b|, 1e-12) >= a_b_rel_sigma_max` →
  None); records `braking_source` in `fit_quality_metrics`
  (`"frontier"` | `"constant"`); passes `braking=braking_params` to `PhysicsParameterSet`.
- `src/physics/physics_simulator.py` — `_compute_braking_decel` has two modes:
  **Frontier mode** (when `parameters.braking` is not None): uses `a_brake(v)` clamped to
  `[0, max_braking_ms2]`; in corners applies friction-circle
  `sqrt(max(a_brake² − a_lat², 0))`.  **Constant mode** (when `braking=None`): byte-identical
  to pre-Phase-5 (constant, friction OFF by default).  `_sample_parameters` extended to draw
  `(a_b, b_b)` jointly from the 2×2 braking covariance (same pattern as lateral A0/A2 draws),
  clipped to physical bounds.
- `src/physics/__init__.py` — Exports `BrakingFrontier`, `fit_braking_frontier`,
  `BrakingParameters`.

### Per-fixture braking fit result
All three blessed fixtures (Spain/Monza/Monaco) **fall back to constant** because the
single-lap brake sample counts (34–48 total) don't populate ≥4 bins with ≥8 points each.
Lap times and all other blessed fields are **byte-identical** — NO re-bless required.
This is the expected outcome given the consolidation's extrapolation-limited finding.

Full per-fixture detail: `.agent-work/445/PHASE5_REBLESS.md`.

### Monza braking — real-telemetry assessment
Single FP1 lap self-rejects (insufficient bin density). On the full-season collection
(consolidation `season_brake2.json`), RBR showed A_b ≈ 1.9 g = 18.6 m/s² — physically
plausible (15–30 m/s² band documented in the brief). The single-lap fixture lacks
data density for a frontier; multi-lap collections will produce valid fits.

### Regression check
Guardrail suite (`tests/unit/physics tests/regression/test_physics_regression.py
tests/integration/test_physics_pipeline.py`):
**Before:** 259 passed, 10 skipped. **After:** 293 passed, 10 skipped
(+34 new tests: 20 braking-fit + 14 braking-simulator). No regressions.
Blessed fixtures byte-identical — no re-bless.
