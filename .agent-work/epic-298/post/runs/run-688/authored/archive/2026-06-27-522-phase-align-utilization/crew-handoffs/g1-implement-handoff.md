# Implementer Handoff — G1 Diagnose (#522)

## Gate
g1-implement (DIAGNOSIS — evidence only, NO production code change)

## Task
Discriminate the root cause of the C1 braking/fast-corner utilization clip (`U` pinned at `U_CLIP_MAX=2.0`, raw ratios 3.3–3.8×). On 2 RBR 2023-Q corners, pull the ideal-lap speed, the real best-lap speed, and the ribbon curvature, all on **true track distance**, and determine which of two root causes holds:

- **(a) misregistration** — the ideal corner caps are physically plausible, but the real lap is registered onto the ribbon by *progress fraction* while v_ideal + curvature are on *true ribbon distance*, so corners drift in distance and the point ratio explodes at braking knees. Verify by recomputing the regime ratio under a **true-distance** registration and showing it falls to ≤~1.
- **(b) under-called caps** — the ideal corner-speed caps are genuinely too low (lateral frontier / Gsat fallback under-calls cornering grip) even when distance-aligned, so the real lap legitimately exceeds the "ideal."

## Protected Intent
The C1 per-regime utilization measure must become physically bounded. This gate decides the fix approach on evidence — do NOT assume (a); prove which it is.

## Test Mode
Inspection-only (diagnosis). Produce a reproducible script + figures + a written finding. No src/ change, no new unit tests this gate.

## Close Criteria
- `DIAGNOSIS.md` written under `.agent-work/522-phase-align-utilization/` that names **(a)** or **(b)** with trace evidence, not assertion.
- For each of 2 corners: the ideal-lap apex/min speed, the real-lap speed at that corner, the curvature, and the point-ratio — tabulated.
- Direct test of (a): recompute each corner's regime ratio with v_real registered by **true distance** (`np.interp(grid_dist, driver_distance, driver_speed)`) instead of `resample_by_progress`, and report whether braking/fast-corner ratios fall to ≤~1. If they do → (a). If they stay >1 with physically-aligned points → (b), and report by how much the ideal caps under-call.
- A recommended comparison method follows from the finding: (a) → true-distance / corner-landmark alignment keeping the ideal-lap denominator; (b) → per-regime measured-frontier comparison (reuse layer2 frontiers).
- A reproducible diagnostic script (in the work area) + the figure(s) the reviewer can regenerate.

## Allowed Scope
- NEW files under `.agent-work/522-phase-align-utilization/` only (script `diag_alignment.py`, `DIAGNOSIS.md`, PNG figures).
- READ-ONLY: `src/physics/utilization/`, `src/physics/physics_simulator.py`, `src/physics/sim_evaluator.py`, `src/physics/ribbon.py`, the store + FastF1 cache.

## Specific Exclusions
- No edits to any `src/` file or any committed `scripts/` file. No new tests in `tests/`. No store writes.

## Constraints
- `py` launcher (Python 3.14). Run from repo root `C:/Programs/f1Brainz`.
- Store + cache are READ-ONLY; open via absolute main-checkout paths (untracked-data rule).
- FastF1 pos_data X/Y are decimetres (×0.1 for metres) — but you are reusing `build_session_ribbon`/`fit_session_full`, which already handle units; do not re-scale.
- Physics rigor: report units (m, m/s, 1/m), state plausibility bounds explicitly.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `src/physics/utilization/regime_utilization.py` (the comparison core, lines ~574–582 build v_ideal_on_grid + v_real_on_grid); `characterize.py` (`_build_ceiling`, `_load_lap_and_ribbon`). `struct:physics` — `physics_simulator.simulate_lap` / `_compute_speed_caps`; `sim_evaluator.resample_by_progress`.
- **Capability:** per-regime driver utilization — how the realised lap is compared to the ceiling.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; assumption that ribbon geometry ≈ real lap line except near knees (this gate tests it).
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (its review trigger explicitly names this phase-alignment fix); `decision:c1_driver_utilization_design` (single canonical ideal-lap path — reuse it, do not build a second sim).
- **Evidence expectations:** ratio falls to ≤~1 under correct alignment ⇒ (a); apex caps under-call when aligned ⇒ (b).

