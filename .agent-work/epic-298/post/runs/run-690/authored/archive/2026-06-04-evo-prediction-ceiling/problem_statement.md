# Problem Statement — evo-prediction-ceiling

## One-line
Re-level the race-start σ to its correct held-out calibration level, and make the
`wrong_sign`/`near_zero` σ_corr diagnostic statistically honest — so an n=24
noise blip stops being reported as a model defect.

## Origin
`docs/evo/prediction_ceiling_and_priorities.md` names the **race-start σ mis-level
(negative `sigma_corr`)** as the "concrete, bounded first win" of Thrust B.

## What investigation found (current bundle `gold_cycle_260603_173742`)
- The pooled race-start `sigma_corr = −0.065` decomposes into:
  - `driver_race_start_power_from_recent_history`  = **−0.119** (wrong-sign flag)
  - `constructor_race_start_power_from_recent_history` = **−0.092** (wrong-sign flag)
  - `driver_race_start_power_from_race_weekend` = **+0.108** (fine)
  - `constructor_race_start_power_from_race_weekend` = **+0.206** (fine)
- n=24 events; race-start is the most deterministic phase (driver rank_mae ~1.2–1.7
  vs quali ~3.5–5). A |corr|≈0.1 on n=24 has ~95% CI ≈ ±0.4 → indistinguishable
  from zero. The `wrong_sign` flag fires on a hard `< 0` threshold with no
  significance test.
- The existing σ calibration `calibrated_σ = α·trace + β·dof` (grid-fit vs
  `rank_mae²`, `gold_cycle/calibration.py`) is **monotone in trace → cannot flip
  the correlation's sign**; α stays pinned at 1.0 and β hits the grid boundary on
  5 modules (the additive term is straining).
- Per-event rows (`event_level_metrics`, 12 modules × 24 events) are persisted in
  `reports/evo/gold_cycle_260603_173742_2018thru2024.details.json` → `sigma_corr`,
  coverage, and recalibration variants are **recomputable offline (no torch/retrain)**.

## Chosen approach — Path 1 ("level + honest flag")
1. **Re-level race-start σ** so its *level* is calibrated to realized held-out error
   dispersion (the genuine "too high / too flat"), via the existing calibration
   seam. Do **not** attempt to flip the correlation's sign.
2. **Significance-gate the σ_corr diagnostic** (`wrong_sign` / `near_zero`) so a
   correlation statistically indistinguishable from zero at the event count is not
   reported as a defect, while genuine significant wrong-sign cases still flag.

## Scope
**IN**
- Race-start σ level recalibration (the mis-leveled phase) via the existing seam.
- Significance/noise-aware gating of the σ_corr diagnostic in
  `module_uncertainty_diagnostics.py` (stats-honesty; applies wherever the flag is
  computed).
- New/updated evo unit tests for the calibration target and the flag gate.
- Offline verification on persisted held-out 2025 rows.
- Update `docs/evo/prediction_ceiling_and_priorities.md` to record the decomposition
  and the corrected "mis-level" understanding.

**OUT (this run)**
- Changing σ *production* (`latent_power/modules.py`) or adding event-conditioned σ
  features.
- Forcing `sigma_corr ≥ 0`.
- Quali/race phase re-leveling beyond what the global diagnostic gate touches.
- The broader "context-conditioned σ floor" (separate Thrust B item).
- The full gold retrain (deferred to a tracked triage item).

## Done-bar (offline + deferred retrain)
- Offline recompute on held-out 2025 rows: re-leveled race-start σ shows correct
  coverage/calibration (predicted σ level matches realized error dispersion); the
  honest flag no longer fires on the two noise-level modules **and** still fires on
  a synthetic significant-negative input.
- Evo unit suite green, incl. new tests.
- `py -m src.utils.simplification_limits` on touched paths (strict).
- Doc updated.
- Triage item filed: confirm fused-Brier neutral-or-better at the next scheduled
  gold cycle (the deferred "Brier primary" gate, tracked per compromise policy).

## Protected intent / invariants
- σ-only change: do **not** alter ranks or means; quali/race *levels* stay untouched.
- No leakage: preserve the existing blocked train-year split that excludes eval_year
  (2025).
- Named/configured mechanism — no hidden inline tuning; one canonical calibration
  path (extend the existing seam, no parallel one).
- Deferred Brier confirmation is a tracked compromise, not a silent skip.
