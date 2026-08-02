# Reviewer Handoff Result — Gate g3: Stint estimator review

## REVIEW_RESULT: APPROVE

**Commit reviewed:** `ea7985ec`
**Branch:** `feat/563-race-fit-path`
**Files added:** `src/physics/layer2/stint_estimator.py` (767 lines), `tests/unit/physics/layer2/test_stint_estimator.py` (235 lines)

---

## Per-Check Findings

### 1. Import smoke
PASS. `from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate` returns `ok`.

### 2. StintEstimate fields
PASS. All required fields present on the frozen dataclass:
`lateral_decay`, `traction_decay`, `braking`, `power_drag`, `coast`, `year`, `gp`, `driver`, `compound`, `stint_num`, `cumulative_track_laps`, `tyre_life_start`, `tyre_life_end`, `n_clean_laps`, `rho`, `k_prior_mu`, `k_prior_sigma`.

### 3. LateralDecayResult fields
PASS. All required fields present: `g0`, `k`, `b_aero`, `covariance` (shape (3,3)), `n_samples`, `n_laps`, `age_obs`, `mu_obs`, `frontier_at_obs`, `utilisation`, `k_prior_mu`, `k_prior_sigma`.

### 4. One-sided loss (w_above >= 5, w_below <= 1)
PASS. `_W_ABOVE = 10.0` (line 59), `_W_BELOW = 0.3` (line 60). In `_decay_loss`, `residual = obs - frontier`; residual > 0 (observation above frontier) is penalized at W_ABOVE=10, residual < 0 (below) at W_BELOW=0.3. Both constraints met.

### 5. k >= 0 enforced
PASS. `_fit_decay_3param` (line 345): `bounds = [(1e-6, None), (0.0, None), (0.0, None)]`. L-BFGS-B enforces k >= 0 structurally. Same bounds used in `_bootstrap_covariance` (line 296). No post-clip needed.

### 6. Injectable (k_prior_mu, k_prior_sigma) stored on result
PASS. Stored on `LateralDecayResult` (lines 443-444), `TractionDecayResult` (lines 539-540), and `StintEstimate` (lines 765-766). Propagation seam intact.

### 7. Age = ABSOLUTE tyre_life
PASS. `tl_map` is built directly from `stint.tyre_life` with no normalization (lines 700-703). Module docstring explicitly states "ABSOLUTE tyre_life from RaceStintData (do NOT subtract the per-stint minimum)". `test_age_is_absolute` verifies `age_obs.min() >= tyre_life_start` (e.g., 4.0, not 0). Evidence note age_obs.min()=4.0 is consistent with this.

### 8. No existing file modified
PASS. `git diff HEAD~2 HEAD --name-only` shows 4 files — all new additions across 2 commits. `ea7985ec --stat` shows only insertions (767 + 235 lines, 0 deletions). `HEAD~1` likewise adds only `session_race.py` and `test_session_race.py` as new files. Zero diff on any existing file.

### 9. No forbidden imports
PASS. Top-level imports: `dataclasses`, `typing`, `numpy`, `scipy.optimize`, and `src.physics.layer2.{braking_view, coast_view, params, power_drag_view, traction_view}`. Inline imports (inside functions): `pandas`, `src.physics.layer2.frontier_fit`. No `evo_predictor`, `latent_power`, `compound_prior`, or `fastf1`.

### 10. a_long / a_lat derivation
PASS. Lines 248-250:
```
a_long_raw = (ax * vx + ay * vy) / safe_speed         # dot product: tangential
a_lat_signed = (vx * ay - vy * ax) / safe_speed       # 2D cross product: normal
a_lat_abs = np.abs(a_lat_signed)
```
This matches the specification exactly. The 2D cross product `vx*ay - vy*ax` gives the z-component of v x a; dividing by speed gives the normal (centripetal) acceleration magnitude. Physically correct.

---

## Constraints Verified

- **Non-linear optimizer**: `_fit_decay_3param` uses `scipy.optimize.minimize` with the custom `_decay_loss`. `frontier_fit.ridge_peak` is used only to detect the crossover speed for traction filtering — not for the decay fit itself.
- **k >= 0**: Enforced by L-BFGS-B bounds `(0.0, None)` on the k parameter.
- **Age = absolute tyre_life**: No normalization applied anywhere in the decay path.
- **w_above >> w_below**: 10.0 >> 0.3.
- **Injectable prior as seam**: Stored verbatim on both decay results and StintEstimate for W3 propagation.

---

## Blockers

None.

---

## Out-of-Scope Observations (triage candidates)

**obs-1 (minor):** `TractionView` and `TractionViewResult` are imported on line 52 but never used in the file. `TractionDecayResult` is the custom dataclass used instead. Dead import — harmless but could be cleaned up.

**obs-2 (design note):** `_CDA0 = 1.2` m² cold-start drag area is used in traction de-conflation. In race conditions with higher downforce levels and unknown DRS state, this will introduce systematic error into `a_drive_obs`. The docstring acknowledges the flat-ground/cold-start approximation; acceptable for the race-stint Phase-C context where no cross-view posterior is available to pin CdA.

**obs-3 (minor):** `sigma_kin = np.full(len(speed), 0.1, dtype=float)` is a uniform noise floor passed to `BrakingView`. Not varied per sample. Acceptable for the initial implementation.

---

## Workflow Feedback

Implementation is clean and well-documented. The module docstring fully specifies all design constraints (flat-ground, DRS-closed assumption, absolute age, one-sided loss weights), which made code verification straightforward. The 10 unit tests cover the critical behavioral contracts (k >= 0, g0 > 0, covariance shape/symmetry, honest-null sparse behavior, prior injection, age absoluteness, field types) without redundancy. The ~200s test runtime is expected given 30-round bootstrap per scipy.optimize run and was clearly communicated in the handoff.
