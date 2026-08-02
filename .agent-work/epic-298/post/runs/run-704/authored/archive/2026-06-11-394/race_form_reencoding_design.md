# Race Recent-History Form Re-encoding Design Note

**Issue:** #394  
**Epic:** #453 (Wave 2)  
**Date:** 2026-06-11  
**Status:** DESIGN NOTE — NO-GO / DEFER  
**Part of:** #453, addresses #394

---

## Recommendation

**NO-GO / DEFER** extending pace-gap form encoding to race recent-history modules (`driver_race_power_from_recent_history`, `constructor_race_power_from_recent_history`) until a controlled A/B at the next #440 gold cycle confirms a non-regressive improvement.

---

## Background

Issue #394 asked whether `recent_history_form_encoding = "quali_pace_gap"` (currently hooked to the two quali recent-history modules via `_fetch_pace_gap_map` in `module_adapters/_common.py`) should be extended to the race recent-history modules.

Current behavior: the `form_encoding` field in `RecentHistoryFeatureConfig` exists but `_fetch_pace_gap_map` gates on `task == "quali"`. Race modules always receive the position_quality (v1) path regardless of the config flag.

The race-pace analogue (`integrated_pace_gap` from `src/evo_predictor/race_pace_gap.py`) already exists: mean per-lap `(t - field_median) / field_median` over green-flag, non-pit, completed laps per prior round. DB probe confirms zero null rate for `track_status` across all training years (2018–2025), so the observable is computable without schema changes.

---

## Evidence

### #369 quali A/B (n=24, 2025 eval year)

The only controlled evidence is the quali pace-gap A/B from #369:

| Module | Metric | v1 (position_quality) | v2 (quali_pace_gap) |
|---|---|---|---|
| driver_quali_rh | pairwise_nll_skill | 0.453 | **0.343** (regressed) |
| driver_quali_rh | corr_sigma vs rank_mae | 0.534 | **0.420** (degraded) |
| constructor_quali_rh | pairwise_nll_skill | 0.519 | **0.390** (regressed) |
| constructor_quali_rh | corr_sigma vs rank_mae | 0.427 | **0.494** (improved) |

Ordering was flat as predicted. Pairwise NLL skill regressed in both modules — the opposite of the hypothesis. Constructor sigma improved marginally, driver sigma degraded. With n=24 these are tentative signals with wide confidence intervals.

### #335 promoted bundle (fused Brier 0.2008 vs 0.2077)

The promoted bundle's Brier improvement conflates:
- `quali_pace_gap` encoding change
- Quali head anchor enabled (#420, alpha=0.5)
- Full retrain at higher epochs/lr

The improvement cannot be attributed to encoding alone or to race-RH encoding specifically. It is not evidence for the race extension.

### Promoted race-RH module sigma diagnostics

The promoted bundle (`gold_cycle_260608_043414_2018thru2024`) flags:
- `driver_race_power_from_recent_history`: corr_sigma_vs_rank_mae = 0.268 — `sigma_error_correlation_insignificant`
- `constructor_race_power_from_recent_history`: corr_sigma_vs_rank_mae = 0.574 — `sigma_error_correlation_insignificant`

Both modules' sigma channels are already weak and insignificant at n=24 in the current (position_quality) encoding. A change that matched the quali A/B delta magnitude would not move them into significance territory.

---

## Why NO-GO

1. The closest analogue (#369 quali A/B) showed NLL skill regression in both modules. The hypothesis — that pace-gap encoding enriches the variance channel — was not confirmed at n=24.
2. Race pace is noisier than quali pace (fuel burn, strategy, cautions, track position). The signal-to-noise ratio for a race-pace form quantity is lower, making benefit less certain.
3. The promoted bundle Brier improvement does not isolate race-RH encoding — it is a compound effect.
4. No controlled race A/B exists. A go without one is speculative.
5. The honest-null clause applies: a measured/argued negative is a complete deliverable.

---

## Conditions for a Future GO

A go is defensible at the next #440 cycle if a controlled A/B (isolated race-RH modules, identical training params, n≥24 eval events) shows:
1. `pairwise_nll_skill` non-regressive in both modules; AND
2. Sigma-error correlation improves ≥0.05 OR sign_accuracy improves >0.5pp in at least one module.

---

## Specification (for the future A/B if conditions are met)

- **Quantity**: `integrated_pace_gap` from `src/evo_predictor/race_pace_gap.py`
- **Provider**: new `build_race_pace_gap_history(db, year, round_num)` returning `{driver_id: [gap_round1, ..., gap_round(round_num-1)]}`. Missing rounds → `nan`.
- **As-of contract**: prior rounds only (round 1 through round_num-1). No current-event leakage.
- **Missingness policy**: explicit `nan` where no actionable laps. Availability features already encode coverage.
- **Schema version string**: `driver_race_power_from_recent_history.v2` (enforced by `_check_feature_schema_consistency`).
- **Hook point**: extend `_fetch_pace_gap_map` in `module_adapters/_common.py` to handle `task == "race"`.
- **Promotion gate**: isolated A/B pass, then full gold retrain.

---

## Orthogonality Note

This finding is orthogonal to the #451 race_weekend quali-channel localization finding. Issue #451 found the race_weekend quali head's deficit is feature-representational (missing cross-channel pace input), not form-encoding related. These are distinct mechanisms and distinct modules. The #394 race-RH form-encoding question stands on its own evidence.
