Sub-issue of Epic 2 #492 (physics — borrow strength across sessions). Surfaced by the 2026-06-19 cartographer pass (commit e1a371a) as an open structural question.

## What

`src/physics/session_fit.py::load_quali_session` imports `fastf1` directly and enables the offline cache (`fastf1.Cache.enable_cache(...)`, `fastf1.get_session(...)`). That makes it a **second FastF1-cache entry point in the physics region**, alongside `src/preprocessing/trajectory/loaders.py` — which the preprocessing packet still calls the package's "sole cache reader."

More broadly, `src/physics/` consumes the trajectory estimator by importing `preprocessing.trajectory.{loaders, calibration, physics_adapter}` **directly** (`session_fit.py`, `layer2/session_braking.py`, `layer2/session_coast.py`, `ribbon.py`, `diagnostics/smoother_validation.py`), rather than reading the on-disk `trajectory/artifact.py` the #448/#449 design intended. The artifact indirection exists but is not on the consumed path.

## Why it matters

- Two places touch the FastF1 cache → two things to migrate when #494 (telemetry → SQLite) lands; easy to migrate one and miss the other.
- Loading/calibration responsibility is duplicated across the region boundary instead of being owned once by preprocessing.
- The intended single boundary (`trajectory/artifact.py`, or at least `preprocessing.trajectory.loaders`) is bypassed, so the trust-profile/artifact contract is not actually exercised on the path physics uses.

## Proposed cleanup

- Route physics session/telemetry loading through a single seam: consume the on-disk trajectory artifact (`trajectory/artifact.py`) where a precomputed trajectory exists, or call `preprocessing.trajectory.loaders` for the raw streams — but do **not** import `fastf1` from `src/physics/`.
- Remove the direct `fastf1` import + `Cache.enable_cache` from `session_fit.py`; let preprocessing own the one cache entry point.
- Restore the preprocessing packet's "sole cache reader" claim once it is true again.

## Relationship to neighbours (coordinate, don't duplicate)

- **#494** (persist telemetry to SQLite) changes *where* telemetry comes from (cache → DB) and also plans to migrate `load_quali_session`. This issue is about *who* loads it / the boundary. The `load_quali_session` change should land once — sequence the boundary consolidation (here) and the source swap (#494) so they don't fight.
- **#476** (re-home orphaned physics-characterization scripts to the trajectory API) is the same "single trajectory API" theme, for scripts.

## Refs

- `src/physics/session_fit.py` (the direct `fastf1` import), `src/preprocessing/trajectory/loaders.py`, `src/preprocessing/trajectory/artifact.py`
- `docs/architecture/packets/physics.md` (Open Questions), `docs/architecture/index.md` (Open Structural Questions: "Physics trajectory artifact-boundary bypass")
- Cartographer reconcile: commit e1a371a
