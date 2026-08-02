# Problem Statement — #644 physics-fit headless deadlock

## Reconciled against the frozen launch order (delegated mode, no reachable human)

**Ask (Mission):** Live physics estimator fits (per-driver smoother-HP calibration; view
Jacobian re-fits invoked by `scripts/nuisance_sensitivity.py`, the per-session estimator,
etc.) deadlock at ~0% CPU when run headless, blocking automated physics fitting. Fix it so
headless physics fits complete.

## Baseline verified against actual code (not assumed)

- `src/evo_predictor/run.py:26-38` DOES carry the #623 thread-cap guard exactly as the
  launch order describes: `setdefault` on `OMP_NUM_THREADS` / `MKL_NUM_THREADS` /
  `OPENBLAS_NUM_THREADS` / `NUMEXPR_NUM_THREADS`, then an unconditional
  `torch.set_num_threads(1)` inside `try/except`, all before any project import that could
  transitively pull in torch. Confirmed by direct read of the file.
- `scripts/nuisance_sensitivity.py` (the named physics-fit entrypoint) imports
  `numpy`, then `from src.physics.longitudinal_fit import MASS_KG` and sibling
  `src.physics.layer2.*` view modules — **no thread-cap guard anywhere in the file**.
  Confirmed by direct read.
- `src/physics/session_fit.py` (`load_quali_session`, the per-session estimator seam named
  in the launch order's Data Locations) imports `numpy`/`pandas` and
  `src.physics.fit_store` / `src.physics.longitudinal_fit` — no thread-cap guard.
- No `src/physics/**` module imports `torch` (`grep -rl "import torch" src/physics` = empty).
  The only other unconditional thread-cap usage in the repo is
  `src/utils/utilization.py:210-221`, a **parametrized per-worker** setter (hard `os.environ[var]
  = value`, not `setdefault`, and a caller-supplied thread count) used for scaling parallel
  workers — a different purpose, not an import-time deadlock guard, and not reusable as-is.
- **Reconciled gap:** the order frames the risk as "torch's native thread-pool init is
  console-handle-dependent"; the physics-fit paths never import torch, so the deadlock
  mechanism there is the numpy/scipy (OpenBLAS/MKL) native thread-pool init instead — same
  Windows-headless console-handle class of bug, different library. The env-var caps
  (OMP/MKL/OPENBLAS/NUMEXPR) cover that regardless of torch's presence; the defensive
  `try: import torch; torch.set_num_threads(1)` stays harmless (no-op via `except Exception`)
  even though physics fits don't need it today, mirroring run.py for consistency (DRY,
  pre-ruling 1 — bounded fix only, no estimator/fit-logic changes).

## Chosen seam (shared guard, not per-entrypoint duplication)

`src/physics/__init__.py` is the physics package's own `__init__` and is transitively
imported by every physics-fit entrypoint the moment any `src.physics.*` submodule is
imported (Python always executes the parent package `__init__.py` first) — confirmed this
covers `scripts/nuisance_sensitivity.py` (`from src.physics.longitudinal_fit import
MASS_KG`), `src/physics/session_fit.py`'s own import of `src.physics.fit_store`, and
`src/physics/layer2/estimate_store.py`. Placing the guard at the very top of
`src/physics/__init__.py`, before its existing submodule imports (which pull in
numpy/pandas/scipy transitively), satisfies the launch order's "prefer a single shared
import-time guard in a low-level physics module that every fit path imports" instruction
without touching evo (`constraint:physics_region_no_evo_import` respected — the guard only
touches `os.environ` + an optional `torch` import, same as `run.py`, no evo import).

## Latitude check

Within Inherited Latitude: apply the cap, add the shared guard, verify, commit, open PR.
No structural/estimator refactor needed — this is a pure import-time environment-cap
addition, matching Pre-Ruling 1. No gap requiring escalation to the Admiral identified.

## Confirmation

Understand-step `user-decision` satisfied by citing LAUNCH_ORDER:Mission (this statement
reconciles the mission against verified current code, per commander-core.md "Reconcile the
order's assumed baseline against the actual code before planning").
