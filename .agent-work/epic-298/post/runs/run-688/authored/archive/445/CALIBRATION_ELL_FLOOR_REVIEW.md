# Calibration Ell Floor Fix — Independent Code Review

Reviewer: fresh-context independent agent (did not write the code)
Date: 2026-06-16
Verdict: **CHANGES-REQUESTED**

---

## Item 2 Call — Does the fix genuinely FIX inflation, or merely BOUND it?

**It BOUNDS but does not FIX the inflation.** This is the core blocker.

Measured after-fix p99 speeds on the synthetic short-lap (seed=7, duration=90 s, pos_hz=2, sig_pos=1.5):

| Seed | Calibrated ell | p99 after fix | Truth max | Ratio |
|------|----------------|---------------|-----------|-------|
| 7    | 1.000 (at floor) | **70.7 m/s** | 42.4 m/s | 1.67x |
| 42   | 1.400          | 55.3 m/s     | 42.4 m/s | 1.30x |
| 137  | 4.500          | 42.3 m/s     | 42.4 m/s | 1.00x |
| 201  | 5.625          | 42.5 m/s     | 42.4 m/s | 1.00x |
| 555  | 1.000 (at floor) | **71.5 m/s** | 42.4 m/s | 1.69x |

For seeds 137 and 201 (where the chi² surface happens to pick ell >> 1.0), the fix is irrelevant and output is correct. For seeds 7 and 555 (where the chi² surface is flat and the grid minimum wins), the floor fires and ell is correctly bounded at 1.0 instead of 0.8 — but p99 is **still 67–69% above truth**. A smooth path with truth max of 42.4 m/s is producing 71 m/s after calibration with ell=1.0. Flooring at 1.0 buys ~6–7 m/s improvement over ell=0.8 (which gives ~85 m/s) but nowhere near truth.

Measured at various ell values for seed=7 (fixed sf/sp):

| ell  | p99   |
|------|-------|
| 0.8  | 85.5  |
| 1.0  | 70.7  |
| 1.4  | 58.8  |
| 1.8  | 51.5  |
| 2.4  | 46.2  |
| 3.2  | 43.9  |
| 4.5  | 43.0  |

Near-truth output (< 5% above truth) requires ell >= 3.2. The floor of 1.0 gets you from "catastrophic" to "still bad."

The real-world "fix" for ALO and GAS in the validation script was `ell_retry = 2.4`, not 1.0. That context is buried in the production notes but should inform the floor choice.

---

## Numbered Findings

### 1. Diagnosis Correctness: CORRECT but incomplete (nit)

The diagnosis — that `_local_refine` proposes `best_ell * 0.8`, and when the grid optimum is at 1.0 this produces 0.8 which wins on a flat chi² surface — is confirmed by direct measurement. For seed=555, without the floor, refinement returns ell=0.800 (grid best was 1.0, 0.8*1.0=0.8, wins on hold-out noise). The path from ell < sample-spacing → Matern interpolates noise → velocity overshoot is real. So the diagnosis is correct.

One gap: the CALIBRATION_ELL_FLOOR_FIX.md states "p99 speed < 110 m/s (analytic truth is ~44 m/s; even with noise the calibrated smoother stays physically bounded)." That sentence implies the fix brings output near physical truth, which is false: 70 m/s is not "physically bounded" in a meaningful sense for F1 telemetry (it is below the 110 m/s gate, but it is 67% above the analytic maximum on this synthetic path). The diagnosis document should distinguish "prevents worst-case catastrophe (>100 m/s)" from "produces accurate output."

### 2. The floor value 1.0 is INSUFFICIENT for short-lap accuracy (BLOCKER)

As shown above, ell=1.0 on a 90 s, 2 Hz synthetic still inflates p99 by 1.67x. The production ad-hoc fix used `ell_retry = 2.4`. A principled sample-density-tied floor (e.g., `max(1.0, 4.0 / hz)` where hz is the observed sample rate) or a minimum correlation-length proportional to `1 / (data density)` would be more correct. Alternatively, the floor should be raised to a value that actually prevents observable inflation — based on the table above, a floor of ~2.4-3.2 s would be needed to bring p99 within ~10% of truth on this synthetic.

This is a blocker because: (a) the fix is presented as preventing unphysical inflation, but at the floor value it still produces output that is clinically misleading (70 m/s on a 42 m/s circuit), and (b) the test bound of `< 110 m/s` is too loose by 2.5x to distinguish "working" from "not working."

