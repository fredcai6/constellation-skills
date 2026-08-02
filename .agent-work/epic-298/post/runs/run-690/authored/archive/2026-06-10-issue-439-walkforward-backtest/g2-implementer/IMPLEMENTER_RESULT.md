# Implementation Result — Gate g2

## Assigned gate
`g2` — Leakage-safe in-season as-of cutoff primitives (training-data assembly + compound prior)

## Completed slice
Added the leakage-safe "train through eval-year round N" primitives the walk-forward
backtest needs (primitives + tests only; no orchestrator):
- **(A) Eval-year split** in training-data assembly: eval_year rounds `<= N` join the
  TRAIN pool; the EVAL set is an explicit round range.
- **(B) As-of-N compound prior build** path (DB-only round cap) + confirmed the existing
  explicit same-season LOAD path is the only same-season entry.
- **(C) Config plumbing** for the cutoff (gold default unchanged).

## Scope — files changed
- `src/evo_predictor/module_training_orchestration.py` — `round_filter` param on
  `build_labeled_batches_for_module`; `eval_year_train_through_round` + `eval_round_range`
  params on `prepare_module_training_data`; extracted `_finalize_prepared_module_data`.
- `src/evo_predictor/module_training_holdout_modes.py` — houses the new round primitives
  `RoundWindow`, `_validate_round_window`, `_resolve_eval_year_split` (co-located with the
  existing `_filter_by_round_threshold`/`_group_batches_by_round`).
- `scripts/run_season_alignment.py` — `through_round` param + `--through-round` CLI on
  `run_year` (DB-only enforced); pure `_extract_round_args`; extracted
  `_baseline_extracted_races`.
- `src/evo_predictor/gold_cycle/config.py` — optional `[data].eval_year_train_through_round`
  + `eval_round_range`; `_validate_in_season_cutoff`; round-trip + override wiring.
- `tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py` (NEW) + `__init__.py`.
- `tests/unit/evo_predictor/test_gold_cycle_config.py` — 6 cutoff config tests.

**Specific exclusions touched:** No. `src/fantasy_scoring/` untouched; no orchestrator,
period logic, aggregation, attestation, or run script built; no heavy training run.

## Behavior changed
Opt-in only. With all new params unset/None the assembly, the compound-prior build, and
the gold config are byte-for-byte unchanged (verified: held-out-eval-year tests + the
committed `gold_defaults.toml` cutoff-free test + 99 regression tests green).

## Test mode
**Required:** test-first (TDD). **Satisfied:** yes — wrote
`test_as_of_cutoff.py` first, observed RED (`unexpected keyword argument
'eval_year_train_through_round'` / `'round_filter'`, 11 failed/3 passed), implemented to
GREEN (21 passed), refactored while green (54 coupled tests still green).

## Evidence (real output)
```
py -m pytest tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py -q
  -> 21 passed
py -m pytest tests/unit/evo_predictor/test_data_adapter/test_multi_season.py \
             tests/unit/evo_predictor/test_gold_cycle_config.py -q
  -> 99 passed
py -m src.utils.simplification_limits --paths <6 touched files>
  -> PASS (6 files checked)
```
Bare `py -m src.utils.simplification_limits` (whole-repo strict) and `--baseline` surface
only PRE-EXISTING violations in other trees (`src/reporting/`, `src/strategy/`,
`models/_param_dataclasses.py`, etc.) — none in any file I touched (confirmed via git +
grep). The canonical per-change gate (`--paths`) passes.

## Design note (for the G3 orchestrator)
- **Eval-year split:** `prepare_module_training_data(..., eval_year_train_through_round: int
  | None = None, eval_round_range: tuple[int,int] | None = None)`. Set together: eval_year
  rounds `1..N` join TRAIN (eval_year auto-appended to the train pool with a `(1,N)`
  window); EVAL = eval_year rounds in `eval_round_range` (inclusive). Validated:
  both-or-neither, cutoff `>= 1`, range well-formed, range start `>` cutoff, eval_year not
  already in train_years. Underlying primitive: `build_labeled_batches_for_module(...,
  round_filter: Mapping[int, RoundWindow] | None)` where `RoundWindow = (min_round,
  max_round)` inclusive, 1-based; a sibling to `gp_name_filter`. Per-event `(year,
  round_num)` is in `batch_manifest["train_events"]` / `["eval_events"]`.
- **As-of-N prior build:** `run_season_alignment.run_year(year, *, skip_collection=True,
  through_round=N, db_path=...)` (or CLI `--through-round N --skip-collection`). Extracts
  only rounds `1..N` from the DB; the built prior's `selected_source_races` are all
  `<= N`. DB-only enforced (`through_round` without `skip_collection` raises).
- **As-of-N prior load:** use the EXISTING `load_time_safe_compound_prior(prior_root, *,
  target_year=eval_year, allow_same_season_research=True)` — already wired end-to-end via
  the gold-cycle `runtime.allow_same_season_compound_prior` flag (legal in research/smoke
  mode, forced false in gold). No new loader added (one-canonical-path). Point
  `compound_prior_root` at the as-of-N-built prior. The as-of guarantee is on the BUILD
  side; rounds `> N` are physically absent, so the load is genuinely as-of-N.
- **Config:** research/smoke profile sets `[data].eval_year_train_through_round` +
  `eval_round_range = [lo, hi]` (and `[runtime].allow_same_season_compound_prior = true`).

## Leakage finding (the protected intent)
Recent-history form AND retro/label inputs are **strictly backward-looking** —
`_build_recent_history_race_features` and `build_quali_pace_gap_history` both draw history
from `range(1, round_num)` (documented as-of guard); the label is the current round only.
Therefore restricting training events to round `<= N` is a *sufficient* leakage boundary:
a round-k (k<=N) training event cannot reach round `> N`. Asserted in the test.

## Assumptions
- Synthetic season modeled as 2024 (train) + 2025 (eval), real calendar GP names, capped to
  12 rounds via `max_rounds_per_year`; interior cutoff N=6, eval range (7,12). A
  recent-history *quali* module is used (needs only session classifications — no compound
  normalizer).
- The as-of build's testable invariant is `selected_source_races` round membership (the
  full solve is not unit-run; that is the heavy training the gate forbids).

## Stop conditions hit
None. No gold-mode guard touched; no broad refactor beyond extracting 2 helpers + relocating
round primitives to their natural sibling module for file-size hygiene; the as-of build is
DB-only.

## Out-of-scope observations (triage candidates for Commander)
- Pre-existing whole-repo simplification violations on this branch (e.g.
  `src/reporting/race_report/html_report.py`, `models/_param_dataclasses.py` 1122 lines,
  `reporting/html_reports/__init__.py` 1627 lines) — unrelated to #439; not in scope.

## Return status
`complete`
