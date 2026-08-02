# Reviewer Handoff

## Gate
g1 — Decompose evo over-limit functions (behavior-preserving)

## What Was Implemented
Four pre-existing over-limit functions decomposed into private helpers (no behavior change):
config.py::_parse_and_validate (→ 5 section validators), runner_support.py::_gold_preflight_coverage (→ 2 helpers),
run.py::_build_parser (→ 6 _add_*_parser helpers), run.py::cmd_train_latent_power_module (→ 4 helpers, incl.
promoting an inline closure to module-level). 127 tests pass; --paths PASS on the 3 files.

## How to Inspect the Diff
- `git diff -- src/evo_predictor/run.py src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner_support.py`
- For each target function, compare the new (driver + helpers) against the ORIGINAL: `git show HEAD:<file>`.
- `git status --porcelain` to confirm scope.
Implementer result: `.agent-work/fn-decomposition-and-bitrepro/crew-handoffs/g1-implementer-result.md`.

## Close Criteria (each a review check)
- All 4 functions decomposed; each resulting function < 100 lines and CC < 20.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/run.py src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner_support.py` → PASS (re-run).
- BEHAVIOR PRESERVED — verify by diffing each helper-set against the original body:
  - `_build_parser`: every subparser, argument, choices, default, `required`, `action`, `nargs`, and help is preserved
    (a dropped/renamed arg or changed default is a BLOCK).
  - `_parse_and_validate`: every validation branch + error MESSAGE preserved; returns the same GoldCycleConfig.
  - `_gold_preflight_coverage`: same per-year coverage dict + ordering + lap-schema logic.
  - **`cmd_train_latent_power_module` (SCRUTINIZE — its body is MOCKED in tests, so coverage is thin):** the
    extracted helpers must preserve EXACT logic and ORDER — compound-normalizer resolution + the requirement check,
    data prep, LatentPowerConfig construction, retro-join, training-diagnostics assembly, bundle write. Diff line-by-line.
- Region tests + run.py CLI tests green.

## Allowed Scope
run.py, gold_cycle/config.py, gold_cycle/runner_support.py, + characterization test additions.

## Specific Exclusions (flag if touched)
No mega-files; no behavior/signature/default/message/output change; no bit-repro work.

## Constraints (each a review check)
- Pure extraction; helpers module-level/private; no new mutable module-level state.
- Simplification (Commander standard): NO NEW violation; the target files must now PASS --paths (this gate's whole point).

## Evidence Produced
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py tests/unit/evo_predictor/test_run_cli_defaults.py -q` → 127 passed (re-run).
- `--paths` PASS on the 3 files (re-run).

## Suggested Model Tier
stronger — reason: behavior-equivalence of central CLI/config code by diff; the cmd_train body is thinly tested so
visual diff is the main guarantee there.

## Stop Conditions
Return BLOCK if: any arg/default/message/behavior changed, a target function is still over limits, the cmd_train
helper extraction altered logic/order, scope was exceeded, or tests/--paths fail.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (file:line + issue), out-of-scope observations.
