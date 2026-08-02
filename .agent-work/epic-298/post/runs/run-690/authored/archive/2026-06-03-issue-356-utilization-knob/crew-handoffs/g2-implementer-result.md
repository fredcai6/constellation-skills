# IMPLEMENTER_RESULT — g2 (gold config + CLI plumbing)

Status: complete. TDD red->green (8 new tests, 69 passed total).

## Files changed
- `src/evo_predictor/gold_cycle/config.py` — import UTILIZATION_LEVELS; `utilization: str = "balanced"` on
  GoldCycleRuntimeConfig; validate in _parse_and_validate (optional, default balanced, against UTILIZATION_LEVELS,
  GoldCycleConfigError naming field/expected/actual); emit in _config_to_raw; section_map utilization->runtime.
- `configs/evo/gold_defaults.toml` — `[runtime] utilization = "balanced"` (commented).
- `src/evo_predictor/run.py` — `_apply_utilization_hint(config, args)` helper called in cmd_gold_cycle AFTER the
  override path and OUTSIDE apply_cli_overrides; `--utilization {background,balanced,max}` (default None) on gold-cycle subparser.
- `tests/unit/evo_predictor/test_gold_cycle_config.py` — 8 new tests.

## Test mode: TDD satisfied
- RED: 8 failed (AttributeError: no 'utilization'; ImportError: _apply_utilization_hint).
- GREEN: 69 passed in 0.31s.
- Key test: --utilization max in gold mode does not raise and applied_overrides stays {} (PASSED).

## Evidence
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py -q` -> 69 passed.

## Simplification — Commander adjudication
- `--paths src/evo_predictor/gold_cycle/config.py src/evo_predictor/run.py` -> FAIL (3 violations), ALL PRE-EXISTING:
  - config.py _parse_and_validate function_lines=142 (was 134 pre-G2; G2 added validation block)
  - run.py _build_parser function_lines=201 (was 195 pre-G2; G2 added --utilization)
  - run.py cmd_train_latent_power_module function_lines=124 (UNCHANGED by G2 — G2 edits cmd_gold_cycle, not cmd_train; proves pre-existing)
- `--baseline` (canonical CI gate) -> FAIL (2 violations) on UNRELATED legacy mega-files
  (_param_dataclasses.py 1122, html_reports/__init__.py 1627) that G2 never touched. The repo baseline is
  already red on main from legacy debt.
- STANDARD APPLIED (Commander): "G2 introduced NO new simplification violation" (no new file>1000, function>100,
  or CC>20). The 3 strict failures are pre-existing (git-stash confirmed by implementer; cmd_train untouched).
  Pre-existing config.py/run.py function-length debt -> triage candidate tc-simplification-evo-cli.
- Decision: do NOT scope-creep G2 into refactoring pre-existing 142/201-line functions (contradicts
  "touch only what you must"; those functions need a planned split, triaged).

## Assumptions
- smoke_defaults.toml lacks utilization; optional-with-default("balanced") handles it cleanly.

## Out-of-scope observations
- Pre-existing simplification debt in config.py (_parse_and_validate) and run.py (_build_parser,
  cmd_train_latent_power_module) -> triage candidate. (Implementer also spawned a harness chip.)
