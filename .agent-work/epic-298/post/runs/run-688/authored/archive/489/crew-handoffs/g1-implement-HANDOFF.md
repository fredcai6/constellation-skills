# Implementer Handoff

## Gate
`g1 — ribbon core + synthetic tests`

## Task
Implement `src/physics/ribbon.py` in the worktree `C:\Programs\f1Brainz\.claude\worktrees\489-ribbon-v2` on branch `feat/489-ribbon-v2`.

The module must provide `build_ribbon(laps_xy, n_grid=1500, smooth_window=9, min_laps=3) -> dict`.

**Algorithm:**
1. Input `laps_xy`: array-like of shape `(N_laps, 2, n_pts)` or a list of `(X, Y)` tuples/arrays — each lap's XY coordinates.
2. For each lap: compute arc-length `s`, normalize to `u = s / s[-1]` (progress 0→1), interpolate `X(u)` and `Y(u)` onto `n_grid` uniform grid points.
3. Stack all resampled laps and take the **median** along the lap axis → `X_med(u)`, `Y_med(u)`.
4. Optionally smooth the median path with a uniform-weight window of `smooth_window` points (via `np.convolve`).
5. Compute arc-length `s_med` of the median path.
6. Compute curvature κ(s) = dθ/ds where θ = unwrapped atan2(dY/ds, dX/ds). Use `np.gradient` for derivatives and `np.unwrap` on the angle.
7. Optionally apply a light smoothing pass on κ (same `smooth_window`).
8. Return `dict(distance_m=s_med, curvature=kappa)` — both 1D numpy arrays of length `n_grid`.

**Also implement tests** in `tests/unit/physics/test_ribbon.py`:
- `test_circle_curvature_recovery`: generate `n_laps=8` synthetic laps of a circle with known radius `R=50.0` (add small XY noise σ=0.5 m). Assert that at ≥90% of the `n_grid` stations, `|kappa_computed - 1/R| < 0.1 * (1/R)` (within 10%). L1 truth-anchored.
- `test_noise_averaging_invariant`: same circle, compute single-lap κ for each of the 8 laps, compute pooled κ via `build_ribbon`. Assert `np.std(kappa_pooled) < np.mean([np.std(single_lap_kappa) for each lap])`. L2 noise-averaging invariant.
- `test_track_profile_schema`: call `build_ribbon` on 5 synthetic laps. Assert output has keys `distance_m` and `curvature`, both are 1D numpy arrays of length `n_grid`, and `distance_m` is strictly monotone increasing.
- `test_min_laps_raises`: assert that calling `build_ribbon` with fewer than `min_laps` laps raises `ValueError`.

## Protected Intent
The output schema `dict(distance_m=array, curvature=array)` must exactly match `PhysicsSimulator._extract_track_profile` in `src/physics/physics_simulator.py`. This is the sim's sole geometry input contract; a mismatch silently produces wrong physics.

## Test Mode
TDD required — write failing tests first, implement to make them pass. The test file must exist before the module.

## Close Criteria
- `src/physics/ribbon.py` exists with `build_ribbon` function
- `tests/unit/physics/test_ribbon.py` exists with the 4 tests listed above
- `py -m pytest tests/unit/physics/test_ribbon.py -v` is **fully green** (all 4 tests pass)
- `py -m pytest tests/unit/physics/ -q` is **fully green** (no regressions in existing physics unit suite)
- Output schema: `distance_m` is monotone increasing, `curvature` is finite float64 array, both length `n_grid`
- `build_ribbon` raises `ValueError` when fewer than `min_laps` laps provided

## Allowed Scope
- CREATE: `src/physics/ribbon.py` (new file)
- CREATE: `tests/unit/physics/test_ribbon.py` (new file)
- READ-ONLY (no edits): any file in the worktree to understand context

## Specific Exclusions
- **Do NOT edit**: `src/preprocessing/trajectory/smoother.py`, `src/preprocessing/trajectory/calibration.py`, `src/preprocessing/trajectory/dynamics.py`, `src/physics/physics_adapter.py`, `src/physics/apex_extract.py`, or any other existing file
- Do NOT import anything from `src/evo_predictor/`, `src/latent_power/`, `src/compound_prior/`, or `src/calibration/`

## Constraints
- Worktree: `C:\Programs\f1Brainz\.claude\worktrees\489-ribbon-v2` — ALL work goes here
- Python is `py`, not `python`
- No evo-region imports (`constraint:physics_region_no_evo_import`)
- Output schema MUST be `dict(distance_m=np.ndarray, curvature=np.ndarray)` — keys and types must match exactly what `PhysicsSimulator._extract_track_profile` accepts
- FastF1 pos_data X/Y are in decimetres (×0.1 for metres) — not relevant for G1 (synthetic tests only) but note it for G2
- Allowed imports: `numpy`, `scipy` (already in physics region deps), standard library

## Map Anchors (inbound)
- **Structural:** `struct:physics — src/physics/` container; `ribbon.py` is a new module-leaf addition at component level under this container
- **Capability:** track geometry as κ(s) input for ideal-lap simulation (the sim currently has no geometry builder; this is that layer)
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import` (no evo/latent/compound imports); track_profile schema: `dict(distance_m=array, curvature=array)` from `PhysicsSimulator._extract_track_profile`
- **Decision anchors:** pooled/median XY → κ(s) is the sim-geometry path (distinct from per-car apex-pace which uses per-car smoothed state)
- **Evidence expectations:** L1: synthetic circle recovers κ=1/R within 10%; L2: pooled κ std < single-lap κ std; schema match confirmed

## Required Evidence
1. `py -m pytest tests/unit/physics/test_ribbon.py -v` output (all 4 tests pass)
2. `py -m pytest tests/unit/physics/ -q` output (no regressions)
3. Source listing of `src/physics/ribbon.py` (confirming build_ribbon schema, curvature formula, smooth_window use)

## Verification Commands

```bash
py -m pytest tests/unit/physics/test_ribbon.py -v --tb=short
py -m pytest tests/unit/physics/ -q --tb=short
```

## Suggested Model Tier
`simple bounded` — new module with clear algorithm, synthetic tests only, no real data. Sonnet is fine.

## Authority
- Algorithm (median-pooled XY → κ(s)) and schema (`distance_m` + `curvature`) are decided.
- `smooth_window=9` default is from the exploration ribbon.py reference — can tune if needed.
- `n_grid=1500` default from the reference.
- Do NOT change the output schema or add dependencies outside numpy/scipy/stdlib.

## Stop Conditions
Stop and return if: (a) the physics unit suite has an existing test that cannot be kept green; (b) the output schema cannot satisfy `PhysicsSimulator._extract_track_profile`; (c) importing numpy/scipy fails in this environment.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
Save result to: `C:\Programs\f1Brainz\.agent-work\489\crew-handoffs\g1-implement-IMPLEMENTER_RESULT.md`
