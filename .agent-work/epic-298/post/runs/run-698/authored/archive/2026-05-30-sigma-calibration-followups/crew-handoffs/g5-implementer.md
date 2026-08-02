# Crew Handoff — G5 implementer

## Role: implementer | Gate: G5 (close #303-306)

## G5 settings (from G4 + user plan: always retrain)
- `student_t_nu`: 4.0
- `student_t_nu_sigma`: null (unset)
- `lambda_sigma_nll`: 1.0
- `solve_sigma_floor`: 0.05 (unchanged)
- Schema v5 already in branch

## Task
1. Confirm `configs/evo/gold_defaults.toml` has lambda_sigma_nll=1.0 (no student_t_nu_sigma key needed)
2. Run full gold cycle: `py -m src.evo_predictor gold-cycle --config configs/evo/gold_defaults.toml` (~56 min)
3. Brier-primary comparison vs baseline `gold_cycle_260530_042533_2018thru2024` — no regression
4. Race-start re-check for #306 verdict
5. Promote bundles to params/gold/runtime_bundles/, unc_cal, sampled manifest
6. Update ADR 0008 + latent_power packet for: target_mode removed, |r/sigma| instrumentation, student_t_nu_sigma knob, schema v5
7. Save evidence/g5-gold.md + g5-metrics-comparison.json

## Close criteria
- Full gold completes exit 0
- Metrics comparison captured (no regression)
- Artifacts promoted
- Docs updated
- `py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q` green

Do NOT commit until Pilot says so — but DO run the gold cycle and promotion.

Return IMPLEMENTER_RESULT with slug, comparison summary, promotion paths.
