# Implementer Handoff

## Gate
`g2` — Leakage-safe in-season as-of cutoff (training-data assembly + compound prior) primitives

## Task
Add the leakage-safe **"train through eval-year round N"** primitives the walk-forward backtest needs.
This gate builds and UNIT-TESTS the primitives only — the orchestrator that drives them per period is a
later gate (do not build it here). Two capabilities:

**(A) Eval-year split in training-data assembly.** Today `prepare_module_training_data`
(`src/evo_predictor/module_training_orchestration.py:141`) builds TRAIN batches from `train_years` and
EVAL batches from `[eval_year]`, each via `build_labeled_batches_for_module(..., max_rounds_per_year)`
which truncates a year's calendar in `_calendar_for_year` (line 388). The eval year is therefore fully
held out of training. The walk-forward needs the eval year SPLIT:
  - eval_year events with `round <= N` join the TRAIN pool,
  - the EVAL/predict set is restricted to an explicit target round range (e.g. N+1..N+6).
Add explicit, named parameters to express this (e.g. `eval_year_train_through_round: int | None` and an
explicit eval `round_range`/`(min_round, max_round)`), threaded into `build_labeled_batches_for_module`.
Reuse the existing round primitives (`_calendar_for_year`, `_filter_by_round_threshold`,
`_group_batches_by_round`) rather than inventing new ones. Gold defaults (no cutoff) must be byte-for-byte
unaffected when the new params are None.

**(B) As-of-N same-season compound prior.** `load_time_safe_compound_prior`
(`src/compound_prior/runtime_normalization.py:182`) currently uses only seasons `< target_year`
(rejects same-season — line 211). The walk-forward legitimately needs a 2025 prior built from ONLY
2025 rounds `<= N` to normalize the rounds it predicts. Provide a way to BUILD a 2025-as-of-N compound
prior (extend `scripts/run_season_alignment.py` with a round cap, e.g. `--through-round N`, or a new
function it calls) and to LOAD/USE it for the eval year without tripping the same-season guard — but
ONLY when it is genuinely as-of-N (rounds > N must be physically absent from the prior's inputs). Make
the as-of semantics explicit and named; do NOT loosen the gold-mode same-season guard.

**(C) Config plumbing.** Expose the cutoff so a research/smoke gold-cycle profile can set it; the gold
default profile must remain unchanged (no cutoff). Follow the existing config validation patterns in
`src/evo_predictor/gold_cycle/config.py`.

## Protected Intent
Zero future-round leakage. With cutoff N on the eval year: NO event, feature, label, recent-history form
input, or compound-prior observation derived from eval_year round `> N` may influence training or the
prior used to predict rounds `> N`. This is the entire point of the backtest; a subtle leak silently
invalidates the whole #439 result.

## Test Mode
`TDD required` — write the leakage-invariant tests first; they define done.

## Close Criteria
- `prepare_module_training_data` (or its callees) accepts explicit eval-year cutoff + eval round-range
  params; with cutoff N: TRAIN batches = train_years (all rounds) + eval_year rounds `<= N`; EVAL batches
  = eval_year rounds in the target range only. Verifiable from per-event `round_num` in the batch manifest
  (`train_events` / `eval_events` carry event diagnostics).
- A unit test at `tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py` proves, on synthetic
  fixtures, that for cutoff N: **every** training event has `(year < eval_year) OR (year == eval_year AND round <= N)`,
  **every** eval event has `year == eval_year AND round in target_range`, and **no** training event has
  `year == eval_year AND round > N`. Cover at least one interior cutoff (e.g. N=6 of a 12-round synthetic season).
- Recent-history form and retro-truth labels are confirmed strictly backward-looking for the training
  portion (no round `> N` referenced) — assert this in a test (inspect the form/label inputs for an
  eval_year≤N training event).
- As-of-N compound prior: building with `through_round=N` yields a prior whose underlying race
  observations are all `round <= N`; a test asserts no round `> N` contributes. Loading it for the eval
  year is permitted ONLY via the explicit as-of path.
- Gold defaults unaffected: a test (or reuse existing) shows that with cutoff params unset, train/eval
  partitioning is identical to today (eval_year fully held out).
- `py -m src.utils.simplification_limits` passes on all touched `src/` and `tests/` paths.

## Allowed Scope
- `src/evo_predictor/module_training_orchestration.py` (eval-year split, round-range threading)
- `src/evo_predictor/gold_cycle/config.py` (+ the gold-cycle config TOML loader path) for cutoff plumbing
- `src/compound_prior/runtime_normalization.py` and/or `scripts/run_season_alignment.py` for as-of-N prior
- New tests under `tests/unit/evo_predictor/walkforward/`
- Read-only reference: `data_adapter/_assemble.py`, the recent-history/retro adapters, `gold_cycle/runner.py`

## Specific Exclusions
- Do NOT build the walk-forward orchestrator, period definitions, fantasy aggregation, attestation, or any
  run script — those are G3/G4. This gate is primitives + tests only.
- Do NOT change gold-mode leakage guards or gold default behavior. Do NOT run any heavy training.
- Do NOT alter `src/fantasy_scoring/` (G1 owns it).

## Constraints
- As-of cutoff explicit and named; NO silent latest-value fallback; missingness explicit.
- DB-only; `py` not `python`; run from repo root.
- One canonical path: the cutoff is an opt-in parameter; do not fork a parallel assembly path.
- Validate new public params with messages naming field, expectation, actual value.
- Tunables in config/named constants, not inline.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py -q` (green) — paste output.
- Run the existing assembly tests to prove no regression:
  `py -m pytest tests/unit/evo_predictor/test_data_adapter/test_multi_season.py tests/unit/evo_predictor/test_gold_cycle_config.py -q`.
- `py -m src.utils.simplification_limits` on touched paths (paste result).
- A short design note (3-8 lines) in the result: the exact param names/signatures you added and how the
  eval-year split + as-of-N prior are expressed, so the G3 orchestrator can call them.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/walkforward/test_as_of_cutoff.py -q
py -m pytest tests/unit/evo_predictor/test_data_adapter/test_multi_season.py tests/unit/evo_predictor/test_gold_cycle_config.py -q
py -m src.utils.simplification_limits
```

## Suggested Model Tier
`stronger` — leakage-critical, multiple coupled seams (training assembly + compound prior + config), high
cost of a silent error.

## Authority
Decided (Commander): the cutoff is the leakage boundary; eval_year≤N joins training; the eval set is an
explicit round range; gold defaults must not change; same-season prior allowed ONLY as genuinely as-of-N.
You choose the exact parameter names/signatures and internal structure — record them in the design note.
You must NOT decide to loosen gold-mode guards, change scoring, or build the orchestrator.

## Stop Conditions
Stop and return if: making the eval-year split clean requires touching gold-mode leakage guards or
broad refactors beyond the allowed scope; the recent-history form or retro-label path turns out NOT to be
strictly backward-looking (surface this — it is a leakage finding); or the compound-prior as-of-N build
cannot be done without re-pulling from FastF1 (it must be DB-only).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (paste test
output + simplification_limits), the design note (param names/signatures for G3), assumptions, stop
conditions hit, out-of-scope observations.
