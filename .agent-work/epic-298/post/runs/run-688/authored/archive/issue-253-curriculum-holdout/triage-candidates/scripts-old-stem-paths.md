# Triage Candidate: Remaining old-convention paths in scripts

**Reason:** Scripts outside Gate 1 scope still contain hardcoded old-convention artifact path defaults — not a regression introduced by this branch, but will produce confusing errors after Gate 6 produces new-named artifacts.

**Files:**
- `scripts/run_residual_backtest.py` line 795 — `--manifest` default references `gold_module_training_cycle_2021-2022-2023-2024_eval_2025.sampled_runtime_manifest.json`
- `scripts/report_predictive_retro_alignment.py` line 71 — hardcoded path component `gold_module_training_cycle_2021-2022-2023-2024_eval_2025_full`
- `scripts/plot_predictive_vs_retro.py` — similar hardcoded path
- `scripts/export_pairwise_predictive_vs_retro.py` — similar hardcoded path
- `params/gold/runtime_bundles/gold_module_training_cycle_2021-2022-2023-2024_eval_2025/` directory — tracked with old-convention naming

**Recommended action:** Post-Gate 6, update these scripts to use glob discovery (same pattern as `run_pipeline_validation.py`) and `git mv` the runtime_bundles directory. Low urgency — scripts still work with explicit `--manifest` flags; defaults just need updating.

**Anchor:** Gate 1 reviewer finding  
**Status:** noted — route to issue after Gate 6
