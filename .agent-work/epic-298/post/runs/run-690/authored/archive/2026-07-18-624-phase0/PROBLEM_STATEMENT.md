# Problem statement — issue #624, Phase 0 probes

Reconciled 2026-07-18 against launch order `ShipB-624` and current code (branch `feat/624-phase0-probes`, base `main` 16c314b9).

## Ask (from launch order)

Run five Phase-0 probes on EXISTING data/estimates (no new estimator modeling): (1) partial-correlation screen of physics axes vs evo's quali error, controlling for evo's existing recent-history features, with a pre-registered primary axis/composite; (2) a wide-σ A/B checkpoint pushing the existing five-view estimates through the residual-history injection seam; (3) an integration tracer pushing one real weekend through the real four-record contract; (4) an SQ coverage probe of the Q estimator; (5) a baseline lock freezing x4's relative-normalization floor and x7's five-fracture checklist. Plus confirm #623's headless fix is green.

## Baseline reconciliation (assumed-vs-verified)

| Launch-order claim | Verified? | Evidence |
|---|---|---|
| #623 headless deadlock fixed & merged, base `main` 16c314b9 | CONFIRMED | `git worktree list` shows both checkouts at `16c314b9`; `run.py` thread-cap fix is on this base by construction. |
| `data/physics_estimates.db` `session_estimates` holds Q estimates 2019–2026 | CONFIRMED | 1597 rows, `session_type='Q'` only (no `SQ` rows — confirms the SQ probe is genuinely unrun), years 2019(210)/2020(170)/2021(220)/2022(220)/2023(220)/2024(240)/2025(240)/2026(77). |
| 11 physics axes exist in the store | CONFIRMED | `session_estimates` columns: `drag_area_closed_m2`, `brake_decel_ms2`, `brake_aero_decel_per_m`, `traction_accel_ms2`, `traction_aero_accel_per_m`, `max_power_w`, `power_drag_area_m2`, `lateral_mech_grip_g`, `lateral_aero_grip_g`, `coast_rolling_decel_ms2`, `coast_drag_area_m2` (11 axes, matches x4 "all 11 axes"). Store is per-`(year, gp_name, session_type, constructor)`, not per-driver. |
| `*_from_recent_history` modules build a direct injectable field prototype | CONFIRMED | `driver_residual_history_adapter.build_neutral_driver_residual_history_field()` (`src/evo_predictor/driver_residual_history_adapter.py:32-115`) is a pure `(residual_mean, residual_variance) -> ModuleFieldResult` injector; today always runs in the neutral (zero-mean, huge-σ) branch because nothing populates `RuntimeModuleContext.driver_residual_states` (`module_context.py:25`; consumed at `module_adapters/_runtime_builders.py:562`). This is the confirmed wide-σ A/B injection seam. |
| SQ already used as quali evidence on current main | CONFIRMED, and traced onto the LIVE prediction path | `data_adapter/_build.py:449-451` (`db.get_session_classification(year, round_num, "SQ")`) is reached from `sampled_runtime.py:21` → `build_sampled_runtime_features` → `build_race_features` (`_helpers.py:237`). Not just backtest scaffolding. |
| `estimate_session` applies `quali_mass()` unconditionally, no `fp_mass()` | CONFIRMED | `src/physics/layer2/session_estimator.py:125` calls `quali_mass(year)` unconditionally; zero `def fp_mass` hits in `src/`. |
| **Evo's own "quali error" is a ready-made artifact to join against** | **NOT CONFIRMED — genuine gap, resolved within latitude (see below)** | No script/table produces a per-`(year,round,driver)` predicted-vs-actual quali residual. `scripts/diagnose_quali_same_pairs.py` computes pairwise sign-accuracy from committed per-event module records (`.agent-work/issue-381-same-pairs/records/`), but that records directory does not exist on disk (ephemeral, issue-381-only) and regenerating it needs `backtest-latent-power-module --emit-module-record` runs per module per year. |

## Gap resolution (within delegated latitude, not floated)

The launch order pre-registers the *method* (semi-partial correlation, physics axis residualized against recent-history features) but leaves "evo's own quali error" underspecified, and the two candidate constructions trade off cost against fidelity:

- **Full-fidelity option**: run `backtest-latent-power-module --emit-module-record` for the trained recent-history quali module across 2019–2026, convert `pi` → rank, diff against `actual_positions`. This needs the NN-bundle inference path (not the 3-stage sampler, but still model-loading machinery) across ~8 seasons — heavier than "pure DB/pandas," and risks looking like new-modeling scope creep for a Phase-0 probe explicitly scoped to avoid it.
- **Chosen option (pure DB/pandas, no model inference)**: operationalize "evo's own recent-history feature" and "evo's quali error" from the SAME primitive the launch order names — `DriverFeatures.quali_pace_gap_history_full` (`src/evo_predictor/models/_features.py:39`, prior-Q pace gaps in raw seconds from field median, calendar order; consumed by `quali_recent_history_adapter.py:114-163`). Define, per `(year, round, driver)`: `recent_history_baseline` = trailing mean of that driver's own prior-Q pace gaps (the literal existing recent-history feature), and `quali_error` = `actual_pace_gap − recent_history_baseline` (the part of the outcome recent-history's own signal does not explain). This is exactly a semi-partial-correlation setup by construction — no OLS-against-a-feature-vector step is needed because the residualization IS the recent-history feature itself — computable via pure DB reads + pandas, no sampler, no NN bundle load, matching the pre-ruling ("does NOT need the sampler") precisely.

This is a **documented methodological choice**, not a scope cut or an architecture decision — it stays within "run analyses... write findings/artifacts" latitude. Limits are stated plainly in the verdict: this measures whether physics beats a *specific, simple* recent-history baseline (trailing mean of the driver's own past Q gaps), not the fused live model's actual prediction error — it is informational (per F7's disposition), not the G1 ceiling answer, and is reported as such.

## Pre-registered primary axis (registered BEFORE computing any correlation — see `PRE_REGISTRATION.md`, this file's sibling, timestamped ahead of the g1 analysis script)

Primary = **total peak lateral capability** = `lateral_mech_grip_g + lateral_aero_grip_g` (both already in the store, additive g-units). Rationale: F1Brainz's own prior #445 axis-consolidation finding (`src/physics/capability.py:110-112`, `docs/architecture/packets/physics.md:246-249`) validated that cornering/apex-speed capability is the dominant pace axis (−0.89) vs. drag CdA (−0.50, secondary) — a different computation pathway (`ApexPace` over raw `ApexObservation`s) but the same underlying physical concept; `lateral_mech_grip_g + lateral_aero_grip_g` is the `session_estimates`-table analog of that validated concept, chosen for physical coherence (total lateral-g ceiling), not by peeking at this run's correlations. Secondary/exploratory axes: the other 9 raw columns, reported separately and clearly labeled non-primary.

## Scope confirmation

All 5 probes are informational per F1/F11/the Honest-Null Clause. No kill switch. No Phase 1-6 machinery will be built if a probe needs it (float instead — see Pre-Ruling #3). Confirmed via `attach understand --type user-decision --field cite='LAUNCH_ORDER:Mission'`.
