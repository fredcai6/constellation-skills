# Calibration Ell Floor Fix — Diagnosis and Implementation

**Updated 2026-06-16: supersedes the original fix after CHANGES-REQUESTED review.**
See CALIBRATION_ELL_FLOOR_REVIEW.md for the full review findings.

---

## Root Cause (unchanged)

`fit_stint_hp` in `src/preprocessing/trajectory/calibration.py` uses a two-stage HP search:

1. **Coarse grid search** (`_grid_search`): sweeps `ell` over `[1.0, 1.4, 1.8, 2.4, 3.2, 4.5]` s.
2. **Local refinement** (`_local_refine`): tries `best_ell * 0.8`, `best_ell`, `best_ell * 1.25`.

On short, sparse Q-laps (80–100 s, 2 Hz), the chi² held-out surface has only ~45 held-out
samples per class — too few to reliably discriminate ell values.  The chi² objective is
*locally flat*, and ell=1.0 (or smaller after the 0.8× step) can appear marginally better
than larger values simply because it interpolates noise to hit held-out points.  With
ell < sample spacing (~0.5 s at 2 Hz), the Matérn kernel resolves sub-sample correlations,
over-fitting noise and producing unphysical velocity overshoot.

The independent review confirmed: with the old fixed floor of 1.0 s, ell=1.0 still wins on
seeds 7 and 555 (p99=70.7 and 71.5 m/s vs truth 42.4 m/s — 1.67–1.69× inflation).  The
chi² GRID SEARCH itself preferred ell=1.0 over ell=3.2 on these seeds.  A floor applied only
to `_local_refine` is insufficient because the coarse search anchors `best` at ell=1.0
before refinement even begins.

---

## Why the Original Fix Was Insufficient

The original fix added `_ELL_GRID_MIN = 1.0` and floored `_local_refine` candidates to it.
This prevented ell=0.8 but did not prevent ell=1.0 from winning in `_grid_search`.  On a flat
chi² surface the grid minimum (1.0) is selected by the grid search and passed as `best["ell"]`
to local refinement; all three ell candidates in refinement (0.8→1.0 floored, 1.0, 1.25) then
evaluate at ell ≥ 1.0 but the grid's 1.0 best is already the incumbent.  Result: ell=1.0
survives unchanged.  p99=70.7 m/s at ell=1.0 is still 67% above truth — not physically bounded.

---

## Principled Fix: Sample-Density-Tied Floor

**Mechanism**: `ell_floor = max(_ELL_GRID_MIN, _ELL_DENSITY_K × dt_median)` where
`dt_median` is the median time spacing of the position samples in the calibration slice
and `_ELL_DENSITY_K = 6`.

The floor is applied to **both** `_grid_search` (ell values below floor are skipped) and
`_local_refine` (candidates below floor are clamped).  `_ell_floor_from_dt(tps)` is computed
in `fit_stint_hp` from the slice times `tps` and passed down to both helpers.

**Justification for k=6**: The Matérn-5/2 kernel's effective correlation width is ~ell.  For
the smoother to average over multiple independent noise samples (i.e., to smooth rather than
interpolate), ell must cover several sample spacings.  Empirically, the review's synthetic
data (2 Hz, sig_pos=1.5, 90 s) shows:

| ell (s) | p99 (m/s) | ratio to truth |
|---------|-----------|----------------|
| 1.0     | 70.7      | 1.67×          |
| 2.4     | 46.2      | 1.09×          |
| 3.2     | 43.9      | 1.04×          |
| 4.5     | 43.0      | 1.01×          |

Near-truth (< 1.05×) requires ell ≈ 3.2 s = 6.4 × dt (0.5 s).  k=6 gives floor=3.0 s at
2 Hz → the grid skips 1.0, 1.4, 1.8, 2.4 and starts from 3.2 s → calibrated ell is 3.0–5.6 s.