## Exact seams (verified from source — use these, do not rediscover)
- Store: `EstimateStore("C:/Programs/f1Brainz/data/physics_estimates.db").load(year=2023, status="ok")` → `store_df` (the OLD #510 baseline; the misregistration is store-independent, so this is the right diagnosis surface). `from src.physics.layer2.estimate_store import EstimateStore`.
- Cache: `C:/Programs/f1Brainz/data/telemetry` (= `session_fit.DEFAULT_CACHE`).
- Ceiling: `src.physics.utilization.characterize._build_ceiling(store_df, year, constructor, round_idx)` → `CarCeilingResult` (`.params`, `.envelope`, `.n_sessions`). Resolve `round_idx` via `characterize._resolve_round_idx(store_df, year, gp_name, constructor)`. Constructor for VER = `"Red Bull Racing"`.
- Lap + ribbon: `characterize._load_lap_and_ribbon(year, gp_name, driver, cache, load_fn)` → `(full, track_df)`. `full.best_distance`, `full.best_speed_real` are the real lap (m, m/s). `track_df` has columns `distance_m`, `curvature`. `load_fn = src.physics.session_fit.load_quali_session` (signature `(year, gp, session_type, cache)` — 4 positional; session_type="Q").
- The comparison (replicate from `regime_utilization.estimate_driver_utilization`, ~lines 574–582):
  ```python
  grid_dist = track_df["distance_m"].to_numpy(float)
  grid_curv = track_df["curvature"].to_numpy(float)
  nominal_lap = sim.simulate_lap(track_df, ceiling.params, sample=False)   # PhysicsSimulator()
  v_ideal = np.interp(grid_dist, nominal_lap.distance_profile, nominal_lap.speed_profile)   # TRUE distance
  v_real_progress = resample_by_progress(grid_dist, full.best_distance, full.best_speed_real)   # PROGRESS fraction (current)
  v_real_truedist = np.interp(grid_dist, full.best_distance, full.best_speed_real)              # TRUE distance (the (a) test)
  ```
  `from src.physics.sim_evaluator import resample_by_progress`. `from src.physics.physics_simulator import PhysicsSimulator`.
- Regime masks: reuse `regime_utilization._regime_masks(...)` (or replicate: braking = `dv/ds < BRAKING_DECEL_THRESHOLD`; fast_corner = corner & `a_lat ≥ 25`). Focus the report on braking + fast_corner (the clipped regimes).

## Cases (2 corners)
- **Monaco / VER** — the canonical fast_corner 3.79× case from #518. (Monaco is GP name `"Monaco"` in the store; confirm via `store_df.gp_name.unique()`.)
- One **braking knee** on the same lap (the steepest `dv/ds` segment), to cover the braking regime.

(If Monaco/VER fails to load for any reason, fall back to another RBR 2023-Q case present in the store — report the substitution.)

## Required Evidence
- `DIAGNOSIS.md`: the (a)/(b) verdict; per-corner table (v_ideal_apex, v_real, curvature, progress-ratio, true-dist-ratio); the recommended comparison method + one-paragraph rationale; any caveat (e.g. if Monaco shows (a) but a residual cap-softness is visible, note it).
- `diag_alignment.py` (work-area) — reproducible.
- ≥1 figure overlaying v_ideal, v_real (both registrations), and curvature vs true distance, with the 2 corners annotated.

## Verification Commands
```bash
py .agent-work/522-phase-align-utilization/diag_alignment.py
```

## Suggested Model Tier
Simple-bounded (Sonnet) — reuses existing seams; the work is pull-plot-conclude, not design.

## Authority
The (a)/(b) call is yours to make FROM THE EVIDENCE; the *fix choice* is the human's at the decide-fix checkpoint — you recommend, you do not decide it. Do not touch production code or assume the answer.

## Stop Conditions
Stop and return if: the canonical ideal-lap path cannot be invoked from the store, both candidate corners fail to load, or producing the true-distance ratio requires touching `src/`.

## Return Format
Return IMPLEMENTER_RESULT: the (a)/(b) verdict + the per-corner numbers, files created, evidence produced, the recommended comparison method, assumptions, stop conditions hit, out-of-scope observations, and workflow feedback (anything in this handoff that made the work harder than needed).
