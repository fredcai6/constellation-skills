# Implementer Handoff

## Gate
`g3` — Stint estimator (five-view, lateral-lead decay fit)

## Task

Implement `src/physics/layer2/stint_estimator.py`: a per-stint five-view physics estimator with age-decay extension. Uses `RaceStintData` from g2 (`session_race.py`). Produces `StintEstimate` objects consumed by g4 (store).

The decay model (Fit B): `frontier(v, age) = g0 * exp(-k * age) + b_aero * v²`
where:
- `g0` = grip/accel at tyre age reference (units match the view's observable)
- `k` = exponential decay rate per lap (1/lap) — injectable prior
- `b_aero` = aero/speed term (speed-squared coefficient)
- `age` = ABSOLUTE tyre_life from lap_times (NOT normalized)

**Lateral-lead**: lateral is the primary decay instrument. Traction second. Braking / PowerDrag / Coast are honest-null (k=0 expected; standard 2-param fit over full stint pool).

Also write `tests/unit/physics/layer2/test_stint_estimator.py` with mocked unit tests.

## Protected Intent

The existing five-view qual path (`session_estimator.py`, `estimate_session`, `EstimateStore`, `BrakingView`, `LateralView`, `TractionView`, `PowerDragView`, `CoastView`) is **completely untouched**. The decay fitting is NEW code in `stint_estimator.py` only.

All five views produce honest estimates — if a view cannot fit (insufficient samples, degenerate frontier), return `None` for that view; do NOT raise.

## Test Mode

TDD required. Write tests that mock `RaceStintData` inputs (synthetic telemetry, no real DB/store required). Tests must pass with `py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v`.

## Close Criteria

- `from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate` imports cleanly
- `estimate_stint(stint_data: RaceStintData) -> StintEstimate` works
- `StintEstimate` has fields for each of five views: `lateral_decay`, `traction_decay`, `braking`, `power_drag`, `coast` (each may be None for honest-null)
- `lateral_decay` is the PRIMARY result: `LateralDecayResult(g0, k, b_aero, covariance_3x3, ...)`
- Decay fit uses ONE-SIDED upper-frontier loss (frontier must bound the cloud from above) — same philosophy as existing `fit_frontier` but non-linear in (g0, k)
- `k >= 0` enforced: decay rate cannot be negative (tyres can only degrade, not improve spontaneously per lap within a stint)
- Injectable `(k_mu, k_sigma)` prior with default `k_mu=0.01, k_sigma=0.02` (weakly-informative, units=1/lap)
- Age covariate = ABSOLUTE tyre_life (NOT per-stint normalized)
- Braking/PowerDrag/Coast: standard 2-param fit (no age covariate) over full stint pool; return `k=None` for those
- Honest-null: any view returning None is fine (sparse stints, narrow speed range, etc.)
- `py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v` passes

## Allowed Scope

- `src/physics/layer2/stint_estimator.py` — NEW file
- `tests/unit/physics/layer2/test_stint_estimator.py` — NEW test file
- `src/physics/layer2/__init__.py` — only if __all__ exists and other modules listed

## Specific Exclusions

- ALL existing view classes (`BrakingView`, `LateralView`, `TractionView`, `PowerDragView`, `CoastView`) — do NOT modify
- `src/physics/layer2/estimate_store.py` — do NOT modify
- `src/physics/layer2/session_estimator.py` — do NOT modify
- `src/physics/session_fit.py` — do NOT modify
- `src/physics/layer2/frontier_fit.py` — do NOT modify
- Any existing test file — do NOT modify

## Constraints

- No imports from `src/evo_predictor/`, `src/latent_power/`, `src/compound_prior/`
- `constraint:physics_region_no_evo_import` enforced
- The decay fit is a NEW non-linear optimizer (scipy.optimize.minimize or curve_fit with one-sided loss) — it does NOT reuse the linear `fit_frontier` function for the decay term
- For braking/powerdrag/coast: reuse `fit_frontier` (no age covariate) over full stint's pooled samples — these are 2-param fits
- `k >= 0` enforced: use bounds in optimizer or post-clip
- Age covariate = ABSOLUTE tyre_life (field `tyre_life` from `RaceStintData`, which is already absolute and NOT normalized)
- Bootstrap covariance for decay views: resample (driver, lap) pairs; fit decay model on each resample; covariance = np.cov of bootstrap parameter estimates. Minimum 20 bootstrap rounds.
- Python: `py`, not `python`; tests: `py -m pytest`

## Map Anchors (inbound)

- **Structural:** `src/physics/layer2/stint_estimator.py` (NEW); `src/physics/layer2/session_race.py` (g2 output — `RaceStintData` is the sole input); `src/physics/layer2/frontier_fit.py` (reused for braking/powerdrag/coast 2-param fits)
- **Capability:** `RaceStintData.processed_df` — contains all smoother-processed lap samples with 'lap_number' column; columns include at minimum: `a_lat` (lateral accel m/s²), `a_long` (longitudinal accel m/s²), `v` (speed m/s), `theta` (grade angle rad), `regime` or equivalent regime labels
- **Constraints/assumptions:** `BrakingView/LateralView/TractionView/PowerDragView` NOT called directly from stint_estimator (no age covariate in them); decay fit is separate logic
- **Decision anchors:** lateral-first (primary signal, Admiral ruling); braking-null is expected fine result; injectable prior is the W3 seam (don't hardcode k per-compound)
- **Evidence expectations:** `lateral_decay.g0 > 0` for VER Bahrain SOFT stint 1; `lateral_decay.k >= 0`; 3x3 covariance positive-definite; braking 2-param fit produces `brake_decel_ms2 > 0`

## Required Data Interface

Input: `RaceStintData` from `src/physics/layer2/session_race.py` — use it exactly as-is.

Key fields consumed:
```python
stint.processed_df     # columns: a_lat, a_long, v, theta, lap_number (at minimum)
stint.tyre_life        # ABSOLUTE tyre_life per clean lap, shape [n_clean]
stint.lap_nums         # race lap numbers, shape [n_clean]
stint.mass_kg          # per-lap mass (kg), shape [n_clean]
stint.rho              # air density
stint.compound         # tyre compound (SOFT/MEDIUM/HARD)
stint.driver           # driver code
stint.gp               # circuit
stint.year             # season
```

To attach per-sample age: join `processed_df.lap_number` → `tyre_life[lap_nums == lap_number]`.

## Required Outputs

### `LateralDecayResult` dataclass

```python
@dataclass(frozen=True)
class LateralDecayResult:
    g0: float                    # grip at age reference (g-units, dimensionless)
    k: float                     # decay rate (1/lap, >= 0)
    b_aero: float                # aero grip coefficient (1/(m/s)^2, >= 0)
    covariance: np.ndarray       # 3x3 bootstrap covariance of (g0, k, b_aero)
    n_samples: int               # total samples used
    n_laps: int                  # clean laps in decay fit
    age_obs: np.ndarray          # per-sample absolute tyre_life
    mu_obs: np.ndarray           # per-sample de-conflated grip coefficient
    frontier_at_obs: np.ndarray  # g0*exp(-k*age) + b_aero*v^2 per sample
    utilisation: np.ndarray      # gap below frontier (>= 0)
    k_prior_mu: float            # injected prior mean for k
    k_prior_sigma: float         # injected prior sigma for k
```

### `TractionDecayResult` dataclass (analogous)

```python
@dataclass(frozen=True)
class TractionDecayResult:
    a0: float                    # mechanical traction at age reference (m/s^2)
    k: float                     # decay rate (1/lap, >= 0)
    b_aero: float                # aero traction coefficient (1/(m/s)^2, >= 0)
    covariance: np.ndarray       # 3x3 bootstrap covariance of (a0, k, b_aero)
    n_samples: int
    n_laps: int
    age_obs: np.ndarray
    a_drive_obs: np.ndarray      # de-conflated drive-grip obs
    frontier_at_obs: np.ndarray
    utilisation: np.ndarray
    k_prior_mu: float
    k_prior_sigma: float
```

### `StintEstimate` dataclass

```python
@dataclass(frozen=True)
class StintEstimate:
    year: int
    gp: str
    driver: str
    compound: str
    stint_num: int
    
    # PRIMARY (decay views, lateral-first):
    lateral_decay: Optional[LateralDecayResult]   # None if insufficient samples
    traction_decay: Optional[TractionDecayResult] # None if insufficient samples
    
    # COMPLETENESS (standard 2-param, no age covariate — k likely null):
    braking: Optional[BrakingViewResult]           # from BrakingView.fit, pooled samples
    power_drag: Optional[PowerDragResult]          # from PowerDragView.fit, pooled samples
    coast: Optional[CoastViewResult]               # from CoastView.fit, pooled samples
    
    # Metadata:
    cumulative_track_laps: int   # from RaceStintData
    tyre_life_start: int
    tyre_life_end: int
    n_clean_laps: int
    rho: float
    k_prior_mu: float            # injected prior used
    k_prior_sigma: float
```

### `estimate_stint` function

```python
def estimate_stint(
    stint: RaceStintData,
    *,
    k_prior_mu: float = 0.01,    # weakly-informative default; W3 will supply pooled compound prior
    k_prior_sigma: float = 0.02,
    n_boot: int = 30,
    min_samples: int = 20,       # per _MIN_SAMPLES convention
) -> StintEstimate:
    """Fit all five views on one race stint with age-decay for lateral+traction.
    
    Lateral view is the primary decay instrument (Admiral ruling, #443 finding).
    Traction second. Braking/PowerDrag/Coast use standard 2-param frontier fit
    (no age covariate); honest-null k expected for those.
    
    Parameters
    ----------
    stint:
        RaceStintData from session_race.load_race_stints.
    k_prior_mu, k_prior_sigma:
        Injectable prior on the decay rate k (1/lap).
        Default is weakly informative; W3 (#511) will supply pooled
        per-compound priors at cross-session pooling time.
    n_boot:
        Bootstrap resample rounds for covariance estimation.
    min_samples:
        Minimum pooled samples to attempt a view fit.
    """
```

## Decay Fitting Algorithm (for lateral and traction)

The decay model is NON-LINEAR in k — `fit_frontier`'s linear design cannot be reused for the decay term.

**Step 1: Extract regime samples**

For lateral: use corner-regime samples from `processed_df`. Regime column may be labeled 'regime' with values like 'corner'. Fallback: samples where `|a_lat| > 3.0 m/s^2` and `|a_long| < 1.0 m/s^2`.

For traction: throttle-on accelerating samples. Regime column 'straight_throttle' or similar. Fallback: samples where `a_long > 0.5 m/s^2`.

**Step 2: Attach age covariate**

For each sample in the regime, look up `tyre_life` for its `lap_number`:
```python
# Build lap_num -> tyre_life map
tl_map = dict(zip(stint.lap_nums, stint.tyre_life))
# For each sample in regime df:
age = tl_map.get(int(row.lap_number), np.nan)
```
Drop samples with NaN age.

**Step 3: De-conflate to observable**

For LATERAL: same de-conflation as `LateralView.fit` — `mu_obs = |a_lat| / (g * cos(theta))` for flat corners (or banked formula if banking available; use flat formula as default for simplicity in race context since terrain profile may not be available)

For TRACTION: de-conflate to `a_drive_obs = a_long + cda_cold * rho * v^2 / (2 * mass) + theta_R + g * sin(theta)` where `cda_cold = 1.2` (cold prior, same as session_estimator). Mass = `stint.mass_kg` per lap (map by lap_number to get per-sample mass).

**Step 4: Fit the decay model with one-sided loss**

```python
def _fit_decay(v, age, obs, *, k_mu, k_sigma, n_boot, min_samples):
    """
    Fit: frontier(v, age) = p0 * exp(-p1 * age) + p2 * v^2
    where p0=g0/a0, p1=k, p2=b_aero
    
    One-sided upper-frontier loss: 
      L(params) = sum(w_above * relu(obs - frontier)^2 + w_below * relu(frontier - obs)^2)
                + MAP_penalty_on_k
    where w_above >> w_below (frontier must bound the cloud from above).
    """
```

Suggested loss weights: `w_above = 10.0`, `w_below = 0.3` (same as `fit_frontier`).

MAP prior on k: add `((k - k_mu) / k_sigma)^2` to the loss (Gaussian MAP regularization).

Optimizer: `scipy.optimize.minimize` with bounds:
- `p0 > 0` (grip must be positive)
- `p1 >= 0` (k >= 0: no spontaneous recovery)
- `p2 >= 0` (aero term non-negative)

Initial guess: `p0 = np.percentile(obs, 90)`, `p1 = k_mu`, `p2 = 0.0`

**Step 5: Bootstrap covariance**

Resample `(v, age, obs)` rows with replacement, fit the decay model on each resample.
Covariance = `np.cov(np.column_stack(all_boot_params).T)` (3x3 matrix).
Clamp: replace any NaN/Inf covariance with a fallback diagonal based on the point-estimate scale.

**For braking/powerdrag/coast**: use existing BrakingView.fit, PowerDragView.fit, CoastView.fit directly on ALL samples from `processed_df` (pooled across all clean laps). Mass must be per-sample (map from lap_number). Use `quali_mass(year)` as a fallback if per-sample mass mapping fails (NOT preferred but acceptable). Use cold prior (GaussianPrior2.cold()).

The existing views require a `BrakingFrontierData`-style input — reconstruct from `processed_df` columns (v, a_long, sigma_kin, theta) pooled across all laps. `sigma_kin` may be approximated as `np.full_like(v, 0.1)` if not in the processed_df (check first).

## Regime Extraction Notes

Check what columns `processed_df` actually contains by reading `smoother_to_processed_telemetry` output. Common columns: `v` (or `speed`), `a_long` (or `accel_long`), `a_lat` (or `accel_lat`), `theta`, `lap_number`, possibly `regime`. If `regime` is present, use it. If not, use threshold filters (described above).

Inspect the columns in the FIRST clean lap's processed_df before committing to column names.

## Required Evidence

- Test output: `py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v` all passing
- Import smoke: `py -c "from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate; print('ok')"`
- At minimum one test verifying `LateralDecayResult.k >= 0` constraint
- At minimum one test verifying covariance is 3x3 and close-to-positive-definite (eigenvalues >= -1e-6)
- Test verifying braking, power_drag, coast are attempted (may return None, but must not crash)

## Verification Commands

```bash
py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v
py -c "from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate; print('ok')"
```

## Suggested Model Tier

`sonnet` — physics-aware new module; decay fit algorithm is specified in detail; bootstrap is standard pattern

## Authority

- Decay fit algorithm (one-sided loss, MAP prior on k, bounds): DECIDED — implement as specified
- Lateral-first ordering: DECIDED by Admiral
- k >= 0 hard constraint: DECIDED
- Injectable prior seam at (k_mu, k_sigma): DECIDED — W3 seam
- Age covariate = ABSOLUTE tyre_life: DECIDED
- Honest-null (None return from any view): DECIDED — never raise for insufficient samples
- Regime extraction fallback (threshold filters): OK if 'regime' column not present
- CdA cold prior = 1.2 for traction de-conflation: DECIDED (inherit from session_estimator._CDA0)
- Per-sample mass from stint.mass_kg: DECIDED — map by lap_number; document if mass approximation used

## Stop Conditions

Stop and return if:
- `processed_df` from RaceStintData is missing columns needed for de-conflation and no reasonable fallback exists
- `scipy.optimize.minimize` consistently fails to converge even with varied initial guesses (surface as a finding, do not crash)
- The existing view classes (BrakingView etc.) require unavailable data that can't be reasonably approximated

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used (especially column names found in processed_df), stop conditions hit, out-of-scope observations, workflow feedback.
