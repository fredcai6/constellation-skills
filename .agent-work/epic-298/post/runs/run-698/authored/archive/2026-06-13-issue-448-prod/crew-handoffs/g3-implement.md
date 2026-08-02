# Implementer Handoff

## Gate
g3 — Bulldoze the dead pathways, retire the grading schema, reconcile docs (Admiral D1 + D2).

## Worktree
`C:/Programs/f1Brainz-worktrees/cmdr-448-prod` (branch issue-448-trajectory-estimator). Python `py`. The new
`src/preprocessing/trajectory/` module is built, tested, and the Spain R gate reproduced (HEAD). NOW remove the
old pathways so no parallel estimation paths remain.

## Authority (binding — Admiral-ruled, do not deviate)
- **D1**: remove the FULL orphaned set (bulldoze, no remnants): the named windowed lineage PLUS the now-orphaned
  legacy preprocessing utils, PLUS their now-dead tests.
- **D2**: retire the committed grading schema entirely. The db_truth_loader + offline_loader were ALREADY salvaged
  into `trajectory/loaders.py` in g1 — so delete `trajectory_grading/` in full now, and retire the v1.0 report
  contract; the new trust-profile schema replaces it.

## Import re-verification (DONE by the Commander at this gate — re-confirm, then delete)
Fresh grep confirms every external importer of each removal target is one of the DEAD TESTS listed below; no
production code imports any of them; `src/physics`, `src/latent_power`, `src/evo_predictor` import NOTHING from
`src/preprocessing`. RE-RUN the grep yourself before deleting (see Verification Commands) and confirm empty of
live (non-deleted-test) importers.

## DELETE — source (src/preprocessing/)
- `windowed_estimator.py`
- `windowed_config.py`
- `windowed_solver/` (whole directory: __init__, _core, _objective, _window_solve, _windows, manager)
- `trajectory_models.py`
- `consensus_stitcher.py`
- `coordinate_transform.py`
- `curvature.py`
- `spline_basis.py`
- `measurement_models.py`
- `loess_bootstrap.py`
- `robust_reweighter.py`
- `irls_reweighter.py`
- `trajectory_grading/` (whole directory: __init__, contract, covariance_gate, cross_residual, db_truth_loader,
  offline_loader, report_schema, runner, sector_anchor, strawman_candidate) — db_truth_loader + offline_loader
  already salvaged into trajectory/loaders.py, so this whole subpackage goes.

## DELETE — dead tests
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
(If `tests/unit/preprocessing/__init__.py` is now empty of other tests, leave it — the trajectory tests live under
`tests/unit/preprocessing/trajectory/`. Do not delete that package marker.)

## DELETE — docs
- `docs/physics/windowed_estimator.md`
- `docs/report_schemas/trajectory_grading_report.md` (the v1.0 committed contract — retired per D2)

## DELETE — orphaned scripts (if present)
- `scripts/test_windowed_estimator.py`, `scripts/diagnose_windowed_estimator.py` (and any other script importing
  the windowed lineage — grep `scripts/` and remove only those that import deleted modules).

## REWRITE
- `src/preprocessing/__init__.py` — currently re-exports ONLY the dead windowed/ribbon symbols. Rewrite it to
  export the new trajectory public API (re-export from `src.preprocessing.trajectory`, or simply make it a thin
  package marker that documents `trajectory/` as the sole content). It must import cleanly with all the old
  modules gone. Update the module docstring (no more "windowed trajectory fitting").

## WRITE — the new trust-profile schema doc
- `docs/report_schemas/trajectory_trust_profile.md` — the schema for the new on-disk trajectory-product artifact +
  trust profile (replaces the retired v1.0 contract). Document: the producer (`src/preprocessing/trajectory/
  artifact.py` writer + `grading.py` trust profile), the consumer (the downstream artifact reader — name the Phase 2
  / force-layer reader as the intended consumer, served by `artifact.py`'s reader), the fields (per-stint trajectory
  samples t/X/Y/V, acceleration state, position covariance, HPs, per-class held-out χ², NIS summary, sector-crossing
  residuals, schema version), and units (m, m/s, m/s², seconds). Match what `artifact.py` actually writes — read it.

## UPDATE — other doc references
- `docs/physics/overview.md` — remove/update any windowed-estimator references; point to the trajectory module.
- Grep `docs/` for `windowed_estimator`, `windowed_solver`, `trajectory_grading`, `consensus_stitcher`, etc. and
  fix or remove stale references (do NOT rewrite the architecture packet/index — Cartographer reconciles those at
  the next step; but fix obvious dead links in narrative docs you delete neighbors of).

