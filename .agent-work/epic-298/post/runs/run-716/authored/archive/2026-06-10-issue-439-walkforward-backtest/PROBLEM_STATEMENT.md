# Issue #439 — Walk-Forward 2025 Backtest — Consolidated Problem Statement

## Goal
A leakage-free walk-forward backtest of the 2025 season: re-train the model (gold
modules + static fusion + calibration **and** compound priors) at 4 checkpoints
through the year, predict each next quarter, and report a **total-season fantasy
score** across all 24 races with a per-race breakdown and period attribution.
This is the *backtest* product, distinct from the *gold run* (one model trained on
everything, 2025 held out wholesale).

## The 4 periods (clean quarters; 2025 = 24 rounds, all collected)
| Period | Train data | Predicts |
|---|---|---|
| 0 — pre-season | 2018–2024 | R1–6 |
| 1 — ¼ in | 2018–2024 + 2025 R1–6 | R7–12 |
| 2 — ½ in | 2018–2024 + 2025 R1–12 | R13–18 |
| 3 — ¾ in | 2018–2024 + 2025 R1–18 | R19–24 |

## Decisions locked (this conversation)
- **Approach A**: full build + full-fidelity run in one go. No separate smoke-validation gate.
  (Correctness still gated by cheap unit tests on cutoff + compound-rebuild logic — test-led per project rules.)
- **Per-period fidelity = full**: gold cycle → static fusion → calibration → materialize bundles, per period.
- **Period 0 reuses the current promoted gold** model/artifacts (it *is* 2018–2024-trained, 2025 held out;
  config already matches: anchor on, quali_pace_gap). Saves one full training. Must verify promoted artifacts present + config match.
- **Utilization = max** for the heavy trainings (dedicated machine).
- **Report location = Commander's judgement** → new dedicated path `reports/walkforward/` (kept distinct from
  `reports/evo` gold-cycle artifacts that pipeline-validation scrutinizes, and from `reports/strategy` single-race examples).

## New capability required (the real work)
The gold cycle expresses only whole `train_years` + one `eval_year` — **no in-season round cutoff exists**.
Periods 1–3 need a leakage-safe **"train through 2025 round N"** path honored across *every* 2025 input:
- session_classifications, recent-history form, retro-truth labels — no round > N visible to training or to the predicted races;
- **compound prior rebuilt per period** from only 2025 rounds ≤ N (priors are *consumed* by the gold cycle, not rebuilt — the subtle leak);
- anchored config = current promoted gold (quali_pace_gap, anchor on).
Plus: the walk-forward **orchestrator** (4 retrains + per-period cutoffs + per-period compound rebuilds) and **season fantasy aggregation**.

## Acceptance
- Total 2025 fantasy score aggregated over all 24 races (`src/fantasy_scoring/scoring_rules.py`; delta-based "lower is better"),
  with per-race breakdown and which period produced each prediction.
- **No-leakage attestation**: for every scored race, max training round < that race's round, and the compound prior used was built without that race.
- Committed report under `reports/walkforward/`.

## Constraints (from ORCHESTRATOR_CONTEXT / GLOSSARY)
- DB-only analysis; no FastF1/live calls from backtest code.
- As-of cutoffs are first-class; no silent latest-value fallback.
- Test-led changes; `py -m src.utils.simplification_limits` on touched src/tests paths.
- Run from repo root; manifests must use repo-relative paths (portability).
- Evo/probability evidence: calibrated baseline; here the headline metric is the fantasy season score, Brier/log-loss supplemental.
- Push/PR ask-first; commit locally after verification is autonomous.

## Heavy / risk notes
- ~3 full gold+fusion+calibration trainings (periods 1–3) + period-0 reuse = a full day-plus of compute at max util.
- Leakage is the dominant failure mode; correctness of cutoff + compound rebuild is unit-tested before the heavy run consumes hours.
