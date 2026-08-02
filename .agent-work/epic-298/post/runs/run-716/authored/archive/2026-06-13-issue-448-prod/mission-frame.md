# Mission Frame — issue-448-prod

Map-first frame for issue #448 (windowless joint-fusion trajectory estimator + removal of old pathways).
Built from the architecture map read at `context` (struct:preprocessing packet, recent reconciliations #446/#447).

## Intent
Replace the dead windowed/ribbon estimation capability in the physics region with ONE validated windowless
Matérn-5/2 SDE Kalman-RTS smoother, lifted+cleaned from the E1–E12 lab into a tested `src/preprocessing/trajectory/`
module (dynamics/smoother/calibration/loaders/grading + on-disk artifact + new trust-profile report schema),
and bulldoze the orphaned windowed lineage + ribbon-grading so no parallel estimation paths remain. Reproduce the
lab gate (2022 Spain R, ~20 ms pooled held-out median ≤50 ms) via a committed end-to-end check using the AUTOMATIC
chi²-target calibration as the production path.

## Affected Capabilities
- `capability: windowed estimator and signal preprocessing for physics inputs` (struct:preprocessing) — being
  REPLACED. Its description + packet change: windowless smoother in, windowed/ribbon out.
- New capability: windowless full-stint trajectory estimation (pos+vel+acc + honest covariance + trust profile),
  consumed downstream by Phase 2 / force-layer (#449) via the on-disk artifact, never the cache.

## Structural Anchors
- `struct:preprocessing` — `src/preprocessing/`, physics region container. New child `trajectory/`; legacy children deleted.
- `src/preprocessing/trajectory/` (NEW) — dynamics.py, smoother.py, calibration.py, loaders.py, grading.py, artifact.py.
- `docs/report_schemas/` — new trust-profile artifact schema doc; `trajectory_grading_report.md` v1.0 RETIRED.
- `docs/architecture/packets/preprocessing.md` + `docs/architecture/index.md` — Key Modules section rewritten at reconcile.
- `docs/physics/windowed_estimator.md`, `docs/physics/overview.md` (windowed refs) — deleted/updated.

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — new module must not import src/evo_predictor / src/latent_power.
- DB-only boundary — FastF1 cache read ONLY in loaders (preprocessing side); downstream reads the persisted artifact.
  (Salvaged db_truth_loader uses `file:?mode=ro` URI; offline_loader uses cache-only, raises if not cached — both
  already honor the boundary.)
- Do NOT touch `src/physics/*` (that is #449) or `src/evo_predictor`/`src/latent_power`. Verified: neither imports
  from src/preprocessing (clean grep), so removal is self-contained in the physics region.
- Physics evidence bar: truth-anchored, units/bounds/invariants explicit (X/Y dm→m ×0.1, Speed km/h→m/s, σ_spd=0.49,
  offset +0.09s nominal / 0.06 Spain). Report-schema change needs producer + committed consumer + schema doc together.

## Decision Anchors & Decision Pressure
- `decision:#446` — trajectory_grading harness + GradingReport v1.0 committed contract. RETIRED this run (Admiral D2).
- `decision:#447` — measurement_model.md Phase 0b contract (docs/physics/measurement_model.md). NOT deleted; edge
  evidence updated at reconcile (measurement_models.py the code IS deleted, but the doc contract for the obs model stays).
- Admiral D1 (RULED): remove full orphaned set — named windowed lineage + coordinate_transform, curvature, spline_basis,
  measurement_models, loess_bootstrap, robust_reweighter, irls_reweighter + their dead tests.
- Admiral D2 (RULED): retire the committed grading schema; salvage db_truth_loader+offline_loader → loaders.py.
- Admiral D3 (RULED): ship AUTOMATIC chi²-target calibration; demonstrate generalization across 2022 Spain R drivers.

## Claims / Evidence Surfaces
- `claim: SDE smoother nests the dense-GP JointFusion to ~mm` — verified-by a nesting-oracle test (e4_lib.JointFusion
  kept as TEST ORACLE ONLY). Gate g2 re-confirms.
- `claim: r==1 NS == stationary E10 exactly` — selftest to ~1e-10. Gate g2 re-confirms.
- `claim: per-sample honest (χ²≈1), speed-honest` — held-out per-class χ² check. Gate g2.
- `claim: clears the sector gate, 2022 Spain R ~20 ms pooled held-out ≤50 ms` — lab E10 = 20.21 ms (n=509,
  p90 59.2 ms), delta 0.06. Gate g2 reproduces via committed end-to-end check using AUTOMATIC calibration (no
  hardcoded KNOWN HPs — that IS the D3 generalization demonstration).
- `claim: removal leaves no live dependents` — re-grep verified at context: every external importer of each removed
  module is a test of that same module; src/physics & src/latent_power import nothing. Gate g3 re-verifies before delete.

## Map Confidence / Staleness / Disputes
- struct:preprocessing description is STALE the moment removal lands (windowed estimator gone). Handled: reconcile step
  rewrites the packet; not silently trusted.
- preprocessing→physics edge evidence cites windowed_estimator.py + measurement_models.py (both deleted). Handled at
  reconcile: edge re-evidenced (physics does not actually import preprocessing — the edge is conceptual/stale).

## Out of Scope
- Validation breadth: wets, more circuits, pit/in-out-lap filtering, quali thin-n (47–63 ms) → triage follow-up.
- Any src/physics/* change (#449); any src/evo_predictor/src/latent_power change.
- New estimation theory — if the lab result fails to reproduce in the lifted module, STOP and return with evidence.
- Merging the PR (Admiral merges). PR #468 / #468-competition branch (Admiral already closed PR #468).
