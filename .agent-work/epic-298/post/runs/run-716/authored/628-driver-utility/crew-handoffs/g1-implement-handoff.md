# Implementer Handoff — G1 (observable module + resumable batch CLI)

## Gate
`g1-implement` (epic #601 wave-7 issue #628 Phase 3b, delegated). Worktree: **C:/Programs/f1-628** ONLY
(branch feat/628-driver-utility). Bespoke scripts need `PYTHONPATH=C:/Programs/f1-628` (editable-.pth trap
silently imports MAIN src/). Tests are cwd-safe.

## Task
Build the **per-driver, per-axis absolute-deficit OBSERVABLE** and a resumable batch CLI that produces it.
Two deliverables:

1. `src/physics/utilization/driver_utility_observable.py` — a PURE, unit-testable function. Given a
   `strictly_pre` causal car ceiling, a driver's best-lap trace, and the track ribbon, compute per-regime
   **absolute speed deficit** rows. This MIRRORS `regime_utilization.estimate_driver_utilization`
   (src/physics/utilization/regime_utilization.py lines 581-598 — READ IT as the reference) with THREE
   differences: (a) the ceiling is built `strictly_pre=True`; (b) NO MC needed; (c) the per-regime metric is
   the **absolute deficit** `g = mean(v_ideal_on_grid - v_real_on_grid)` over each regime mask — **NOT** the
   ratio `mean(v_real/v_ideal)`. There must be **no division of v_real by v_ideal (or observed by capability)
   anywhere** in this module — that is the load-bearing F4 requirement.

2. `scripts/build_driver_utility_observables.py` — a **resumable** batch CLI over a
   `(year, session_type, rounds, drivers)` slice that persists observable rows to an **untracked** scratch DB.

## Protected Intent
Anti-circularity (critic F4): the observable is an absolute deficit against a **causal** ceiling that excludes
the round being measured. Never compute `observed ÷ capability`. Never add a driver dimension to the car
ceiling.

## Test Mode
TDD required for the pure function (synthetic arrays); test-after allowed for the CLI (a dry-run/2-case smoke).

## Close Criteria
- `compute_regime_deficits(...)` pure function returns per-regime `{axis: (g, n_points, sigma_lapsampling)}`
  for axes `braking, slow_corner, fast_corner, straight`, where `g = mean(v_ideal - v_real)` over each mask.
- **Driver at ceiling** (v_real == v_ideal on grid) → all `g ≈ 0`.
- **Driver 5% slower in corners only** (v_real reduced on corner-mask points, equal on straight) → `g > 0` on
  braking/slow_corner/fast_corner and `g ≈ 0` on straight.
- `sigma_lapsampling = std(deficit[mask]) / sqrt(n_points)` per regime (mirror
  `regime_utilization._u_and_consistency`'s SEM form, but on the **deficit**, not the ratio).
- Regime masks come from `regime_utilization._build_regime_masks` (REUSED, not reinvented).
- CLI: `--year --session-type --rounds --drivers --db <scratch.db>`; for each (constructor,round) builds ONE
  `build_car_ceiling(strictly_pre=True)` + ONE `simulate_lap` (shared across the constructor's drivers); per
  driver uses `fit_best_lap_trace` for v_real; **idempotent skip-if-present** (re-run adds only missing rows).
- A grep proves NO `v_real / v_ideal`, no `/ v_ideal`, no `observed / capab*` in the new files.

## Allowed Scope
- NEW: `src/physics/utilization/driver_utility_observable.py`, `scripts/build_driver_utility_observables.py`,
  `tests/unit/physics/test_driver_utility_observable.py`.
- READ-ONLY reuse (do NOT modify): `regime_utilization.py` (`_build_regime_masks`, `_u_and_consistency`
  pattern), `car_prior.build_car_ceiling`, `session_fit.{load_quali_session,fit_best_lap_trace}`,
  `characterize.py` (`_make_track_df`, `build_session_ribbon` usage — copy the ribbon→track_df pattern),
  `sim_evaluator.resample_by_progress`, `physics_simulator.PhysicsSimulator`.

## Specific Exclusions
- Do NOT build the latent estimator (G2), the gate harness (G3), or run any real batch (that is G5). This gate
  ends when the module + CLI + unit tests are green and a 2-case CLI smoke works.
- Do NOT modify `regime_utilization.py`/`car_prior.py`/`session_fit.py` (reuse only).
- Do NOT compute or store any ratio.

## Constraints
- `py` not `python`. Tests: `py -m pytest tests/unit/physics/test_driver_utility_observable.py -q`.
- DB-only analysis: v_real via `load_quali_session` (telemetry-store seam) → `fit_best_lap_trace`; no FastF1.
- Scratch DB `data/driver_utility_observables.db` is **UNTRACKED** — NEVER `git add` it; it is gitignored-class.
- Row schema (persist exactly): `year, session_type, gp_name, round_idx, constructor, driver, axis, g_deficit,
  n_points, sigma_lapsampling, n_sessions_causal, error`.

## Exact seam signatures (verified from source — use these)
- `build_car_ceiling(*, store_df, year: int, constructor: str, target_round: int, strictly_pre: bool=False,
  config=None) -> CarCeilingResult` (`.params`, `.envelope`, `.air_density`, `.n_sessions`). Pass
  `strictly_pre=True`. Raises ValueError when no round < W (round 1 has no causal history — SKIP with an
  error row, never crash the batch).
- `_build_regime_masks(distance, curvature, v_real, *, decel_threshold=..., alat_threshold=FAST_CORNER_ALAT_THRESHOLD,
  curvature_threshold=CURVATURE_THRESHOLD) -> (m_braking, m_slow, m_fast, m_straight)`.
- `PhysicsSimulator().simulate_lap(track_df, ceiling.params, sample=False)` → lap with `.distance_profile`,
  `.speed_profile`. `track_df` needs columns `distance_m`, `curvature`.
- `resample_by_progress(grid_dist, driver_distance, driver_speed)` (from `src.physics.sim_evaluator`) → v_real on grid.
- `fit_best_lap_trace(session, driver) -> Optional[(best_distance, best_speed_real, best_lap_s)]` (lean; skips MAP fit).
- `load_quali_session(year, gp, session_type='Q') -> (session, rho, rho_is_fallback)` (telemetry-store first).
- Store load: `EstimateStore('C:/Programs/f1Brainz/data/physics_estimates.db').load(year=YEAR, session_type='Q')`,
  then filter `fit_status=='ok'`. The `drivers` column is a JSON list (both cars) — resolve a driver's
  constructor by membership (see `characterize._lookup_constructor`).

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new module + script; reuse `_build_regime_masks`,
  `build_car_ceiling`, `fit_best_lap_trace`.
- **Capability:** per-driver per-axis absolute access deficit (produced observable).
- **Constraints:** DB-only; NEVER commit data/*.db; no observed/capability division.
- **Decision anchors:** `decision:c1_driver_utilization_design` — reuse the causal ceiling; the `strictly_pre`
  choice is the falsifiable-gate refinement (do not contradict; it is surfaced at reconcile).
- **Evidence:** at-ceiling→g≈0; corner-slow→g>0 corners, ≈0 straight; grep proves no ratio.

## Deliverable Path Check
- **Committed:** `src/physics/utilization/driver_utility_observable.py`,
  `scripts/build_driver_utility_observables.py`, `tests/unit/physics/test_driver_utility_observable.py` —
  run `git check-ignore <path>` for each and confirm exit 1 (not ignored) before finishing.
- **Local-only (untracked, do NOT stage):** `data/driver_utility_observables.db`.

## Required Evidence
- `py -m pytest tests/unit/physics/test_driver_utility_observable.py -q` full pass output.
- The grep result proving no `observed/capability` division in the two new source files.
- CLI 2-case smoke: run on `--year 2023 --rounds 5 --drivers VER,PER` (round 5 has causal history), show the
  rows written and that a re-run skips them (resumable). (This touches the MAIN checkout DBs read-only; the
  scratch write DB is under data/ — confirm `git status data/` shows only the untracked scratch DB, then
  leave it; do NOT stage.)

## Verification Commands
```bash
cd /c/Programs/f1-628 && py -m pytest tests/unit/physics/test_driver_utility_observable.py -q
cd /c/Programs/f1-628 && grep -nE "v_real ?/ ?v_ideal|/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py || echo "NO-RATIO-OK"
cd /c/Programs/f1-628 && PYTHONPATH=C:/Programs/f1-628 py scripts/build_driver_utility_observables.py --year 2023 --session-type Q --rounds 5 --drivers VER,PER --db data/driver_utility_observables.db
```

## Suggested Model Tier
simple bounded — the spec + seams are exact; risk is confined to the F4 no-ratio discipline (grep-checked).

## Authority
The construction (absolute deficit vs strictly_pre causal ceiling, no ratio) is DECIDED by the Commander
(cold-critic-ratified). Do not re-open it. If a seam signature is wrong, STOP and return — do not invent.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a listed seam signature does not match source, the F4
no-ratio requirement cannot be met, or the scratch DB cannot be written without staging a tracked data file.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (pytest + grep + CLI
smoke output), assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
