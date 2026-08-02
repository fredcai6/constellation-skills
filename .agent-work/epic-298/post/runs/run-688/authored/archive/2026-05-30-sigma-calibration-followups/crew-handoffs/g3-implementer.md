# Crew Handoff — G3 implementer

## Role: implementer | Gate: G3 (#305)

## Task
Add `student_t_nu_sigma: float | None = None` to `LatentPowerConfig` (None or >2.0). Term B in `modules.loss_from_pairwise` uses `student_t_nu_sigma or student_t_nu`; term A unchanged. Wire: `run.py --student-t-nu-sigma`, gold_cycle config + runner passthrough. Tests: None = bit-identical to current; override affects only term B; reject nu<=2.

## Exclusions
No gold default change. No commit. No REPORT_SCHEMA bump. No loss math beyond nu routing for term B.

## Close criteria
```bash
py -m pytest tests/unit/latent_power/test_config.py tests/unit/latent_power/test_modules.py tests/unit/latent_power/test_losses.py tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py -q
```

Return IMPLEMENTER_RESULT with diff summary + pytest output.