## Specific Exclusions
- Do NOT touch `src/physics/*` (that is #449), `src/evo_predictor`, `src/latent_power`. Confirm via git diff that
  they are unchanged.
- Do NOT delete anything OUTSIDE the lists above. If a grep turns up an unexpected live importer of a removal
  target (i.e. NOT one of the listed dead tests), STOP and report it — do not delete it (that would be outside the
  Admiral-ruled set and must float).
- Do NOT touch `docs/physics/measurement_model.md` (the #447 Phase 0b obs-model contract doc STAYS — only the
  `measurement_models.py` CODE is deleted, not the doc).
- Do NOT edit the architecture packets/index (Cartographer's reconcile step).

## Close Criteria (prove each)
- `src/preprocessing/` contains ONLY `trajectory/` + `__init__.py` (no legacy preprocessing code). `ls` proves it.
- `py -c "import src.preprocessing; print('ok')"` succeeds (clean import with old modules gone).
- `py -c "import src.preprocessing.trajectory; print('ok')"` still succeeds.
- `py -m src.utils.simplification_limits --paths src/preprocessing` is clean.
- A full grep over `src/` and `tests/` shows NO remaining import of ANY deleted module
  (windowed_estimator/windowed_config/windowed_solver/trajectory_models/consensus_stitcher/coordinate_transform/
  curvature/spline_basis/measurement_models/loess_bootstrap/robust_reweighter/irls_reweighter/trajectory_grading).
- `git diff --stat` shows NO change under `src/physics/`, `src/evo_predictor/`, `src/latent_power/`.
- The fast test suite still collects + passes (no test references a deleted module):
  `py -m pytest tests/unit tests/integration -q --ignore=tests/integration/test_trajectory_spain_reproduction.py
   -p no:cacheprovider` — or at minimum `py -m pytest --co -q` collects with no import errors. (Use `-m "not slow"`
  if the project has a slow marker to skip the 13-min reproduction.)
- `docs/report_schemas/trajectory_trust_profile.md` exists with producer + consumer named; the retired v1.0 doc and
  `docs/physics/windowed_estimator.md` are gone.

## Constraints
- `py` never `python`; tests `py -m pytest`.
- Use `git rm` (or delete then `git add -A`) so deletions are staged.
- No dual estimator paths may remain in `src/preprocessing/`.

## Map Anchors (inbound)
- **Structural:** struct:preprocessing — legacy children deleted, only trajectory/ remains; docs/report_schemas/
  v1.0 retired, trust-profile added.
- **Decision:** Admiral D1 (full orphaned-set removal), D2 (retire committed grading schema); decision:#447
  measurement_model.md DOC stays (only .py deleted).
- **Constraint:** no parallel estimation paths; src/physics & src/latent_power untouched + import-clean.
- **Evidence:** removal leaves no live dependents (re-grep); import clean; simplification clean.

## Required Evidence
- The pre-delete re-grep output, the post-delete grep (empty), the `ls src/preprocessing/`, the import checks, the
  simplification_limits run, the `git diff --stat` proving physics/evo/latent untouched, and the test collection
  result. Write a removal-diff summary (files deleted + import-verification) to
  `.agent-work/issue-448-prod/evidence/removal_summary.md`.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-448-prod
# pre-delete re-verify (expect only dead-test importers):
grep -rn "windowed_estimator\|windowed_config\|windowed_solver\|trajectory_models\|consensus_stitcher\|coordinate_transform\|\bcurvature\b\|spline_basis\|measurement_models\|loess_bootstrap\|robust_reweighter\|irls_reweighter\|trajectory_grading" src tests --include=*.py | grep -v "src/preprocessing/trajectory/"
# ... do the deletions ...
ls src/preprocessing/
py -c "import src.preprocessing; import src.preprocessing.trajectory; print('import ok')"
py -m src.utils.simplification_limits --paths src/preprocessing
grep -rn "windowed_estimator\|windowed_config\|windowed_solver\|trajectory_models\|consensus_stitcher\|coordinate_transform\|spline_basis\|measurement_models\|loess_bootstrap\|robust_reweighter\|irls_reweighter\|trajectory_grading" src tests --include=*.py ; echo "(expect empty)"
git diff --stat -- src/physics src/evo_predictor src/latent_power ; echo "(expect empty)"
py -m pytest tests/unit tests/integration -q -m "not slow" -p no:cacheprovider
```

## Suggested Model Tier
Stronger — broad multi-file deletion with a hard "nothing outside the ruled set, nothing in physics" boundary and
a new schema doc to author.

## Authority
The removal set and schema retirement are Admiral-ruled — execute them exactly. The trust-profile schema doc
content/structure is yours (match artifact.py). If any importer outside the listed dead tests appears, STOP and report.

## Stop Conditions
Stop and return if: a removal target has a LIVE importer not in the dead-test list; deletion would require touching
src/physics/evo/latent_power; or the import/test checks cannot pass after removal (a real coupling you didn't expect).

## Return Format
IMPLEMENTER_RESULT to `.agent-work/issue-448-prod/crew-handoffs/g3-implement-result.md`: files deleted (by category),
the pre/post grep outputs, the import + simplification + test-collection results, the git diff --stat proving
physics/evo/latent untouched, the new schema doc path, blockers/stop-conditions, out-of-scope finds, workflow feedback.
