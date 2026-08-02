# Triage recommendations — #626 Phase 2 (delegated; Admiral is filing authority for #601 graph)

Filing into the epic #601 issue graph is the Admiral's call (delegated run, no reachable human).
All non-fixed candidates are `recommend-and-defer`; the Admiral files/routes at the epic boundary.

## tc1 — F6 gate per-axis coverage floor — DISPOSITION: fixed-now
- **What:** `gate_spec.evaluate_axis` had no per-axis minimum car-season-coverage floor; a model abstaining on hard car-seasons could game the ≥7/11 tally with thin coverage.
- **Fix:** folded into g5 `gate_f6.py` as `MIN_COVERED_CAR_SEASONS=5` (an axis-beat requires ≥5 held-out car-seasons; coverage reported per axis). Strictly tightening — can only remove beats. Verified by g5 review (max_power cov=3 correctly excluded).
- **Fix commit:** 6dab8d5a (g5). Label: research hardening.

## tc3 — Per-car representative-lap session-time bridge (UN-FLOAT LAYER 2) — DISPOSITION: recommend-and-defer + ARCHITECTURE FLOAT
- **What:** Layer 2 (within-session grip evolution) is REAL and identifiable (slope +0.00196 g/lap, t=28.4, LOO −2.56% held-out, orthogonality r²≈0) but acts as a wide-σ no-op on the frozen split because `physics_estimates.db:session_estimates` has NO per-car representative-lap `cumulative_track_laps` — so the field-level track-state latent is absorbed by the weekend-median subtraction and cannot become a per-car de-bias.
- **Unlock:** record each car's representative-lap `cumulative_track_laps` (the track-rubbering state when that car set its Q time) into `session_estimates`. Then Layer 2 becomes a per-car track-state de-bias that survives median subtraction. Secondary: backfill Q grip bins beyond 2023 (`grip_bin_obs` Q = 2023-only); measure a grip-g → 11-axis-unit map.
- **Why FLOAT:** adding a column sourced from the estimator/telemetry to `session_estimates` touches the estimator/store public surface — an architecture change beyond this issue's "build the weekend-state model" latitude. Admiral decision.
- **Importance:** HIGH — it is the concrete path to make the within-session-evolution layer do real work; without it Layer 2's marginal contribution stays ~0 (confirmed by the g5 ablation). Label: research hardening / architecture weakness / feature.
- **Acceptance:** `session_estimates` carries a per-(year,gp,constructor) representative-lap track-laps field; Layer 2 re-run shows non-zero held-out marginal contribution on the F6 ablation.

## tc2 — Weather data-source anchor (f1_data → telemetry_store) — DISPOSITION: recommend-and-defer
- **What:** measured session weather (Pressure) lives in `telemetry_store.tele_weather`, NOT `f1_data_<year>.db` (no Pressure column). Handoffs/docs citing f1_data for weather are stale.
- **Status:** the arch map was corrected this run (Cartographer recorded telemetry_store as the density source). Remaining: audit durable project docs (CLAUDE.md / collector docs) for any stale f1_data-weather references.
- **Deferral reason:** durable-doc audit is outside this issue's file scope; filing is Admiral's. Label: missing doc / stale reference.

## tc4 — gate_f6._axis_coverage duplication — DISPOSITION: recommend-and-defer
- **What:** `gate_f6._axis_coverage` re-derives the floor∩model∩guard-pass intersection that `gate_spec.evaluate_axis` already computes — low-severity duplication / future-drift risk, correct today.
- **Deferral reason:** clears the fix-now rungs (bounded, adjacent, verifiable, no arch impact) BUT I decline to refactor the F6 gate harness immediately after it was frozen + independently reviewed + its PASS reproduced — a cosmetic DRY change would disturb a load-bearing reviewed artifact and require re-review for no behavioral gain. Better as a standalone cleanup. Label: cleanup.

## Also noted (Cartographer OSQ) — hardcoded main-checkout DB_PATH — DISPOSITION: recommend-and-defer
- **What:** the `weekend_state` modules hardcode the absolute main-checkout `physics_estimates.db` path (worktree-untracked-data workaround). Portability/config debt.
- **Deferral reason:** intentional for this delegated worktree run; a config-driven path is a small future cleanup. Label: cleanup / tooling.
