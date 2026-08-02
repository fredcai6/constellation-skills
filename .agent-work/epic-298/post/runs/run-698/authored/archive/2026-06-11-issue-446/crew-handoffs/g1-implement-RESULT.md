# Implementation Result — REWORK (g1 defect fixes)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1 — Scoring primitives + report schema` (REWORK: reviewer-identified defects only)

## What was fixed

### Defect 1 — s3 anchor not co-estimated (`sector_anchor.py`)

**Root cause:** In `_build_residuals_fn`, `s3_est = x[2]` was unpacked but the
s3 residual was `(t_end - t_s2) - off["s3"]` — using `t_end` (the last sample
time, a constant for a given lap) rather than the interpolated crossing time of
`s3_est`. This gave s3 a zero gradient in the Jacobian, so `least_squares`
never moved it; `s3_fit` always equalled the initial guess `0.85 * lap_length_m`.

**Fix:**
- `_build_residuals_fn`: added `t_s3 = _interp_time_at_arc(s3_est, s_arr, t_arr)`
  and changed the s3 residual to `(t_s3 - t_s2) - off["s3"]`.
- `_compute_lap_residuals`: same fix — added `t_s3` interpolation, updated
  residual to `(t_s3 - t_s2) - off["s3"]`, and added `s3_fit: float` parameter.
- `score_sector_anchor`: updated the call site to pass `s3_fit` to
  `_compute_lap_residuals`.

s3 now has a real gradient through `_interp_time_at_arc` and is genuinely
co-estimated with Jacobian-based uncertainty alongside s1 and s2.

### Defect 2 — s3 known-answer test was tautological (`test_trajectory_grading.py`)

**Root cause:** `_make_known_anchor_scenario` injected `known_anchors[3] = 0.85 *
lap_length_m`, which is exactly `x0[2]` (the optimizer's initial guess). Because
the old code never moved s3, the "recovery" assertion trivially passed. The test
would have accepted any implementation that left s3 at 0.85.

**Proof that old test was tautological:** With the buggy residual, the optimizer
reports `s3_fit = 0.85 * lap_length_m` regardless of the data. With the injected
anchor also at 0.85, `|fitted - expected| = 0 < 50m`. Pass. No discrimination.

**Proof that new test guards the bug:** With the buggy code and `known_anchors[3]
= 0.72 * lap_length_m`, the optimizer still returns `s3_fit = 0.85 * lap_length_m`
(initial guess, never moved). The test asserts `|fitted - expected| < 50m` but
`|0.85 * 5000 - 0.72 * 5000| = |4250 - 3600| = 650m >> 50m`. The test FAILS on
the old code. With the fix, the optimizer genuinely finds `s3 ≈ 3600m` and the
assertion passes.

**Changes made:**
- `_make_known_anchor_scenario`: changed `known_anchors[3]` from `0.85 *
  lap_length_m` to `0.72 * lap_length_m` (650m away from initial guess).
- `_make_official_splits`: changed `"s3": t_lap_end - t_s2` to
  `"s3": t_s3 - t_s2` — matching the now-correct residual formula (sector 3
  spans from s2 crossing to s3 crossing, not to the last sample time).
- Removed unused `anchor_fracs` and `t_lap_end` variables from
  `_make_official_splits`.
- `test_sector_anchor_fails_for_bad_candidate`: updated corruption from
  uniform +200ms across all sectors to +200ms on lap 0 only. Uniform
  per-lap inflation is absorbed by shared-anchor repositioning (optimizer
  shifts all three anchors forward by the same amount); per-lap-inconsistent
  corruption cannot be absorbed because anchors are shared across all laps.

## Scope
**Files changed:**
- `src/preprocessing/trajectory_grading/sector_anchor.py`
- `tests/unit/preprocessing/test_trajectory_grading.py`

No other files touched. No schema changes required. No new imports.

## Evidence

### pytest — all 47 tests pass

```
py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q
```

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1Brainz-worktrees\cmdr-446
configfile: pyproject.toml
plugins: anyio-4.9.0, hypothesis-6.152.9, mock-3.15.1
collected 47 items

tests\unit\preprocessing\test_trajectory_grading.py .................... [ 42%]
...........................                                              [100%]

============================= 47 passed in 0.21s ==============================
```

### simplification-limits — PASS

```
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory_grading tests/unit/preprocessing/test_trajectory_grading.py
```

```
PASS (7 files checked)
```

## Commit

`579dbca` on branch `issue-446-grading-harness` — "fix(g1-rework): co-estimate s3 anchor and fix tautological s3 test"

## Return status
`complete`

## Workflow Feedback

- The defects were precisely described and easy to locate. No ambiguity in the handoff.
- Fixing Defect 1 exposed a collateral breakage in `test_sector_anchor_fails_for_bad_candidate`:
  uniform sector inflation (all three sectors +200ms, all laps) is fully absorbed by
  the optimizer shifting all three anchors forward by the same amount. The test only
  worked before because the old buggy code could not move s3, leaving a guaranteed
  non-zero s3 residual. After the fix, the corruption type needed to change to something
  the optimizer genuinely cannot absorb (per-lap-inconsistent corruption). This is a
  collateral fix necessary to keep the suite green — it was not listed as one of the two
  defects but is a direct consequence of correctly fixing Defect 1.
- The `_make_official_splits` helper also needed to change its s3 formula from
  `t_lap_end - t_s2` to `t_s3 - t_s2` — the old formula only made sense when the
  optimizer's s3 residual used `t_end`, which it no longer does after the fix.
