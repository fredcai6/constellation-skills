# IMPLEMENTER_RESULT — g2 (Gap-MAE measurement harness + OOS result)

## Completed slice
Created `scripts/diagnose_quali_gap_scale.py` (DB + committed artifacts; stdlib + numpy; py;
deterministic; runs in seconds, foreground) and `tests/unit/evo_predictor/test_quali_gap_scale_harness.py`
(18 pure-helper tests). Computed OOS 2025 midfield gap-MAE for four scale sources, calibration,
and the flat-ordering confirmation; emitted the evidence JSON.

## Files changed
- `scripts/diagnose_quali_gap_scale.py` (NEW)
- `tests/unit/evo_predictor/test_quali_gap_scale_harness.py` (NEW)
- `.agent-work/issue-391-quali-gap-scale/evidence/quali_gap_scale_numbers.json` (generated)

## Method
Per quali event with a committed quali s_e: read committed s_e (`load_spread_target`),
read-only retro quali pi (`load_retro_solution_for_event`), observed gaps (`compute_pace_gaps`
over `DatabaseManager.get_quali_best_valid_laps_batch` — the SAME query that produced s_e), Q
positions (`diagnose_quali_evidence.classification_order`). Frame: `expected_gap_ij = s*(pi_i-pi_j)`
predicts `observed_advantage_ij = -(gap_i-gap_j)` (the spread_target sign convention). Metric:
pairwise gap-MAE = mean |pred_adv - obs_adv| over undirected non-tie, non-degenerate-pi pairs.
Midfield = both Q positions in [6,15]. Train 2018-2024 / OOS 2025 scored separately, never pooled.

Scale sources: `event` (committed per-event s_e, label ceiling, reference only — EXCLUDED from
winner), `cf1` (carry-forward last-prior-event s_e, as-of safe), `cf2` (same-circuit prior-year
s_e, as-of safe), `global_const` (median of train-pool s_e, the status-quo-ante baseline).

## HEADLINE numbers — OOS 2025 MIDFIELD gap-MAE (lower better)
- event (label ceiling): 0.0019486
- cf1 (last-prior-event):  0.0032578
- cf2 (same-circuit PY):   0.0038252
- global_const (baseline): 0.0032552

## Outcome: HONEST NULL
Neither carry-forward variant beats the global-constant baseline on OOS midfield gap-MAE.
- cf1 beats baseline: FALSE (0.0032578 vs 0.0032552 — essentially tied, baseline marginally ahead by 2.6e-6).
- cf2 beats baseline: FALSE (0.0038252, clearly worse — track-structure carry-forward does not pay off here).
- RECOMMENDED shipped default s_hat_e source = **global_const** (the baseline wins by measurement).

The label-side `event` ceiling (0.0019486) is ~40% below baseline, so event-to-event spread
structure DOES exist and is exploitable in principle — but neither cheap carry-forward heuristic
captures it. That gap is the motivation for the deferred feature->s_e head (#375-shaped triage).

## FLAT-ORDERING CONFIRMATION (the decoupling evidence)
OOS midfield sign-accuracy is IDENTICAL across all four scale sources = 0.938776;
max pairwise spread = 0.000000; is_flat = True. Empirically confirms the algebraic
monotone-invariance: a positive per-event scalar on pi-differences cannot move ordering KPIs.

## Calibration (OOS midfield, observed-on-predicted OLS)
- event: slope 0.999, intercept ~0, r2 0.842 (near-ideal — the label ceiling).
- global_const: slope 0.761, r2 0.538.
- cf1: slope 0.623, r2 0.327. cf2: slope 0.497, r2 0.325.

## Evidence produced
- `py scripts/diagnose_quali_gap_scale.py` -> report above + JSON written.
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale_harness.py -q` -> 18 passed.
- `py -m pyright scripts/diagnose_quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale_harness.py` -> 0 errors.
- `py -m src.utils.simplification_limits --paths ...` -> PASS (2 files checked).
- JSON: `.agent-work/issue-391-quali-gap-scale/evidence/quali_gap_scale_numbers.json`.

## Assumptions / notes
- Retro quali artifacts exist for 2021+ only; 2018-2020 contribute 0 events (train pool effectively 2021-2024, 90 events). Logged in `n_events_by_year`.
- `DatabaseManager` used for best laps (consistency with s_e generation); per-year DB `data/f1_data_<year>.db`. No FastF1; DB is the data source.
- `event` source excluded from winner selection (it is a post-event label, not deployable).

## Stop conditions hit
None. No retrain, no NN inference. Runs in seconds.

## Out-of-scope observations
The ~40% headroom between the label ceiling and every prediction-time source quantifies the
value of a learned feature->s_e head — strengthens the deferred-head triage case (see triage-candidates).
