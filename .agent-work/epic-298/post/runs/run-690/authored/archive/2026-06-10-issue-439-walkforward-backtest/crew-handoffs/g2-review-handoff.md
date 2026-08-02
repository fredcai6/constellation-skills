# Reviewer Handoff

## Gate
`g2` — Leakage-safe in-season as-of cutoff primitives. **Leakage is the dominant failure mode — review rigorously.**

## What Was Implemented
Eval-year split in training-data assembly (eval_year rounds `<= N` join TRAIN; EVAL = explicit round range),
an as-of-N compound-prior BUILD path (`--through-round N`, DB-only), and config plumbing. Primitives + tests
only (no orchestrator). New params:
`prepare_module_training_data(..., eval_year_train_through_round, eval_round_range)`,
`build_labeled_batches_for_module(..., round_filter)`,
`run_season_alignment.run_year(..., through_round=N, skip_collection=True)`.
Reported: 21 new tests pass; 99 regression pass; simplification PASS on 6 touched files.

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git status --short
git diff --stat
git diff -- src/evo_predictor/module_training_orchestration.py src/evo_predictor/module_training_holdout_modes.py scripts/run_season_alignment.py src/evo_predictor/gold_cycle/config.py
```
New tests (untracked): `tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py`.

## Task Statement
Build leakage-safe "train through eval-year round N" primitives. Full spec:
`.agent-work/issue-439-walkforward-backtest/crew-handoffs/g2-handoff.md`. Implementer result:
`.agent-work/issue-439-walkforward-backtest/evidence/g2-implementer-result.md`.

## Close Criteria (each a review check — verify INDEPENDENTLY, don't just trust claims)
- **Leakage invariant (the critical one):** with cutoff N, every training event is
  `(year < eval_year) OR (year == eval_year AND round <= N)`; every eval event is `year == eval_year AND
  round in target_range`; NO training event has `year == eval_year AND round > N`. Read the test and the
  assembly code; confirm the test actually asserts this on an interior cutoff (not just N=last round).
- **Backward-looking confirmation:** independently READ `_build_recent_history_race_features`
  (`src/evo_predictor/module_adapters/_common.py` ~line 456) and `build_quali_pace_gap_history`
  (`src/evo_predictor/quali_pace_gap_history.py` ~line 78) and confirm they draw history from
  `range(1, round_num)` (strictly `< current round`). If either can reach `round >= current`, that is a
  leakage BLOCK. (This is the implementer's central claim — verify it yourself.)
- **As-of-N prior:** `run_season_alignment ... --through-round N` produces a prior whose
  `selected_source_races` are all `<= N`; a test asserts no round `> N` contributes. DB-only (no FastF1).
- **Gold defaults unchanged:** with the new params unset, train/eval partitioning is identical to before
  (eval_year fully held out). The gold-mode same-season compound guard is NOT loosened
  (`config.py` still forces `allow_same_season_compound_prior=false` in gold mode).
- **Tests genuine:** re-run `py -m pytest tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py -q` and
  confirm green; spot-check that assertions are substantive (would fail if the cutoff leaked).
- **simplification_limits** passes on touched paths.

## Allowed Scope
`module_training_orchestration.py`, `module_training_holdout_modes.py` (confirm this was necessary for
round_filter threading, not gold-default change), `scripts/run_season_alignment.py`,
`src/evo_predictor/gold_cycle/config.py`, new tests under `tests/unit/evo_predictor/walkforward/`,
+6 tests in `test_gold_cycle_config.py`.

## Specific Exclusions (BLOCK if touched)
- No walk-forward orchestrator / period logic / fantasy aggregation / attestation / run script.
- `src/fantasy_scoring/` untouched. Gold-mode leakage guards not loosened. No heavy training run.

## Constraints the Implementation Must Respect (each a check)
- As-of cutoff explicit/named; no silent fallback. DB-only. One canonical path (opt-in param, not a fork).
- New public params validated with clear messages.

## Evidence Produced
- `py -m pytest tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py -q` → 21 passed.
- `py -m pytest tests/unit/evo_predictor/test_data_adapter/test_multi_season.py tests/unit/evo_predictor/test_gold_cycle_config.py -q` → 99 passed.
- `py -m src.utils.simplification_limits --paths <6 files>` → PASS.

## Suggested Model Tier
`stronger` — independent leakage verification; read the form/label code yourself; high cost of a missed leak.

## Stop Conditions
BLOCK if: any training path can reach eval_year round `> N`; form/labels are not strictly backward-looking;
the as-of prior includes round `> N`; gold defaults changed; tests are hollow; excluded code touched.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
