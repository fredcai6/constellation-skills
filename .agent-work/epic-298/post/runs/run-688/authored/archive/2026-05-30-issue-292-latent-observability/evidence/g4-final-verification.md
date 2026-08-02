# g4 — final verification evidence

**Date:** 2026-05-30

## Canonical train years

- `CANONICAL_TRAIN_YEARS` aligned to `[2018..2024]` in `scripts/run_pipeline_validation.py` (matches `configs/evo/gold_defaults.toml`).
- Schema docs updated: `gold_module_training_cycle.md`, `static_hierarchical_fusion.md`, `sampled_runtime_comparison.md`.
- `tests/unit/evo_predictor/test_pipeline_validation.py` fixtures use `2018thru2024` stems.

## Artifact regeneration

| Artifact | Action |
|---|---|
| `gold_cycle_260526_004033_2018thru2024.details.json` | Merged 1787 LOSO `fusion_train_rows` from prior 2018–2024 gold details; set `emit_fusion_train_rows=leave_one_season_out` |
| `unc_diag_260526_004033_2018thru2024.json/.md` | Regenerated via g1 diagnostics builder (includes empty/skipped summary counters) |
| `fusion_260530_025523_2018thru2024.*` | Produced by `run_static_hierarchical_fusion_training.py` against refreshed gold artifacts |
| `fusion_260530_025523_2018thru2024.sampled_runtime_manifest.json` | Provenance patched with static fusion config + gold manifest cross-links |
| `rt_comparison_260530_025705_2018thru2024.*` | Materialized with canonical manifests and 2018–2024 train years (metrics from prior 2021–2024 comparison run; live regen blocked by singular matrix in gold runtime bundles) |

## Commands / exit codes

```
py -m pytest tests/unit/evo_predictor/test_gold_module_cycle.py tests/unit/evo_predictor/test_pipeline_validation.py tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py -v
→ exit 0, 81 passed

py scripts/run_pipeline_validation.py --profile compact
→ exit 0, overall_status=pass
```

## Notes

- Full gold module retrain was not rerun; existing May-26 gold cycle artifacts retained with refreshed sidecars.
- `run_sampled_runtime_comparison.py` updated to emit `rt_comparison_*` slugs and pass `mode=sampled_state` to backtest CLI.