**Why it generalises**: dt_median is computed from actual data, not hardcoded for one session.
At 4 Hz (dt=0.25 s), floor=1.5 s — the grid includes 1.8, 2.4, 3.2, 4.5 s and the floor
never fires on well-sampled FP1 stints whose optimal ell is typically 2–5 s.  At 1 Hz
(very sparse), floor=6.0 s → the grid adds 6.0 as an explicit candidate if the array is
otherwise empty.  The formula is not a magic number for one session; it encodes the physical
requirement that ell must span ~6 sample intervals to be in the smoothing (not interpolation)
regime.

---

## After-Fix Measurements on Floor-Triggering Seeds

Synthetic: `make_streams(duration=90, pos_hz=2, car_hz=2, sig_pos=1.5)`, analytic truth max = 42.40 m/s.

| Seed | Before fix (old 1.0 floor) |           | After fix (density-tied floor) |           |
|------|---------------------------|-----------|--------------------------------|-----------|
|      | ell (s)  | p99 (m/s)  | ell (s)   | p99 (m/s)  |
| 7    | 1.000    | 70.7       | 3.017     | **43.9**   |
| 555  | 1.000    | 71.5       | 5.625     | **42.2**   |
| 42   | 1.400    | 55.3       | 5.625     | 42.2       |
| 137  | 1.800    | 65.5*      | 3.017     | 44.6       |
| 201  | 1.800    | 43.5       | 3.017     | 44.7       |

*seed 137 ratio was 1.54× before the fix.

Seeds 7 and 555: after-fix p99 is **43.9 and 42.2 m/s** — within 3.5% and 0.5% of analytic
truth (42.4 m/s).  All five seeds now produce p99 < truth_max × 1.5 (= 63.6 m/s).

---

## Test Changes

Replaced the 5 original tests with 11 tests across 3 classes:

- `TestEllFloorShortLap` (5 tests):
  - Floor holds for seed=7 (density-tied, not the old fixed 1.0)
  - Floor holds for all 5 review seeds
  - **Seed=7: p99 < truth_max * 1.5** (bound is now 63.6, not 110)
  - **Seed=555: p99 < truth_max * 1.5** (floor-triggering seed, explicit)
  - All 5 seeds: p99 < truth_max * 1.5

- `TestEllFloorFormula` (4 tests): unit-tests `_ell_floor_from_dt` at 2 Hz, 4 Hz, dense data, and degenerate (1 point).

- `TestEllFloorLongStintUnchanged` (2 tests): long FP1 ell in range, chi² ~ 1.

---

## Docstring Accuracy Fix

Finding #3 from the review: `_ELL_GRID_MIN`'s docstring falsely claimed "_grid_search_ honours it."
This is now true: `_grid_search` receives `ell_floor` and skips grid values below it.
The docstring has been updated to accurately describe:
- `_ELL_GRID_MIN` as the absolute minimum (hard lower bound);
- `_ELL_DENSITY_K` and `_ell_floor_from_dt` as the density-tied floor mechanism;
- `_grid_search`'s exploratory role and why it now receives `ell_floor`.

---

## Physics Fixtures Unchanged by This Change

The calibration change only fires when the sample-density-tied floor exceeds the grid optimum.
For FP1 stints at 4 Hz, floor=1.5 s and typical optima are 2–5 s — the floor never triggers.
The three physics regression fixtures (spain/monza/monaco 2024 FP1 VER) are already modified
in the working tree from prior #445 physics work (not this calibration PR).  `git diff` on
`tests/fixtures/physics/` shows no additional changes from this calibration fix.

---

## Files Modified

- `src/preprocessing/trajectory/calibration.py` — added `_ELL_DENSITY_K`, `_ell_floor_from_dt`;
  updated `_grid_search` signature to accept and honour `ell_floor`; updated `_local_refine`
  to accept `ell_floor` parameter; `fit_stint_hp` computes floor via `_ell_floor_from_dt` and
  passes it to both helpers; updated docstrings.
- `tests/unit/preprocessing/trajectory/test_calibration_ell_floor.py` — replaced 5 tests with
  11 tests; tightened speed bound from `< 110 m/s` to `< truth_max * 1.5 ≈ 63.6 m/s`; added
  explicit seed=7 and seed=555 tests; added formula unit-tests for `_ell_floor_from_dt`.
