# Mission Frame — #522 phase-align (or per-regime-frontier) the utilization comparison

## Intent

Make the C1 per-regime driver-utilization measure (`U_r`) physically bounded and trustworthy for braking/fast-corner — replacing the point-aligned `v_real/v_ideal` ratio (which clips at 2.0 from a corner-misregistration artifact) with a comparison method **chosen by gate-1 diagnosis**, then re-run C1 and re-assess the verdict. Map is fresh/high-confidence here (reconciled by #518); the run's uncertainty is empirical (root cause a vs b), so gate-1 is a diagnosis gate, not a map-scout.

## Affected Capabilities

- **per-regime driver utilization** (`struct:physics.utilization`) — currently `U_r = mean(v_real_i/v_ideal_i)` on a progress-resampled shared grid; braking/fast-corner clip at `U_CLIP_MAX=2.0`. This run changes *how the realised lap is compared to capability* (the denominator/registration), not the capability measurement.
- **ideal-lap simulation / two-sided evaluation** — the QSS ceiling (`PhysicsSimulator`) stays correct; its *consumption* by utilization changes (gate-1 decides whether it stays the denominator with corrected alignment, or is replaced by measured per-view frontiers).

## Examples / Events

- Monaco/VER fast corner: `v_ideal≈17` (tight-corner cap) divided into a progress-misregistered `v_real≈63` (fast-corner real speed) → 3.79× → clipped. The canonical failure this run must make read `U≈1`.
- A real lap genuinely at the car's braking limit must read `U≈1`, not 2–4× (acceptance criterion).

## Structural Anchors

- `struct:physics.utilization` — `src/physics/utilization/`, component. `regime_utilization.py` (the comparison core + `U_CLIP_MAX`), `characterize.py` (orchestration seam), `car_prior.py` (ceiling assembly).
- `struct:physics` — `physics_simulator.py` (`simulate_lap` forward/backward QSS, `_compute_speed_caps`), `sim_evaluator.py` (`resample_by_progress` — the progress-normalization at fault), `capability_envelope.py`.
- `struct:physics.layer2` — the five measured per-view frontiers (`braking_view`, `lateral_view`, `traction_view`, `power_drag_view`, `coast_view`, `frontier_fit`) — the reuse basis for fix-option B.
- `scripts/driver_utilization_dashboard.py` — the re-run / verdict surface.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — utilization stays measurement-only; no evo import (verified posture).
- Physics rigor (ORCHESTRATOR_CONTEXT): truth-anchored L1–L4 evidence, units/bounds/invariants explicit; `py` launcher; SQLite/FastF1-cache read-only via absolute main-checkout paths from any worktree.
- `assumption`: ribbon geometry approximates the real lap's line closely except near sharp speed transitions (the misregistration is local to knees) — gate-1 tests this.

## Decision Anchors & Decision Pressure

- `decision:c1_driver_utilization_design` — causal through-W constructor denominator; both teammates define the frontier; `split_is_impure=True` always; single canonical ideal-lap path. **Review trigger active** (ceiling/comparison recalibration).
- `decision:ideal_lap_sim_two_sided_evaluator` — ideal lap = two-sided evaluator, not predictor; small gap = under-call-suspect. **Review trigger explicitly names "phase-alignment fix landing."**
- **Decision pressure (forced to human at gate-1 checkpoint):** which comparison method — (a) true-distance/landmark-aligned ratio (keeps the ideal-lap denominator) vs (b) per-regime measured-frontier comparison (drops it). Resolved by gate-1 evidence, then confirmed by the human. This becomes a new/updated decision anchor at reconcile.

## Claims / Evidence Surfaces

- `claim`: post-fix, a real lap at/under capability reads `U≈1` (braking + fast-corner no longer pinned at 2.0). Re-confirmed by the gate-3 dashboard re-run.
- `claim`: straight `U` stays physical (~1; no spurious >1 over-call). Re-checked at gate-3.
- `claim`: honest covariance preserved (envelope σ + lap-sampling σ quadrature). Re-confirmed by gate-2/3 tests.
- Evidence: physics unit suite (`test_regime_utilization.py`, `test_driver_utilization_dashboard.py`, `test_utilization.py`, `test_ideal_lap_top_speed_invariant.py`) + the gate-1 diagnosis traces + gate-3 dashboard output.

## Map Confidence / Staleness / Disputes

- `struct:physics.utilization` — **high confidence, fresh** (reconciled #518, 2026-06-26). The packet already documents the KNOWN METHOD FLAW this run fixes. No map-scout needed; gate-1 verifies the *empirical* root cause, which the map cannot settle.

## Out of Scope

- The braking estimator / ceiling depth (#518 done). The sim units fix (#518 G5 done). Wiring the other 4 C1 constructors. Composing C-outputs into prediction (#509 P-phase). The lateral-frontier Gsat-fallback softness is in-scope only as a *finding* if gate-1 lands on (b); a full lateral-frontier rebuild routes to triage.
