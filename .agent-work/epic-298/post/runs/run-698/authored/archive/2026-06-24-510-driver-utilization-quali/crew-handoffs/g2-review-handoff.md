# Reviewer Handoff

## Gate
g2-review (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## What Was Implemented
`src/physics/utilization/regime_utilization.py` — the per-regime driver-utilization estimator. A pure core
`regime_utilization(distance, curvature, v_real, v_ideal, ...)` (no FastF1/DB) and a thin integration wrapper
`estimate_driver_utilization(ceiling, track_df, driver_distance, driver_speed, ...)` that runs the canonical
`PhysicsSimulator` ideal lap from the G1 car ceiling and propagates envelope covariance via Monte Carlo. Decomposes
realised-vs-ceiling into four regimes (braking / slow_corner / fast_corner / straight). 17 new TDD tests. Implementer
result: `.agent-work/510-driver-utilization-quali/crew-handoffs/g2-implement-result.md` (read it in full).

## How to Inspect the Diff
Two new files only: `src/physics/utilization/regime_utilization.py`,
`tests/unit/physics/test_regime_utilization.py`. `git status -s` should show only these as project changes (plus the
`.agent-work/` work area; ignore `.agent-work/CONSTELLATION_FEEDBACK.md`, `.agent-work/templates/**` churn — that is
skill-load noise, not this gate). The implementer claims `car_prior.py`, `sim_evaluator.py`, `physics_simulator.py`,
`capability_envelope.py`, `session_fit.py`, `ribbon.py` are all UNCHANGED — **verify that**.

## Task Statement
Compute per-(driver, quali) per-regime utilization = realised lap vs the G1 car ceiling, normalised cross-circuit,
with honest covariance from the envelope; envelope = car (from G1), utilization = driver; the split is impure and the
covariance owns it. Full task: `.agent-work/510-driver-utilization-quali/crew-handoffs/g2-implement-handoff.md`.

## Close Criteria (each a review check)
- **Frontier invariant:** `v_real == v_ideal` → `U_r ≈ 1.0` in every populated regime. (Confirm the test proves it.)
- **Uniform-0.9 invariant:** `v_real == 0.9·v_ideal` → `U_r ≈ 0.9`.
- **Partition tiling:** the four regime masks cover every track point **exactly once** (no gaps, no overlaps). Read
  the masking logic, not just the test — confirm the priority (braking → slow/fast corner → straight) cannot
  double-count or drop a point.
- **Honest covariance:** σ on each `U_r` is propagated from the envelope covariance (a real MC over sampled params),
  not nominal, and GROWS with envelope σ (confirm the monotonic test).
- **Impure-split caveat explicit:** `split_is_impure=True` on every result + docstring caveat; no over-claim of clean
  separation.
- **Reuse, not duplication:** `sim_evaluator.resample_by_progress` + `BRAKING_DECEL_THRESHOLD` reused (no second Δv
  path); single canonical sim path.
- `constraint:physics_region_no_evo_import` held; `simplification_limits` clean; L1/L2 tests green (re-run them).

## Three specific scrutiny points (judge them)
1. **Covariance MC reaches into `PhysicsSimulator._sample_parameters` (a private method)** instead of
   `monte_carlo_laps` (which the implementer found returns lap times only, not per-point speed profiles — a real API
   gap). **Judge:** is consuming the private `_sample_parameters` an acceptable single-canonical-path use of the same
   internal machinery (APPROVE, with a triage candidate to expose a public per-point MC), or a boundary violation
   that should BLOCK? Recommend APPROVE-with-triage **if** it genuinely reuses the simulator's own sampling (no
   re-implemented sampling) and the canonical sim path is otherwise intact.
2. **`U_r = mean(v_real_i / v_ideal_i)` (mean-of-ratios), clipped [0,2].** **Judge:** is mean-of-ratios a defensible
   utilization normalisation for a first characterization (it meets the invariants and is interpretable), or does it
   distort vs a time/distance-weighted or pace-based measure in a way that would mislead the verdict? A note is enough
   if defensible; BLOCK only if it is actually wrong.
3. **Lap-sampling σ not modelled** (realised lap treated as noise-free; documented TODO hook, field not omitted).
   **Judge:** is it honest to ship σ_U that captures only the envelope term, given it is explicitly documented as an
   understatement with a hook? (Honest = the limitation is disclosed, not hidden.) Confirm it is disclosed in the
   artifact, not just the result file.

## Allowed Scope
New: `src/physics/utilization/regime_utilization.py`, `tests/unit/physics/test_regime_utilization.py`. Read-only reuse
of car_prior/sim_evaluator/physics_simulator/ribbon/session_fit.

## Specific Exclusions (flag if touched)
No batch/dashboard/verdict (G3); no `scripts/` changes; no change to G1 `car_prior.py` or `sim_evaluator.py`; no
second inline sim; no evo import.

## Constraints the Implementation Must Respect (each a check)
- `constraint:physics_region_no_evo_import`; single canonical sim path; honest covariance first-class; regime
  thresholds as named constants/config (the `FAST_CORNER_ALAT_THRESHOLD=25 m/s²` and `CURVATURE_THRESHOLD` are module
  constants — confirm no inline magic numbers); `py` not `python`; public input validation.

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `regime_utilization.py` (new); reuses `sim_evaluator` pure helpers,
  `physics_simulator` (canonical sim), G1 `car_prior` (ceiling).
- **Capability:** driver utilization measurement (per-regime) — new; extends
  `decision:ideal_lap_sim_two_sided_evaluator` (gap = driver signal).
- **Constraints:** physics_region_no_evo_import; honest covariance first-class; single canonical path.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — per-point Δv is the primary read; flag any
  contradiction as a candidate.
- **Evidence expectations:** frontier→~1; 0.9→~0.9; mask tiling; covariance monotonic in envelope σ.

## Evidence Produced
- `py -m pytest tests/unit/physics/test_regime_utilization.py -q` → 17 passed. **Re-run to confirm.**
- `py -m src.utils.simplification_limits --paths ...` → PASS (2 files).

## Suggested Model Tier
Stronger-ish — the partition-tiling correctness, covariance honesty, and the three scrutiny judgments carry the risk.

## Stop Conditions
BLOCK if: the diff cannot be accessed; an invariant is not actually proven; the masks can gap/overlap; covariance is
nominal or does not grow with envelope σ; the impure caveat is missing from the artifact; an exclusion was touched; or
scrutiny point 1/2/3 reveals a real correctness/honesty break (not a tracked simplification).

## Return Format
Return REVIEW_RESULT to `.agent-work/510-driver-utilization-quali/crew-handoffs/g2-review-result.md`: verdict (literal
APPROVE or BLOCK), per-check findings (incl. explicit rulings on the three scrutiny points), blockers, out-of-scope
observations, Workflow Feedback.
