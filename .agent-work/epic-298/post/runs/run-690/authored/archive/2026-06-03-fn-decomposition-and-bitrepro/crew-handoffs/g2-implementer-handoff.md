# Implementer Handoff

## Gate
g2 — Decompose run_comparison (behavior-preserving)

## Task
Split `scripts/run_sampled_runtime_comparison.py::run_comparison` (~134 lines) into focused helpers so strict
`py -m src.utils.simplification_limits --paths scripts/run_sampled_runtime_comparison.py` passes. PURE refactor.

## Protected Intent
ZERO behavior change: same manifest-resolution + ManifestResolutionError path, same default+trained backtest
fan-out (the G5 run_jobs path), same `_metric_deltas`, same run_config / summary / details / markdown artifacts,
same output filenames and EXIT behavior. Public signature `run_comparison(args) -> dict[str, Path]` unchanged.

## Test Mode
TDD-for-refactor: confirm the existing rt-comparison tests are green (baseline), add a characterization test only
if a behavior path is uncovered, then refactor and keep green.

## Close Criteria
- `run_comparison` decomposed; it and every new helper < 100 lines and CC < 20.
- `--paths scripts/run_sampled_runtime_comparison.py` → PASS.
- Behavior preserved: rt-comparison tests stay green; artifacts/filenames/return value/exit behavior unchanged.
- Suggested seams (you choose): manifest-resolution+failure-write block; the run_config dict assembly; the
  summary/details/markdown payload assembly; the artifact-writing block. Extract cohesive pieces as private helpers.

## Allowed Scope
- `scripts/run_sampled_runtime_comparison.py`
- `tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py` /
  `test_sampled_runtime_comparison_reporting.py` / `test_sampled_runtime_comparison_parallel.py` (characterization only).

## Specific Exclusions
- No behavior/output/filename/exit change. No touching the gold cycle, the other decomposition targets (G1), or bit-repro work.

## Constraints
- Use `py`, not `python`. print() acceptable in this CLI script.
- Pure helper extraction; helpers module-level/private; no new mutable module-level state.
- Run `py -m src.utils.simplification_limits --paths scripts/run_sampled_runtime_comparison.py`.

## Required Evidence
- Baseline-green-before / green-after.
- `py -m pytest tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py tests/unit/evo_predictor/test_sampled_runtime_comparison_reporting.py tests/unit/evo_predictor/test_sampled_runtime_comparison_parallel.py -q` → pass (tail).
- `py -m src.utils.simplification_limits --paths scripts/run_sampled_runtime_comparison.py` → PASS (paste).

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py tests/unit/evo_predictor/test_sampled_runtime_comparison_reporting.py tests/unit/evo_predictor/test_sampled_runtime_comparison_parallel.py -q
py -m src.utils.simplification_limits --paths scripts/run_sampled_runtime_comparison.py
```

## Suggested Model Tier
simple bounded — single-function mechanical extraction with test + `--paths` + review guardrails.

## Authority
Decided: pure decomposition, no behavior change. You choose helper boundaries/names.

## Stop Conditions
Stop and return if: cannot get under limits without behavior change; scope must be exceeded; evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (command tails incl. --paths PASS),
assumptions, stop conditions hit, out-of-scope observations.
