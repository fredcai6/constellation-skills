# G3 Removal Summary

**Date:** 2026-06-12  
**Gate:** g3 — bulldoze dead pathways, retire grading schema, reconcile docs  
**Branch:** issue-448-trajectory-estimator

---

## Files Deleted by Category

### src/preprocessing/ — Legacy Source (11 files + 2 subdirs = 27 files total)

**Top-level files (11):**
- `consensus_stitcher.py`
- `coordinate_transform.py`
- `curvature.py`
- `irls_reweighter.py`
- `loess_bootstrap.py`
- `measurement_models.py`
- `robust_reweighter.py`
- `spline_basis.py`
- `trajectory_models.py`
- `windowed_config.py`
- `windowed_estimator.py`

**windowed_solver/ (6 files):**
- `__init__.py`, `_core.py`, `_objective.py`, `_window_solve.py`, `_windows.py`, `manager.py`

**trajectory_grading/ (10 files):**
- `__init__.py`, `contract.py`, `covariance_gate.py`, `cross_residual.py`, `db_truth_loader.py`, `offline_loader.py`, `report_schema.py`, `runner.py`, `sector_anchor.py`, `strawman_candidate.py`

### Dead Tests (12 files)

- `tests/unit/test_consensus_stitcher.py`
- `tests/unit/test_loess_bootstrap.py`
- `tests/unit/test_measurement_models.py`
- `tests/unit/test_robust_reweighter.py`
- `tests/unit/test_trajectory_models.py`
- `tests/unit/test_windowed_config.py`
- `tests/unit/test_windowed_estimator.py`
- `tests/unit/test_windowed_solver.py`
- `tests/unit/preprocessing/test_trajectory_grading.py`
- `tests/integration/test_trajectory_grading_runner.py`
- `tests/integration/test_windowed_pipeline.py`
- `tests/integration/test_windowed_regression.py`

### Docs (2 files retired)

- `docs/physics/windowed_estimator.md`
- `docs/report_schemas/trajectory_grading_report.md`

### Orphaned Scripts (9 files)

- `scripts/characterize_telemetry_instruments.py`
- `scripts/characterize_timetag_jitter.py`
- `scripts/create_physics_regression_fixtures.py`
- `scripts/diagnose_windowed_estimator.py`
- `scripts/run_regression_matrix.py`
- `scripts/run_trajectory_grading_strawman.py`
- `scripts/run_windowed_preprocess.py`
- `scripts/run_windowed_regression.py`
- `scripts/test_windowed_estimator.py`

**Total deletions: 60 files | Net change: 57 files, 82 insertions, 14,514 deletions**

---

## Pre-Delete Import Verification

Command:
```
grep -rn "from src.preprocessing.windowed_estimator|...|from src.preprocessing.trajectory_grading" src tests --include=*.py | grep -v "src/preprocessing/" | grep -v <dead-test-list>
```

**Result: (empty)** — No live (non-dead-test) importers found outside `src/preprocessing/` itself and the listed dead test files. Safe to proceed.

---

## Post-Delete Grep

Command:
```
grep -rn "windowed_estimator|windowed_config|windowed_solver|...|trajectory_grading" src tests --include=*.py
```

**Result:** Only `src/preprocessing/trajectory/loaders.py` lines 8-9 matched — these are docstring provenance comments ("Salvaged from: src/preprocessing/trajectory_grading/..."), not imports. No live code imports any deleted module.

---

## Import Checks

```
py -c "import src.preprocessing; import src.preprocessing.trajectory; print('import ok')"
```
**Result: `import ok`**

---

## Simplification Limits

```
py -m src.utils.simplification_limits --paths src/preprocessing
```
**Result: `PASS (8 files checked)`**

---

## git diff --stat (physics/evo/latent untouched)

```
git diff --stat -- src/physics src/evo_predictor src/latent_power
```
**Result: (empty) — no changes to any protected region**

---

## Fast Test Suite

```
py -m pytest tests/unit tests/integration -q -m "not slow" -p no:cacheprovider --ignore=tests/integration/test_trajectory_spain_reproduction.py
```
**Result: 3465 passed, 35 skipped, 1 deselected, 2 xfailed in 261.48s**

---

## ls src/preprocessing/

```
__init__.py
__pycache__
trajectory
```

`src/preprocessing/` contains ONLY `trajectory/` + `__init__.py` (plus `__pycache__`).

---

## New Files Written

- `docs/report_schemas/trajectory_trust_profile.md` — new schema doc (schema v1)
- `src/preprocessing/__init__.py` — rewritten to export trajectory API only

## Docs Updated

- `docs/DOCUMENTATION.md` — replaced `windowed_estimator.md` row with `trajectory_trust_profile.md`
- `docs/physics/measurement_model.md` — Related docs footer updated (removed dead links)
- `docs/report_schemas/README.md` — added `trajectory_trust_profile.md` entry
