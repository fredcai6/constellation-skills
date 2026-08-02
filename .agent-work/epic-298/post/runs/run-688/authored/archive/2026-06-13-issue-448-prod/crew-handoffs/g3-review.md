# Reviewer Handoff

## Gate
g3 — review the bulldoze removal + schema retirement.

## Worktree
`C:/Programs/f1Brainz-worktrees/cmdr-448-prod` (branch issue-448-trajectory-estimator). Python `py`. The g3 removal
is committed (HEAD). Implementer result: `.agent-work/issue-448-prod/crew-handoffs/g3-implement-result.md`; removal
summary: `.agent-work/issue-448-prod/evidence/removal_summary.md`.

## What was implemented
Deletion of the dead windowed-estimator lineage + 7 orphaned preprocessing utils + the whole `trajectory_grading/`
subpackage + 12 dead tests + 9 orphaned scripts + 2 retired docs; `__init__.py` rewritten to the new trajectory API;
new `docs/report_schemas/trajectory_trust_profile.md` schema; dead doc-links fixed.

## Close Criteria (verify each; BLOCK on failure)
- `src/preprocessing/` contains ONLY `trajectory/` + `__init__.py` (`ls src/preprocessing/`). No legacy code.
- `py -c "import src.preprocessing; import src.preprocessing.trajectory; print('ok')"` succeeds.
- `py -m src.utils.simplification_limits --paths src/preprocessing` is clean.
- **Nothing outside the Admiral-ruled set was deleted.** Run `git diff --stat HEAD~1..HEAD` and confirm every
  deletion is one of: the named windowed lineage, the 7 orphaned utils (coordinate_transform, curvature,
  spline_basis, measurement_models, loess_bootstrap, robust_reweighter, irls_reweighter), the trajectory_grading/
  subpackage, the 12 dead tests, the 2 retired docs, or a script that imported a deleted module. For EACH deleted
  `scripts/*.py`, confirm via `git show HEAD~1:scripts/<name>.py | grep import` that it imported a removed module
  (windowed/trajectory_grading/etc.) — a script deleted that did NOT import a removed module would be a BLOCK
  (out-of-ruled-set). (Commander pre-checked all 9 import a removed module; re-confirm.)
- **Protected regions untouched:** `git diff --stat HEAD~1..HEAD -- src/physics src/evo_predictor src/latent_power`
  is EMPTY.
- **`docs/physics/measurement_model.md`:** the ONLY change allowed is fixing dead doc-links (the deleted
  windowed_estimator.md / trajectory_grading_report.md → the new trust_profile.md). Confirm the #447 Phase 0b
  obs-model CONTRACT content is otherwise unchanged (`git diff HEAD~1..HEAD -- docs/physics/measurement_model.md`).
- **Post-delete grep clean:** `grep -rn "windowed_estimator\|windowed_config\|windowed_solver\|trajectory_models\|
  consensus_stitcher\|coordinate_transform\|spline_basis\|measurement_models\|loess_bootstrap\|robust_reweighter\|
  irls_reweighter\|trajectory_grading" src tests --include=*.py` returns ONLY docstring/provenance comments (the two
  lines in trajectory/loaders.py documenting the salvage source), NO actual imports.
- **No dual estimator paths:** confirm `src/preprocessing` has a single estimation path (the trajectory module).
- **Fast suite green:** `py -m pytest tests/unit tests/integration -q -m "not slow" -p no:cacheprovider` passes
  with no collection/import errors (implementer reports 3465 passed).
- **New schema doc:** `docs/report_schemas/trajectory_trust_profile.md` exists and names a producer
  (trajectory/artifact.py + grading.py) and a consumer (the downstream artifact reader); the retired v1.0
  `trajectory_grading_report.md` and `docs/physics/windowed_estimator.md` are gone.

## Constraints
- Review only; report defects as BLOCK with file/line/fix. Do not modify code.
- The 9-script deletion is slightly broader than the handoff's 2 named examples — it is acceptable ONLY if each
  deleted script imported a removed module (so it would be broken dead code). Verify; if any did not, BLOCK.

## Map Anchors (inbound)
Inherits g3 anchors: struct:preprocessing legacy children removed; Admiral D1 (full orphaned-set removal) + D2
(retire committed grading schema); decision:#447 measurement_model.md doc stays; constraint: no parallel paths,
physics/evo/latent untouched.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-448-prod
ls src/preprocessing/
py -c "import src.preprocessing; import src.preprocessing.trajectory; print('ok')"
py -m src.utils.simplification_limits --paths src/preprocessing
git diff --stat HEAD~1..HEAD -- src/physics src/evo_predictor src/latent_power ; echo "(expect empty)"
git diff --stat HEAD~1..HEAD | grep "scripts/"   # then for each: git show HEAD~1:scripts/<f> | grep import
grep -rn "windowed_estimator\|windowed_solver\|trajectory_grading\|measurement_models\|loess_bootstrap\|consensus_stitcher" src tests --include=*.py ; echo "(expect only loaders.py provenance docstring)"
py -m pytest tests/unit tests/integration -q -m "not slow" -p no:cacheprovider
```

## Return Format
REVIEW_RESULT to `.agent-work/issue-448-prod/crew-handoffs/g3-review-result.md`, starting `VERDICT: APPROVE` or
`VERDICT: BLOCK`. Include the close-criteria checklist, the per-script import confirmation, any defects, out-of-scope
finds (e.g. the physics-characterization scripts that got orphaned — note them for triage), and workflow feedback.
