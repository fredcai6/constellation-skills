# Mission Frame: cmdr-461 — Trajectory Grading Hygiene

## Intent
Harden four small hygiene items deferred from the Phase 0a grading harness (#446). Two are doc/config
changes (items 1 and 4), one is honest-null (item 2), one is a code hardening (item 3). None block
physics work; all stay inside loaders/util/packaging territory.

## Affected Capabilities
- `struct:preprocessing` → `trajectory/loaders.py` — the sole FastF1 cache reader; docstring and
  version-guard hardening
- `pyproject.toml` — scipy dependency floor pin

## Structural Anchors
- `struct:preprocessing` path: `src/preprocessing/trajectory/`
- Sole FastF1 importer in the package: `loaders.py` (the boundary this work touches)
- `constraint:physics_region_no_evo_import` — preprocessing imports no evo-region packages

## Governing Constraints / Assumptions
- **Fence**: do NOT touch `smoother.py` (cmdr-504), `src/physics/*` (#525), `scripts/` (cmdr-476)
- Preprocessing packet boundary: FastF1 cache read ONLY in `loaders.py`
- Canonical data: no live FastF1/Jolpica calls from analysis code (version guard is on the OFFLINE loader)
- Unit convention: X/Y/Z pos_data in decimetres (×0.1 → metres); already in module docstring but
  missing Spa arc-length verification numbers

## Decision Anchors and Decision Pressure
- None. All four items are mechanical hygiene; no durable structural choices forced.

## Claims / Evidence Surfaces
- `lesson:fastf1-posdata-decimetres`: Spa 2023 Q VER arc 6941.6 m vs FastF1 Distance 6949.5 m,
  ratio 9.99 — ALREADY VERIFIED in issue-447; document at the seam, don't re-derive
- scipy 1.17.1 installed; floor in pyproject.toml is `>=1.9.0` — tighten to `>=1.17.1`
- fastf1 3.8.1 installed; `Cache.offline_mode()` is absent in 3.x (AttributeError catch is silent)

## Map Confidence / Staleness / Disputes
HIGH. Map reconciled through #522 (2026-06-26). The `struct:preprocessing` packet accurately
describes the post-#448 package. No stale or disputed areas in scope.

## Out of Scope
- `smoother.py`, `src/physics/*`, `scripts/`
- New shared GP-name normalizer (item 2 is honest-null — documented in triage)
- Any physics refit or trajectory recomputation
- FastF1 cache population or online session loading
