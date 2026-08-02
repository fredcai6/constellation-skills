# REVIEW_RESULT — g2 (Gap-MAE measurement harness + OOS result)

## Verdict
APPROVE

## Scope inspected
`scripts/diagnose_quali_gap_scale.py`, `tests/unit/evo_predictor/test_quali_gap_scale_harness.py`,
and `.agent-work/issue-391-quali-gap-scale/evidence/quali_gap_scale_numbers.json`. Re-ran the
harness tests and cross-checked the JSON from the worktree.

## Close-criteria findings
1. Gap-MAE math: `|expected_gap_ij(pi_i,pi_j,s) - observed_advantage(gap_i,gap_j)|`. Sign
   convention consistent with spread_target estimator (`s_e ~= median[-(gap_a-gap_b)/(pi_a-pi_b)]`),
   so `s*(pi_i-pi_j)` predicts `-(gap_i-gap_j)`. Verified by `test_exact_match_is_zero_error`. PASS.
2. As-of safety CF1: `_cf1_scale` includes only events with `(yr,rnd) < (event.yr, event.rnd)` —
   strictly before; no same-event leakage. PASS.
3. As-of safety CF2: `_cf2_scale` uses `prior_year = event.year - 1` only. PASS.
4. Global-constant: single median of train-pool (2018-2024) s_e, applied uniformly to every
   event. One scalar. PASS.
5. Midfield band [6,15] matches diagnose_quali_same_pairs.MIDFIELD_LO/HI. PASS.
6. OOS not pooled with train: `score_regime` called separately on disjoint event sets;
   headline uses OOS only. `history_by_year` feeds CF lookups/global-constant (legitimate
   as-of history), NOT metric pooling. PASS.
7. Flat-ordering genuinely computed: `_flat_ordering_confirmed` reads the actual per-source
   `sign_accuracy` computed in `_score_slice` (not asserted). Reports real spread = 0.0. PASS.
8. Winner by measured MAE: `select_winner` = min over predictive sources, EXCLUDES `event`
   label. Result global_const. PASS.
9. Win/no-win matches JSON: cf1 0.003258 and cf2 0.003825 both > baseline 0.003255;
   honest_null=True; both `*_beats_global_constant`=False. Numbers match the printed report
   and the JSON exactly. PASS.
10. Reuse, no fork: imports compute_pace_gaps, quali_gap_scale (expected_gap_ij + providers),
    load_spread_target, load_retro_solution_for_event, dqe.open_db/classification_order. No
    re-implemented ceiling/gap math. PASS.
11. Honest-outcome reporting: explicit "HONEST NULL" in report + JSON. PASS.

## Apples-to-apples confirmation
OOS 2025: all four sources scored on identical 24 events / 1080 midfield pairs. The per-event
`pairs` set is computed once and shared across sources, so within-event comparisons are exact.
Train-regime attrition (cf1 89/90 events: first event has no prior; cf2 60/90: 2021 events have
no 2020 retro counterpart) is the EXPECTED as-of behavior, not a defect — and the train regime is
context-only; the OOS headline is fully matched.

## Headline (verified)
OOS 2025 midfield gap-MAE: event 0.0019486 (label ceiling), cf1 0.0032578, cf2 0.0038252,
global_const 0.0032552 (baseline). HONEST NULL — neither CF beats the baseline; shipped default
= global_const. Flat-ordering: identical sign-acc 0.938776 across all scales, spread 0.0,
is_flat True (empirical decoupling confirmation).

## Evidence (re-run from worktree)
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale_harness.py -q` -> 18 passed.
- pyright -> 0 errors; simplification_limits -> PASS (2 files).
- JSON cross-checked: n_pairs/events_used consistent; numbers match report.

## Out-of-scope finds
- The ~40% headroom between the label ceiling (0.001949) and every prediction-time source
  quantifies the value of a learned feature->s_e head. Strengthens the deferred-head triage
  candidate (already flagged for triage). Not in this gate's scope.
