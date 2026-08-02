# Reviewer Handoff

## Gate
`g4` — Compare (A vs B) + anchor §7.6.4 acceptance + cleanup verifications

## What Was Implemented
Evidence package for the G5 promotion decision: `evidence/comparison.md` (A/B fused verdict), `evidence/acceptance_420.txt` (§7.6.4 anchor acceptance run against the new Arm B quali head), `evidence/cleanup_checks.json`. Plus a default-preserving `--bundle-path`/`--output-dir` argparse addition to `scripts/accept_quali_anchor_420.py` so the harness could target the new bundle.

## How to Inspect
```bash
cd C:/Programs/f1Brainz
git diff -- scripts/accept_quali_anchor_420.py
cat .agent-work/issue-335-gold-regen/evidence/comparison.md
cat .agent-work/issue-335-gold-regen/evidence/cleanup_checks.json
head -60 .agent-work/issue-335-gold-regen/evidence/acceptance_420.txt
```

## Task Statement
Establish (not promote) the evidence: the fused A/B verdict, the anchor acceptance on the new bundle, and the cleanup confirmations.

## Close Criteria (independently verify)
- **A/B numbers traceable**: recompute Arm A vs Arm B mean fused Brier from the two `evidence/arm*/backtest_trained_2025.json` (`per_race[i].metrics.pairwise_brier_against_actual_order`). Expect A≈0.2077, B≈0.2008, B better in 19/24, paired bootstrap 95% CI excludes 0 (≈[−0.0104,−0.0038]). `comparison.md` verdict = promote Arm B (quali_pace_gap).
- **Harness change is SAFE**: `git diff scripts/accept_quali_anchor_420.py` shows ONLY an added argparse (`--bundle-path` default = existing `BUNDLE_PATH`, `--output-dir` default = existing `OUTPUT_DIR`) threaded into `build_numbers()`/`main()`. NO change to `BUNDLE_NAME`/`BUNDLE_PATH`/`OUTPUT_DIR` constants, blend math, `REF_HEADLINE`/`REF_OOS`, or scoring. Confirm a no-arg invocation still targets 260603 (argparse defaults). `py -m src.utils.simplification_limits scripts/accept_quali_anchor_420.py` — the 1 violation (`_score_event_production` 122 lines) must be PRE-EXISTING (verify via `git stash` round-trip), not newly introduced.
- **Acceptance numbers real**: `acceptance_420.txt` shows the run targeted Arm B's `driver_quali_power_from_race_weekend` bundle and reports headline a=0.5 OVERALL ≈0.776 / EASY ≈0.906 and OOS a=0.5 ≈0.762/0.900 — i.e. ≥ the §7.6.4 references (reproduce-or-improve satisfied; "PARTIAL_REPRODUCTION" is an *upward* exceedance, not a miss). Sanity-check alpha=0 ≈ baseline (no-op).
- **cleanup_checks.json**: `nll_ok=true` (both arms' unc_diag have `corr_sigma_pi_trace_vs_nll`, no `_vs_log_loss`), `race_count=24`, threads_note correct (utilization=max ⇒ threads_per_worker=1 per `src/utils/utilization.py`).

## Allowed Scope / Exclusions
Read-only verification + reading the harness diff. Nothing promoted; `params/gold/` untouched. The pre-existing `_score_event_production` limits violation is flagged (tc4) — note, do not block on it. The `oracle_all_states` tc2 is also known.

## Suggested Model Tier
sonnet — bounded evidence + diff verification.

## Stop Conditions
BLOCK if: the A/B Brier numbers don't reproduce or the bootstrap CI does not exclude 0; the harness diff changes default behavior, math, or references; the acceptance didn't actually target the new bundle or is below the §7.6.4 references; or cleanup_checks are wrong.

## Return Format
REVIEW_RESULT: verdict APPROVE/BLOCK, per-criterion findings with commands/results, explicit confirmation that (1) the A/B verdict is sound and CI excludes 0, (2) the harness change is default-preserving, (3) the acceptance targeted the new bundle and meets reproduce-or-improve, blockers, out-of-scope observations.