### 3. `_grid_search` does NOT honour `_ELL_GRID_MIN` (documentation false claim, nit)

The docstring on `_ELL_GRID_MIN` says: "This constant is the single source of truth for that floor; both `_grid_search` and `_local_refine` honour it."

This is false. `_grid_search` hardcodes its own grid:
```python
ell_grid = np.array([1.0, 1.4, 1.8, 2.4, 3.2, 4.5])
```
It never reads `_ELL_GRID_MIN`. If `_ELL_GRID_MIN` is raised (e.g., to 2.4), `_grid_search` will still try ell=1.0 and 1.4, and `_local_refine` will correctly floor them, but the grid will be exploring below the intended minimum.

This is a documentation/consistency nit rather than a runtime bug (because the floor in `_local_refine` bounds the worst-case output), but it means the single-source-of-truth claim is false and could cause confusion if `_ELL_GRID_MIN` is ever adjusted.

### 4. Seed=555: floor makes p99 marginally WORSE (nit/concern)

For seed=555 (before: ell=0.800, p99=75.1 m/s; after: ell=1.000, p99=71.5 m/s via the same sf/sp) the floor improves the ell but p99 changes by only 3.6 m/s. However, running the full calibration after the fix gives p99=71.5 m/s vs the no-floor run's 75.1 m/s — that is a marginal improvement. The concern is structural: a 6 m/s "improvement" on a 30 m/s overshoot is not a meaningful fix.

### 5. Test bound too loose (nit / part of blocker)

`test_smoothed_speed_physically_bounded_short_lap` asserts `p99 < 110 m/s`. The actual after-fix value is 70.7 m/s (seed=7). The bound is 110. That is a 56% buffer between the asserted limit and the failure mode. A test that passes at 70.7 m/s when truth is 42.4 m/s provides no regression safety — a future regression that pushes p99 to 109 m/s would still pass. The bound should be at most `truth_max * 1.5` (say `< 65 m/s`) to actually guard against the behaviour described in the issue. The current test would have passed even before the fix if the no-floor ell happened to not win (seeds 137 and 201 would have passed trivially since those seeds don't trigger the bug).

### 6. Long-stint tests are sound (pass)

`test_long_stint_chi2_still_honest` confirms chi2 in [0.6, 1.6] on 400 s, 4 Hz data. The floor never fires here. The long-stint path is unaffected. This is correct.

### 7. Physics regression fixtures (not caused by this change)

`git diff HEAD` shows `blessed_params.json` and `processed_telemetry.parquet` are modified for all three fixtures (spain, monza, monaco 2024 FP1 VER). These diffs predate the ell-floor change (per the subagent's claim and per `git log` — the fixture changes come from the broader physics-module #445 work, not from the one-line `max()` call here). The ell-floor change in isolation does not touch the calibration path for long FP1 stints (confirmed: floor does not fire for ell > 1.0 grid optima). The fixture change is a separate concern belonging to the broader #445 physics work, not this PR.

### 8. Counts: 307 tests pass, 10 skipped (confirmed)

Full run: `py -m pytest tests/unit/preprocessing/trajectory tests/integration/test_trajectory_spain_reproduction.py tests/unit/physics tests/regression/test_physics_regression.py -q` → 307 passed, 10 skipped. The 5 new ell-floor tests all pass. No regressions introduced. Skips are pre-existing physics regression markers (documented `xfail`/`skip` for unresolved fallback lap-time accuracy).

---

## Summary

The fix is correctly diagnosed and correctly implemented as a lower bound on `_local_refine`. It prevents the worst-case catastrophic overshoot (>100 m/s) by stopping refinement at ell=0.8 when the grid minimum is 1.0. However, it does not achieve its stated goal of "physically bounded" output: the calibrated smoother at ell=1.0 still inflates p99 by 67% above the analytic truth on the exact short-lap synthetic used in the tests. The test bound of `< 110 m/s` is too loose by 2.5x to distinguish correct from incorrect behaviour. A principled floor of ~2.4–3.2 s (matching the production `ell_retry=2.4` workaround) would be needed to achieve near-truth output on short Q-laps.

**CHANGES-REQUESTED:** Fix the floor to a value that actually suppresses inflation (or tie it to sample density), and tighten the test bound to `< 65 m/s` (truth_max * 1.5) so it would catch regressions.
