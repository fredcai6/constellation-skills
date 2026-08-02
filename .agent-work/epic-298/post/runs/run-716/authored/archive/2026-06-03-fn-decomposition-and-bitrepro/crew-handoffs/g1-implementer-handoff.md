# Implementer Handoff

## Gate
g1 — Decompose evo over-limit functions (behavior-preserving)

## Task
Split four pre-existing over-limit functions into focused helpers so strict
`py -m src.utils.simplification_limits --paths` passes on each file. PURE refactor — no behavior change.

Targets:
- `src/evo_predictor/run.py::_build_parser` (~201 lines) — e.g. extract a per-subcommand builder
  (`_add_<command>_parser(subparsers)`) for the larger argument groups.
- `src/evo_predictor/run.py::cmd_train_latent_power_module` (~124 lines) — extract cohesive steps
  (e.g. compound-prior/normalizer setup, data prep, training invocation, result assembly).
- `src/evo_predictor/gold_cycle/config.py::_parse_and_validate` (~142 lines) — extract per-section
  validators (e.g. `_validate_training_section`, `_validate_runtime_section`, ...).
- `src/evo_predictor/gold_cycle/runner_support.py::_gold_preflight_coverage` (CC=21, ~114 lines) — extract
  the per-year coverage computation / sub-steps to drop CC < 20 and lines < 100.

## Protected Intent
ZERO behavior change. Same CLI surface, same parsed args/defaults, same validation errors/messages, same
config parsing results, same preflight coverage output. Public signatures and caller contracts unchanged —
only internal structure changes.

## Test Mode
TDD-for-refactor: FIRST identify the existing tests covering each target function and confirm they're green
(your characterization baseline). If any function is thinly covered, add a characterization test BEFORE
refactoring it. Then refactor; keep green.

## Close Criteria
- All four functions decomposed; each resulting function < 100 lines and CC < 20.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/run.py src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner_support.py` → PASS (no violations on these files).
- Behavior preserved: the region tests covering these functions stay green; no signature/default/message change.
- New helpers are module-level, private (underscore-prefixed) where appropriate, and have clear names.

## Allowed Scope
- `src/evo_predictor/run.py`
- `src/evo_predictor/gold_cycle/config.py`
- `src/evo_predictor/gold_cycle/runner_support.py`
- Test files for characterization additions only (e.g. tests/unit/evo_predictor/test_gold_cycle_config.py,
  test_gold_cycle_runner.py, test_gold_module_cycle.py, and whatever covers the run.py CLI commands).

## Specific Exclusions
- Do NOT touch the two legacy mega-files (`_param_dataclasses.py`, `html_reports/__init__.py`) — out of scope.
- Do NOT change behavior, signatures, defaults, validation messages, or output.
- Do NOT touch the bit-reproducibility work (separate gates).

## Constraints
- Use `py`, not `python`.
- Pure helper extraction; reuse existing patterns in each file.
- No new mutable module-level state; logging via `logging.getLogger(__name__)` (print only in CLI/scripts).
- Identify and run the tests covering EACH function; report which tests cover `cmd_train_latent_power_module`
  and `_build_parser` specifically (these are the least-obvious; add a characterization test if coverage is thin).

## Required Evidence
- Baseline-green-before / green-after for each touched function's tests.
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py -q` → pass (tail), plus any CLI tests you identified for run.py.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/run.py src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner_support.py` → PASS (paste).

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py -q
py -m src.utils.simplification_limits --paths src/evo_predictor/run.py src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner_support.py
```

## Suggested Model Tier
simple bounded — mechanical helper extraction with strong test + `--paths` + review guardrails; the only care
needed is preserving every CLI arg/default and validation message during `_build_parser`/`cmd_train` extraction.

## Authority
Decided: pure decomposition, no behavior change, the 4 named functions only (exclude mega-files). You choose the
exact helper boundaries/names and any characterization tests.

## Stop Conditions
Stop and return if: a function cannot be brought under limits without a behavior/signature change; scope must be
exceeded; required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied (which tests cover each function;
baseline-then-refactor green), evidence (command tails incl. --paths PASS), assumptions, stop conditions hit,
out-of-scope observations.
