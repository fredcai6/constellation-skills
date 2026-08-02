# Mission Frame — #644 physics-fit headless deadlock

Shrunk frame: this is a small, local, mechanical fix (one import-time environment-cap
guard + verification), not an architecture-touching change. Per commander-core.md §Mission
frame, the frame is shrunk accordingly rather than skipped outright, since the chosen seam
(`src/physics/__init__.py`) is a shared package entry every physics consumer imports and
deserves a named rationale.

## Intent
Make headless physics-fit entrypoints (currently deadlocking at ~0% CPU on Windows,
mirroring the already-fixed #623 sampler deadlock) complete, by capping native BLAS/OMP/torch
thread-pool init before it runs, the same way `src/evo_predictor/run.py` already does for the
sampler/predictor entrypoint.

## Affected capability
`src/physics/` (Physics region per `docs/agents/ORCHESTRATOR_CONTEXT.md` Architecture
Boundaries — `src/physics/`, `src/preprocessing/`). No evo or data-layer code touched.
`constraint:physics_region_no_evo_import` applies and is respected (the guard imports only
`os`/`logging`/optionally `torch`, same shape as the already-shipped `run.py` guard).

## Structural anchor
`src/physics/__init__.py` — the physics package's own `__init__`, unconditionally executed
before any `src.physics.<submodule>` import (Python parent-package-first import order).
Verified this covers the launch order's named entrypoints:
- `scripts/nuisance_sensitivity.py` → `from src.physics.longitudinal_fit import MASS_KG`
- `src/physics/session_fit.py` (`load_quali_session`) → `from src.physics.fit_store import
  FitRecord`
- `src/physics/layer2/estimate_store.py` and the rest of `layer2/*` → all `src.physics.*`
  submodules

## Governing constraint / precedent
`src/evo_predictor/run.py:26-38` is the shipped #623 fix and the pattern to mirror exactly:
`os.environ.setdefault` (respects an operator override) on the four thread-count env vars,
then a defensive `try: import torch; torch.set_num_threads(1); except Exception: ...`. No
other unconditional import-time guard exists; `src/utils/utilization.py:210-221` is a
parametrized per-worker setter for a different purpose (explicit worker-count scaling, hard
`os.environ[var]=` not `setdefault`) and is not reused here.

## Decision pressure
Where to put the guard: one shared seam vs. duplicated per-entrypoint patches. See
plan-alternatives below.

## Map confidence
High. Read `run.py` (existing fix) and `src/physics/__init__.py` (target seam) directly from
source; confirmed no `torch` import anywhere under `src/physics/`; confirmed the physics
architecture packet (`docs/architecture/packets/physics.md`) names no thread-cap precedent to
reconcile against, so the change is additive, not a rewrite of documented behavior.

## Out of scope
No estimator/fit-logic/smoother changes (Pre-Ruling 1). No production-default change beyond
the thread cap (Inherited Latitude boundary). No refactor of `run.py`'s existing guard into
the new shared location — `run.py` keeps its own copy; a "run.py should call the shared
physics guard too" consolidation is a nice-to-have named as a triage candidate, not done here.
