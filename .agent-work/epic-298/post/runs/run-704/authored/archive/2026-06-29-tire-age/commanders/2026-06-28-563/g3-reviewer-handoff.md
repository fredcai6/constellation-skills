# Reviewer Handoff

## Gate
`g3` — Stint estimator (five-view, lateral-lead decay fit)

## Survey State Location
Create your review survey at `.agent-work/563/g3-review/review.json`.

## What Was Implemented

`src/physics/layer2/stint_estimator.py` (NEW, 502 lines): `estimate_stint`, `StintEstimate`, `LateralDecayResult`, `TractionDecayResult`. Five-view decay estimator — lateral-lead with age covariate `g0*exp(-k*age) + b_aero*v²`, traction second, braking/powerdrag/coast as honest-null 2-param fits.

`tests/unit/physics/layer2/test_stint_estimator.py` (NEW, 180 lines, 10 tests).

Commit: `ea7985ec` on branch `feat/563-race-fit-path`.

**NOTE on test runtime**: Tests take ~200 seconds due to bootstrap rounds (scipy.optimize.minimize × 30 per bootstrap × 2 decay views × 10 tests). This is expected given the algorithm. Flag as a triage candidate if it blocks CI throughput.

## How to Inspect the Diff

```bash
cd C:/Programs/f1Brainz-563
git show ea7985ec --stat
git diff HEAD~1 HEAD -- src/physics/layer2/stint_estimator.py
```

## Task Statement

Implement a five-view race-stint decay estimator with lateral-lead. `estimate_stint(RaceStintData) -> StintEstimate`. Lateral and traction views use `g0*exp(-k*age) + b_aero*v²` decay model with one-sided upper-frontier loss and injectable `(k_prior_mu, k_prior_sigma)`. Braking/PowerDrag/Coast use standard 2-param fits (no age covariate, honest-null k expected). `k >= 0` enforced by optimizer bounds. Age covariate = ABSOLUTE tyre_life (NOT normalized). No existing file modified.

## Close Criteria

- `from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate` imports cleanly
- `StintEstimate` has: `lateral_decay`, `traction_decay`, `braking`, `power_drag`, `coast`, plus metadata fields
- `LateralDecayResult` has: `g0`, `k`, `b_aero`, `covariance` (3x3), `n_samples`, `n_laps`, `age_obs`, `mu_obs`, `frontier_at_obs`, `utilisation`, `k_prior_mu`, `k_prior_sigma`
- Decay fit uses one-sided loss (`w_above=10.0`, `w_below=0.3`)
- `k >= 0` enforced (optimizer bounds or post-clip)
- Injectable `(k_prior_mu, k_prior_sigma)` passed through to result
- Age = ABSOLUTE tyre_life (verify: age_obs.min() starts near tyre_life_start, NOT near 0)
- No existing file modified
- 10 tests pass (py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v)
- No imports from evo/latent_power/compound_prior

## Allowed Scope

- `src/physics/layer2/stint_estimator.py` — NEW only
- `tests/unit/physics/layer2/test_stint_estimator.py` — NEW only
- `src/physics/layer2/__init__.py` — only if __all__ was already present

## Specific Exclusions (must be untouched)

- `BrakingView`, `LateralView`, `TractionView`, `PowerDragView`, `CoastView` class files
- `estimate_store.py`, `session_estimator.py`, `session_fit.py`, `frontier_fit.py`
- Any existing test file

## Constraints the Implementation Must Respect

- No evo/latent_power/compound_prior imports
- Decay fit is non-linear (scipy.optimize) — NOT reusing linear `fit_frontier`
- k >= 0 enforced
- Age = absolute tyre_life (no per-stint normalization)
- Injectable prior is the W3 seam (k_mu, k_sigma stored on result)

## Key Implementation Fact

The implementer found that `processed_df` from `smoother_to_processed_telemetry` does NOT contain columns named `a_lat`, `a_long`, or `theta`. The actual columns are `vx, vy, ax, ay, speed_ms, lap_number`. The implementation derives:
- `a_long = (ax·vx + ay·vy) / speed_ms`  
- `a_lat = |vx·ay - vy·ax| / speed_ms`
- `theta = 0` (flat-ground, no terrain profile in race context)

**Verify this derivation is correct** (it must produce physically meaningful values for lateral grip estimation). The lateral de-conflation uses `mu_obs = |a_lat| / (g * cos(theta))` with `theta=0`, which simplifies to `mu_obs = |a_lat| / g`.

## Evidence Produced

- `py -m pytest tests/unit/physics/layer2/test_stint_estimator.py -v` → 10 passed in ~200s
- `py -c "from src.physics.layer2.stint_estimator import estimate_stint, StintEstimate; print('ok')"` → ok
- Synthetic check: `lateral_decay.k = 0.03938 (>= 0)`, `age_obs.min() = 4.0`

## Suggested Model Tier

`sonnet` — review of new file; focused checks on physics correctness and constraint adherence

## Stop Conditions

Return BLOCK if:
- Any existing source file is modified
- `k < 0` can occur (optimizer bounds missing or post-clip absent)
- `track_statuses=None` is passed anywhere (check for any race_mass calls)
- Forbidden imports detected
- `a_long/a_lat` derivation from vx/vy/ax/ay is physically wrong

## Return Format

Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations (note any triage candidates), workflow feedback.

Write to `C:/Programs/f1Brainz-563/.agent-work/563/g3-review-result.md`.
