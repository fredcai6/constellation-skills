# Problem Statement — issue-369-pace-gap-form

**Issue:** #369 — recent_history: re-encode form as % off median lap time

## Statement

Add a flag-gated alternative form encoding to the **quali** recent-history
modules (`driver_quali_power_from_recent_history`,
`constructor_quali_power_from_recent_history`): per past quali event, replace
linear `position→quality` with **pace-gap** `(t − field_median)/field_median`,
where `t` = driver's best valid non-pit Q lap and `field_median` = median of
drivers' best Q laps that event. Window aggregates (mean/median/std), deltas,
head-to-head, and availability machinery run over the new series unchanged in
shape. Priority low: consistency + variance-enrichment refinement, **not** an
ordering-accuracy play (measured flat in the issue's probe).

## Scope decisions (human-confirmed 2026-06-05)

1. **Quali only.** Race recent-history deferred to a triage follow-up (race
   pace-gap is a separate design problem — fuel/SC). Race-start recent-history
   also goes to triage as a **lower-priority investigation**: its per-event
   quantity is already grid→target-lap gain, not position-quality, so the
   issue's "analogously race-start" doesn't apply directly — the follow-up is
   to investigate what form-encoding enrichment means there.
2. **Main, independent of #368.** No code dependency on the unmerged
   `claude/compound-regime-feasibility` branch; only the `(t−median)/median`
   concept is shared. Own config knob in `configs/evo/gold_defaults.toml`
   (e.g. `recent_history_form_encoding = "position_quality" | "quali_pace_gap"`).
3. **Computation locus: data_adapter.** New parallel field
   `DriverFeatures.quali_pace_gap_history_full` populated from `lap_times`
   only when the flag is on — default-off does **zero extra DB work**.
   Adapters stay pure feature consumers. (DB has full Q lap coverage
   2018–2025; valid_lap / pit / track_status columns available.)
4. **Replace, not augment, under the flag.** Flag on → the per-event series IS
   the pace-gap; feature schema bumps to v2 with renamed features
   (`quali_pace_gap_*`). Flag off (default) → today's v1 features
   **bit-identical**. Augment A/B is a possible follow-up.
5. **Value semantics:** raw gaps, no clipping/winsorizing in v1. Lower=better
   (mirrors position polarity → h2h/gap machinery reuses verbatim). Missing
   (no valid lap: DNS, all-deleted, red-flag-only) → excluded + availability
   drop, NOT "slowest" (fixes the DNF→0.0 misread). Empty-window neutral
   becomes 0.0 (= at field median). Forgiveness drops highest-gap events.
6. **Evidence to close:** unit tests + default-off bit-identical proof, then
   targeted A/B — train the two quali recent-history modules flag-on and
   compare σ/error correlation (the variance claim under test) +
   rank_mae/sign-accuracy no-regression (expected ~flat) against the
   flag-off baseline. **No full gold cycle.**

## Protected intent

- Default behavior bit-identical: flag off reproduces current v1 features,
  current bundles, current DB access pattern exactly.
- Training/runtime encoding consistency: a bundle trained with pace-gap must
  be served pace-gap features at runtime; mismatches must fail loudly
  (feature schema version is the marker), never silently fall back.
- DB-only analysis (no FastF1 from adapters); history stays same-season,
  Q-sessions-only, as-of (prior rounds only — no leakage).
- Missingness explicit via existing availability/DQI machinery; no silent
  imputation.

## Non-goals

- Race / race-start recent-history re-encoding (both triaged: race pace-gap
  design; race-start lower-priority investigation).
- Promoting the flag to default-on (needs the A/B evidence first, separate
  decision).
- Any change to fusion, latent_power internals, or the race_weekend (#368)
  encoding.

Confirmed by human 2026-06-05 (AskUserQuestion, 6-question interrogation).
