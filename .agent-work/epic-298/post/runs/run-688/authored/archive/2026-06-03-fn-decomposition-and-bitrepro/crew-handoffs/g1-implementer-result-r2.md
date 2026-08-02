# IMPLEMENTER_RESULT — g1 rework (round 2): cmd_train order fix

Status: complete. Single precise fix + regression test.

## Fix
- run.py cmd_train_latent_power_module: removed the hoisted retro_root read + `--retro-root` check from before
  `_resolve_compound_normalizers`; re-placed it AFTER prepare_module_training_data. Call order now matches HEAD:
  1. _resolve_compound_normalizers (compound requirement fires here)
  2. _resolve_db_args
  3. prepare_module_training_data
  4. retro_root read + `--retro-root` required-check
- Confirmed via `git diff HEAD src/evo_predictor/run.py`: only the helper-extraction structure differs; the
  check/effect ORDER within cmd_train now matches HEAD.

## Regression test (closes the test-blindness)
- tests/unit/evo_predictor/test_run_cli_defaults.py::test_cmd_train_compound_prior_error_precedes_retro_root_error
  — compound-needing module (evidence_source=race_weekend) with both retro_root and compound_prior_root None;
  asserts the ValueError mentions "compound-prior-root", not "retro-root". RED before fix, GREEN after.

## Evidence
- `py -m pytest test_gold_cycle_config.py test_gold_cycle_runner.py test_gold_module_cycle.py test_run_cli_defaults.py -q` -> 128 passed.
- `py -m src.utils.simplification_limits --paths run.py config.py runner_support.py` -> PASS (3 files).

## Note
- `--retro-root` is required=True at the parser, so the divergence was only reachable by calling cmd_train
  directly / bypassing the parser; restoring exact HEAD order is still correct and now test-pinned.

## Scope
- run.py (order fix only) + test_run_cli_defaults.py (new test). config.py/runner_support.py/other helpers/mega-files/bit-repro untouched.
