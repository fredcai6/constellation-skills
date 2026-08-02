# Context read — issue-448-prod

## Baseline context loaded
- ORCHESTRATOR_CONTEXT.md, GLOSSARY.md, engine-config.json (rework_cap=3, replan=abort-and-reissue, checkpoints understand/plan/run.accept)
- LESSONS.md Active section (16 lessons) — key ones for this run:
  - py-launcher (py not python), shell-cwd-reset, engine-artifact-attest (attach not attest user-decision/review-result), compact-step-skip (skip /compact with reason), run-crew-cli-launcher-misfit (dispatch via Agent tool + record in crew-runs.json via run_crew pure fns), spine-lease-stale-long-crew (re-claim after >30min crew), worktree-untracked-data (absolute paths into main checkout for cache/DBs), dbmanager-not-readonly (file:?mode=ro for read-only), fastf1-posdata-decimetres (X/Y *0.1 for metres), subprocess-utf8-io.
- Architecture map read: struct:preprocessing (physics region) container; recent reconciliations #446 (trajectory_grading harness) and #447 (measurement_model.md Phase 0b). Constraint: physics_region_no_evo_import.

## Map-relevant facts
- struct:preprocessing description "Windowed estimator and signal preprocessing" — WILL change after removal (windowed estimator gone).
- preprocessing→physics edge evidence cites windowed_estimator.py + measurement_models.py — windowed_estimator.py removal needs edge-evidence update (measurement_models.py stays).
- docs/architecture/packets/preprocessing.md "Key Modules" section heavily describes windowed lineage — needs rewrite.

## Removal import-verification (DONE at context; gate will re-verify)
Named removal targets: windowed_estimator.py, windowed_config.py, windowed_solver/*, trajectory_models.py, consensus_stitcher.py, docs/physics/windowed_estimator.md, ribbon parts of trajectory_grading/.

Grep results (src/ + tests/):
- windowed_estimator/windowed_config/windowed_solver/trajectory_models/consensus_stitcher: matches ONLY within the removal targets themselves, their own tests, and __init__.py. No live external dependents.
- loess_bootstrap.py + robust_reweighter.py: imported ONLY by windowed lineage + own tests + __init__.py → ORPHANED after removal (windowed Phase 1/4 reweighters). Candidates for removal as now-orphaned shared utils.
- src/physics/ imports NOTHING from src/preprocessing (confirmed: grep `from src.preprocessing` empty). segment_classifier curvature/spline grep hits are generic words, not imports.
- src/latent_power/ imports NOTHING from src/preprocessing.
- scripts/test_windowed_estimator.py + scripts/diagnose_windowed_estimator.py reference windowed lineage — orphaned scripts (not map nodes).

## SURVIVORS (shared utils, not windowed-only)
- measurement_models.py (MeasurementModel/PositionMeasurement/SpeedMeasurement) — stays (referenced in tests, shared).
- coordinate_transform.py, curvature.py, spline_basis.py — need per-module import check at gate (may be windowed-only too; verify before deciding).
- irls_reweighter.py — present on disk but NOT in __init__; check usage.

## DB / data locations (absolute, into main checkout)
- FastF1 cache: C:/Programs/f1Brainz/outputs/cache
- Season DBs: C:/Programs/f1Brainz/data/f1_data_<year>.db (lap_times)
- Lab libs: C:/Programs/f1Brainz-worktrees/expt-e12/scripts/experiments/{e4,e6,e10,e11,e12}_lib.py
- Lab evidence: C:/Programs/f1Brainz-worktrees/expt-e12/.agent-work/expt-e12/evidence/
- Clean-race reproduction target: 2022 Spain R, ≤50 ms held-out median at real loops.

## Autonomy note
Launch order grants push/PR + the named deletions (overrides ORCHESTRATOR_CONTEXT "ask first" for push/delete). Merge stays with Admiral. Removing anything OUTSIDE named list, or any src/evo|latent_power|physics change, FLOATS to Admiral.
