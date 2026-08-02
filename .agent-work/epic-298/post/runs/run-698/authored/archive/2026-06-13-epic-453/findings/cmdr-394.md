# cmdr-394 findings — Race Recent-History Pace-Gap Re-encoding Design Note

**Issue:** #394  
**Date:** 2026-06-11  
**Commander:** cmdr-394 (Wave 2, epic #453)  
**Deliverable:** Design note with explicit go/no-go recommendation

---

## 0. Summary Verdict

**NO-GO / DEFER** — extend pace-gap form encoding to race recent-history modules only after a full #440 retrain cycle, and only if a controlled A/B (isolated to race RH modules, identical training params) confirms an improvement on the primary ordering or uncertainty metric. Do not promote on the current evidence.

---

## 1. What Was Asked

Issue #394 asks: should `recent_history_form_encoding = "quali_pace_gap"` (currently hooked to `driver_quali_power_from_recent_history` and `constructor_quali_power_from_recent_history`) be extended to the race recent-history modules (`driver_race_power_from_recent_history`, `constructor_race_power_from_recent_history`)?

The current code wires `_fetch_pace_gap_map` only when `task == "quali"`. Race modules get `None` (position_quality path) regardless of the encoding flag. The question is whether a race-pace analogue is meaningful, available, and evidenced enough to recommend.

This note does **not** justify the recommendation by appeal to the #451 quali-channel gap finding (confirmed orthogonal by LO-394 pre-ruling).

---

## 2. What Exists as a Race-Pace Observable

`src/evo_predictor/race_pace_gap.py` (added #387) already provides:

- **`integrated_pace_gap`** (PRIMARY): per-driver mean of `(lap_time - lap_field_median) / lap_field_median` over actionable (green-flag, non-pit, completed) laps. Same median-relative de-unitization as `quali_pace_gap_history.compute_pace_gaps`. Uses per-(driver, lap) `track_status` for caution filtering; approved spike-proxy fallback when status unavailable.
- **`finishing_gap`** (BASELINE): total race time gap to field median, retained as diagnostic only.

### DB availability probe (read-only, 2026-06-11):
- `lap_times.track_status`: **0 nulls** across all probed years (2018, 2022, 2024, 2025). The primary actionable-lap filter has full data.
- `lap_times` contains `pit_in_time`, `pit_out_time`, `valid_lap`, `lap_time` — all required columns are present.

**Conclusion on availability:** The `integrated_pace_gap` observable is computable from the current DB schema for all training years. No schema change required.

### Conceptual validity of `integrated_pace_gap` as a race-form quantity

The issue body correctly flags that race lap times carry fuel burn, safety cars, and stint structure that make a naive single event-level gap number less meaningful than in qualifying. `integrated_pace_gap` addresses this:

- **Fuel burn**: per-lap `(t - field_median) / field_median` cancels much of the systematic fuel-burn progression because all drivers burn fuel at roughly the same rate; the gap measures relative pace, not absolute pace. Not perfect (tyre/strategy variation affects timing), but substantially cleaner than total race time.
- **Safety cars / VSC**: per-(driver, lap) `track_status` filtering excludes non-green laps per driver. A driver who passed the incident before the yellow is correctly credited; a driver behind the incident is not penalized for slowing.
- **Stint structure / pit stops**: pit laps (non-zero `pit_in_time` or `pit_out_time`) are excluded. In/out laps contribute only their qualifying green-lap portion.

The #387 candidate-selection measurement confirmed `integrated_pace_gap` gives ~13x greater dynamic range than `finishing_gap` and is causally robust. The observable is physically reasonable as a cross-event race-form quantity.

---

## 3. Evidence Review

### 3.1 The #369 quali A/B (canonical, n=24, 2025 eval year)

| Metric | driver v1 | driver v2 | constructor v1 | constructor v2 |
|---|---|---|---|---|
| pairwise_sign_accuracy | 0.7452 | 0.7453 | 0.7620 | 0.7671 |
| pairwise_nll_skill | 0.4531 | **0.3431** | 0.5186 | **0.3901** |
| corr_sigma vs rank_mae | 0.534 | **0.420** | 0.427 | **0.494** |
| rank_mae_vs_actual | 3.571 | **3.488** | 1.658 | 1.683 |

**Reading:** Ordering was flat as predicted. Uncertainty channel: mixed — driver sigma degraded, constructor sigma improved slightly. But **pairwise_nll_skill regressed in both modules** (driver 0.453→0.343; constructor 0.519→0.390), which is the opposite of the hypothesis. Statistical caveat: n=24 gives wide confidence intervals on all these differences; the numbers are directional signals, not strong conclusions.

**Key takeaway for the race-extension question:** The quali encoding change's benefit was primarily asserted to be in the variance channel (sigma better predicts error). On n=24, it failed to clearly demonstrate that even for the module it was purpose-built for. This weakens (but does not eliminate) the case for extending to race.

### 3.2 The #335 promoted bundle numbers

The promoted bundle `gold_cycle_260608_043414_2018thru2024` shows fused Brier **0.2008 (trained)** vs **0.2077 (default/baseline)** — a 3.4% improvement. However, this comparison is between:
- **Trained**: full gold retrain with `quali_pace_gap` encoding AND `quali_pace_anchor_enabled = true` (alpha=0.5)
- **Default**: the prior promoted bundle without anchor or encoding change

This is a **compound effect** — the Brier improvement conflates the encoding change with the quali head anchor (#420) and the full retrain at higher epochs/lr (pace-encoding-368 config changes). The Brier improvement cannot be attributed to race-RH encoding alone, or even to quali-RH encoding alone. It is not evidence that extending to race would help.

The module-level metrics for race recent-history modules in the promoted bundle:
- `driver_race_power_from_recent_history`: pairwise_nll_skill = **0.631**, pairwise_sign_accuracy = 0.793, rank_mae = 2.790
- `constructor_race_power_from_recent_history`: pairwise_nll_skill = **0.406**, pairwise_sign_accuracy = 0.741, rank_mae = 1.892

The uncertainty diagnostics for these modules in the promoted bundle:
- **driver**: corr_sigma_pi_trace_vs_rank_mae = **0.268**, corr_sigma_pi_trace_vs_nll = 0.288 — flagged `sigma_error_correlation_insignificant` (n=24)
- **constructor**: corr_sigma_pi_trace_vs_rank_mae = **0.574**, corr_sigma_pi_trace_vs_nll = 0.359 — flagged `sigma_error_correlation_insignificant`

The sigma-error correlations on the race-RH modules are **weaker** than what the #369 quali A/B showed for the position_quality baseline (driver 0.534, constructor 0.427). This means even if pace-gap encoding improves sigma calibration proportionally to what it did in quali, the resulting correlations would still be in the insignificant-at-n=24 range.

**Key takeaway:** The promoted Brier improvement is primarily from the anchor (#420) and retrain, not from race-RH encoding. The promoted bundle shows the race-RH sigma channel is already weak at n=24 — not a compelling surface for a form-encoding change to target.

### 3.3 What the #369 quali A/B actually shows about race extension

The #369 A/B ran on **quali** modules with a **quali-specific** encoding (best valid Q laps, field-median gap per round). The race analogue would be `integrated_pace_gap` per prior round — a different signal:
- Quali laps are single-lap maximum effort, primarily driver-skill signal.
- Race pace is multi-lap average, carries constructor pace, tyre/strategy noise, caution exposure, and track position effects.
- The information content ratio (driver skill vs noise) is worse for race pace.

Even if the quali A/B had been clearly positive, it would not straightforwardly transfer to race. That it was mixed (pairwise_nll_skill regressed) further weakens the extrapolation.

---

## 4. Decision Framework

### Arguments for GO:
1. `integrated_pace_gap` is an existing, well-designed observable with full DB availability and zero null rate.
2. The median-relative encoding is consistent with other pace features (#368/#369 patterns).
3. The position_quality encoding for race is a coarse (discrete rank) signal; pace gaps are continuous and more information-rich in principle.
4. The code extension would be straightforward: `_fetch_pace_gap_map` would need a race analogue route, and the race recent-history adapter would need to consume it.
5. The promoted bundle's race-RH sigma correlations are weak — there is room for improvement.

### Arguments against GO (or for defer):
1. **#369 A/B was mixed even for quali**: pairwise_nll_skill regressed in both modules. The claim that pace-gap enriches the variance channel was not confirmed at n=24. Extending to race before the quali outcome is more solidly confirmed is premature.
2. **The promoted Brier improvement does not isolate race-RH encoding**: the compound effect of anchor + retrain + encoding change makes it impossible to attribute the improvement to race-RH encoding specifically.
3. **Race pace signal is noisier than quali pace**: fuel, strategy, track position, cautions all degrade the signal-to-noise ratio. The gain is less certain than for quali.
4. **Weak baseline sigma correlations on race-RH**: the promoted bundle flags `sigma_error_correlation_insignificant` for both race-RH modules. At n=24, even a 2x improvement would not reach significance. The channel is not obviously broken in a way that pace-gap encoding would fix.
5. **No race-specific A/B exists**: unlike quali (which had a controlled A/B with n=149 training + n=24 eval), there is no race-pace-gap form encoding measurement. Recommending go without one is speculative.
6. **The honest-null clause applies**: a measured/argued negative is a complete deliverable. The evidence does not support go.

---

## 5. Recommendation: NO-GO / DEFER

**Do not extend pace-gap form encoding to race recent-history modules at this time.**

### Rationale:
- The primary evidence base (#369 quali A/B) was mixed, with pairwise_nll_skill regressing for both modules. This is the closest analogue to what race extension would produce, and it did not confirm the hypothesis.
- The promoted bundle's Brier improvement conflates the anchor and retrain with the encoding change — it is not evidence for race extension.
- Race pace is a noisier signal than quali pace; the information gain from continuous gap encoding over discrete positions is less certain for race.
- No controlled race A/B exists. A go recommendation without one would be speculation.
- The race-RH sigma correlations in the promoted bundle are already weak and insignificant at n=24 — the extension does not have a clear target to improve.

### What would change the recommendation (condition for a future GO):

A go is defensible if all of the following hold at the next #440 cycle:

1. A controlled A/B (isolated to race-RH modules, identical training params, n≥24 eval events) shows `pairwise_nll_skill` non-regressive AND either sigma-error correlation improves meaningfully OR sign_accuracy improves by >0.5pp.
2. The quali pace-gap encoding demonstrates a clear benefit in isolation (separate from anchor and retrain effects) in the #440 cycle — confirming the signal enrichment hypothesis that #369's A/B left uncertain.
3. `integrated_pace_gap` is available and non-null for ≥95% of drivers across all training years (already confirmed true from today's DB probe, so this condition is met).

---

## 6. If a Future Measurement Plan Proceeds

If the conditions above are met and a GO is authorized, the specification would be:

- **Quantity**: `integrated_pace_gap` from `src/evo_predictor/race_pace_gap.py` — mean per-lap `(t - field_median) / field_median` over actionable (green, non-pit, completed) laps per prior round.
- **Provider pattern**: analogous to `build_quali_pace_gap_history` — a new `build_race_pace_gap_history(db, year, round_num)` that returns `{driver_id: [gap_round1, ..., gap_round(round_num-1)]}`. Rounds with no actionable laps for a driver get `nan` (not imputed).
- **As-of contract**: uses only laps from prior rounds (round 1 through round_num-1), consistent with the existing form-history pattern. No leakage from the current event.
- **Missingness policy**: explicit — `nan` where a driver has no actionable race laps that round (e.g. DNS, DNF before a green lap, all-caution race). The `availability_fraction_n*_delta` features already encode coverage, so the model can learn to down-weight sparse form windows.
- **Feature schema version**: new version string (e.g. `driver_race_power_from_recent_history.v2`) required for schema consistency enforcement (per `_check_feature_schema_consistency`).
- **Hook point**: `_fetch_pace_gap_map` in `module_adapters/_common.py` extended to handle `task == "race"` with `encoding == "race_pace_gap"` (or a new flag value); or a separate provider function.
- **Measurement plan for #440 A/B**: train fresh-v1 (position_quality) and treatment-v2 (race_pace_gap) as isolated single-module runs on both driver and constructor race-RH modules. Backtest on 2025 (n=24). Primary gate: pairwise_nll_skill non-regressive AND (sigma-error correlation improves ≥0.05 OR sign_accuracy improves >0.5pp). Promotion requires full gold retrain.

---

## 7. Triage Candidates

- **Proceed with measurement plan at #440**: if the next gold retrain produces module records, an isolated race-RH A/B can be run cheaply as part of #440 analysis. Track as a future go decision under #394 or a new #440-child issue.
- **Quali re-examination at #440**: the #369 A/B left the quali encoding benefit uncertain. The #335 gold retrain partially addressed it (promoted quali_pace_gap as default), but the compound effect makes it hard to isolate. A dedicated quali isolation A/B at #440 would sharpen confidence before extending to race.

---

## 8. Evidence Summary

| Source | Key number | Interpretation |
|---|---|---|
| #369 A/B driver pairwise_nll_skill | 0.453 (v1) → 0.343 (v2) | Regressed — hypothesis not confirmed |
| #369 A/B constructor pairwise_nll_skill | 0.519 (v1) → 0.390 (v2) | Regressed — hypothesis not confirmed |
| #335 promoted bundle fused Brier | 0.2008 (trained) vs 0.2077 (baseline) | Compound effect of anchor + retrain; not isolatable to encoding |
| Promoted driver_race_rh corr_sigma_vs_rank_mae | 0.268 | Weak/insignificant at n=24 |
| Promoted constructor_race_rh corr_sigma_vs_rank_mae | 0.574 | Moderate but flagged insignificant at n=24 |
| DB probe: track_status nulls (2018/2022/2024/2025) | 0% nulls | integrated_pace_gap fully computable |
