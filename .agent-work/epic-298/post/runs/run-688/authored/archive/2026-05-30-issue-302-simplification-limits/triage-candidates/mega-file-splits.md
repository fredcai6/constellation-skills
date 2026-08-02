# Mega-file split backlog (issue #302)

Triage candidates for user-approved GitHub issues. In-PR splits: `race_report` package, `database` package.

## Evo region

| Path | Lines | Suggested split |
|------|------:|-----------------|
| `src/evo_predictor/models.py` | ~2816 | Feature dataclasses vs training payloads vs module bundles |
| `src/evo_predictor/data_adapter.py` | ~1765 | DB load vs feature assembly vs validation |
| `src/evo_predictor/fusion_training.py` | ~1670 | Training loop vs loss assembly vs checkpoint I/O |
| `src/evo_predictor/practice_preprocessor.py` | ~1654 | Session-type preprocessors per phase |
| `src/evo_predictor/module_adapters.py` | ~1396 | One module per adapter family |
| `src/evo_predictor/gold_cycle/runner.py` | ~1198 | Cycle orchestration vs per-stage runners |
| `tests/unit/evo_predictor/test_fusion_training.py` | ~1663 | Mirror `fusion_training` modules |
| `tests/unit/evo_predictor/test_data_adapter.py` | ~1011 | Mirror `data_adapter` modules |
| `tests/unit/evo_predictor/test_session_dropout.py` | ~1055 | Scenario fixtures vs test cases |

## Compound prior region

| Path | Lines | Suggested split |
|------|------:|-----------------|
| `src/compound_prior/diagnostics.py` | ~2723 | Plot/report builders vs metric calculators |
| `src/compound_prior/solver.py` | ~2342 | Fit kernels vs constraint solvers vs audit helpers |

## Physics region

| Path | Lines | Suggested split |
|------|------:|-----------------|
| `src/preprocessing/windowed_solver.py` | ~1283 | Solver core vs window scheduling vs I/O |

## Baseline allowlist

Paths above remain in `config/simplification_baseline.json` until their split issue closes and the entry is removed.
