# g2 — committed artifact validation blocker evidence

**Date:** 2026-05-29  
**Command:** `py scripts/run_pipeline_validation.py --profile compact`  
**Exit:** 1 (expected; gates not weakened)

## g2 code scope (passes unit tests)

`py -m pytest tests/unit/evo_predictor/test_pipeline_validation.py -v` → **24 passed**

## Committed repo failures (out of g2 compact-validation scope)

| Failure | Owning artifact |
|---|---|
| `gold module uncertainty diagnostics summary is missing modules_with_empty_usable_event_set` | `reports/evo/unc_diag_260526_004033_2018thru2024.json` |
| `gold module uncertainty diagnostics summary is missing modules_with_fully_skipped_usable_event_set` | same |
| `gold details is missing fusion_train_rows or equivalent LOSO rows` | `reports/evo/gold_cycle_260526_004033_2018thru2024.details.json` |
| `train_years is [2018..2024], expected [2021..2024]` | gold summary/details, gold calibration, static fusion config |
| `sampled-runtime summary/details/markdown is missing` | no `rt_comparison_*.summary.json` in repo |
| `static fusion summary/details/manifest is missing` | stem `fusion_260525_125312_2018thru2024` siblings absent under `reports/evo/` |

## Resolution path (g4 / artifact refresh, not gate weakening)

1. Regenerate gold cycle + unc_diag after g1 summary counter additions.
2. Commit fusion/rt_comparison sibling artifacts or regenerate full gold pipeline.
3. Reconcile canonical train-year policy (2018–2024 vs 2021–2024) in artifact refresh or docs (g3).
