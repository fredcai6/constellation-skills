# G2 IMPLEMENTER_RESULT — complete (agent a1eb7bbd70f7552d1)

Leakage-safe in-season as-of cutoff PRIMITIVES + tests (no orchestrator). TDD red→green.

## Files
- src/evo_predictor/module_training_orchestration.py (eval-year split, round_filter)
- src/evo_predictor/module_training_holdout_modes.py
- scripts/run_season_alignment.py (--through-round N as-of prior build, DB-only)
- src/evo_predictor/gold_cycle/config.py (cutoff config plumbing)
- tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py (NEW) + __init__.py
- tests/unit/evo_predictor/test_gold_cycle_config.py (+6 cutoff tests)

## Evidence
- test_as_of_cutoff.py → 21 passed
- regression test_multi_season.py + test_gold_cycle_config.py → 99 passed
- simplification_limits --paths (6 touched files) → PASS
- (bare simplification surfaces only PRE-EXISTING violations in untouched trees — triage)

## DESIGN NOTE (signatures for G3)
- `prepare_module_training_data(..., eval_year_train_through_round: int|None=None, eval_round_range: tuple[int,int]|None=None)`
  - both-or-neither; cutoff>=1; range start STRICTLY > cutoff; eval_year not in train_years.
  - eval_year rounds 1..N auto-appended to TRAIN with (1,N) window; EVAL = eval_year rounds in eval_round_range (inclusive).
  - primitive: `build_labeled_batches_for_module(..., round_filter: Mapping[int, RoundWindow]|None)`, RoundWindow=(min,max) 1-based inclusive.
  - per-event (year, round_num) in batch_manifest["train_events"]/["eval_events"].
- As-of prior BUILD: `run_season_alignment.run_year(year, skip_collection=True, through_round=N, db_path=...)` / CLI `--through-round N --skip-collection`. selected_source_races all <= N. DB-only (through_round without skip_collection raises).
- As-of prior LOAD: existing `load_time_safe_compound_prior(..., target_year=eval_year, allow_same_season_research=True)` via `runtime.allow_same_season_compound_prior` (research/smoke only; forced false in gold). No new loader.
- Config: `[data].eval_year_train_through_round`, `[data].eval_round_range=[lo,hi]`, `[runtime].allow_same_season_compound_prior=true` (research/smoke).

## LEAKAGE FINDING (protected intent confirmed)
Recent-history form (`_common.py:456 _build_recent_history_race_features`) and quali-pace-gap history
(`quali_pace_gap_history.py:78`) both draw from `range(1, round_num)`; label = current round only. So
training-event restriction to round<=N is a SUFFICIENT leakage boundary. Asserted with interior cutoff N=6/12.

## Stop conditions: none.
