# Crew Handoff — G3 Implementer

## Role: implementer | Gate: G3 — Evo wiring + gold-cycle passthrough

## Task
Wire `lambda_sigma_nll` and `solve_sigma_floor` end-to-end on evo side.

1. **run.py** `cmd_train_latent_power_module`: pass `lambda_sigma_nll` and `solve_sigma_floor` into `LatentPowerConfig`. Add CLI args `--lambda-sigma-nll` (default 1.0) and `--solve-sigma-floor` (default 0.05).

2. **gold_cycle/config.py**: Remove the `lambda_sigma_nll != 0.0` rejection block. Keep validated float >= 0.

3. **gold_cycle/runner.py** `_module_train_args`: pass `lambda_sigma_nll` and `solve_sigma_floor` into train args namespace.

4. **Tests**: Replace `test_nonzero_lambda_sigma_nll_raises` with acceptance test. Update any gold tests that still assume bce target_mode or reject nonzero lambda.

## Exclusions
- No gold retrain (G5)
- No report schema changes (fields exist)

## Verification
```bash
py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_module_cycle.py -q
```

Commit: `feat(evo_predictor): wire lambda_sigma_nll gold passthrough (issue #142 g3)`

Return IMPLEMENTER_RESULT.
