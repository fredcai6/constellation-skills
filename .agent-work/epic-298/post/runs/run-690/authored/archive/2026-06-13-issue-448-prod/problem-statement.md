# Problem statement — issue-448-prod (consolidated, map-first)

## The ask (binding, from rewritten #448 + launch order)
Productionize the ONE validated trajectory-estimation pathway from epic #445's lab (E1–E12) into a
tested `src/preprocessing/trajectory/` module, AND remove the dead windowed-estimator + ribbon-grading
pathways so no parallel estimation paths remain. Explicit REPLACEMENT directed by the user. Reproduce
the lab gate (≤50 ms held-out at real loops on 2022 Spain R) via a committed end-to-end check. Open PR,
do not merge.

## Map-first frame
- Region: **Physics** (`src/preprocessing/`, `src/physics/`). Container `struct:preprocessing`.
- Capability today: "windowed estimator and signal preprocessing for physics inputs" — this capability
  is being **replaced** by the windowless smoother. Container description + packet will change.
- Recent reconciliations in this area: #446 (`trajectory_grading/` harness + report schema v1.0),
  #447 (`docs/physics/measurement_model.md` Phase 0b contract). The new module builds directly on these.
- Constraint `constraint:physics_region_no_evo_import` applies — new module must not import evo region.
- Constraint: DB-only boundary — cache read ONLY on preprocessing/loader side; downstream reads the
  persisted trajectory artifact, never the cache.
- Edge `preprocessing→physics` evidence cites `windowed_estimator.py` (being deleted) + `measurement_models.py`.
  Edge evidence needs update at reconcile (measurement_models.py removal status TBD — see decisions).

## What I verified at context (grounded)
- The lab core (`e10_lib.StintSmoother`, `e11_lib.NSStintSmoother`, `e12_lib` loop co-est, `e4_lib.JointFusion`
  oracle, `e6_lib` DB plumbing) is read in the sibling expt-e12 worktree. Lab cruft to strip: hardcoded
  `EVID` worktree path + `os.makedirs(EVID)` (e10_lib L69-70), experiment-only logging.
- Reproduction target (lab evidence E12_VERDICT.md): **2022 Spain R pooled held-out median 20.4 ms / p90 59.2 ms**
  at E5-co-estimated real loops (≤50 ms gate). Quali sessions 47–49 ms (out of scope here — thin-n follow-up).
- Calibration soft-spot is REAL and grounded: per-driver HPs vary widely in the lab evidence
  (e12_2022_Spain_R.json: ell 0.8–5.625, sf 86–125, sig_pos 1.6–2.48, chosen per-stint by chi²-target).
  Production needs a robust automatic chi²-target routine OR a demonstrated generalizing fixed/light set.
- Removal import-verification (src/ + tests/): the entire legacy `src/preprocessing/` EXCEPT
  `trajectory_grading/` is consumed ONLY by the windowed lineage + `__init__.py` + windowed tests/scripts.
  `src/physics/` and `src/latent_power/` import NOTHING from `src/preprocessing` (confirmed empty grep).
  So removal is fully self-contained in the physics region — no live external dependents.

## DECISIONS surfaced to the human (genuine, govern structure/scope)

### D1 — Orphaned-util removal breadth (named list vs. full dead pathway)
The named removal list is: windowed_estimator.py, windowed_config.py, windowed_solver/*,
trajectory_models.py, consensus_stitcher.py, docs/physics/windowed_estimator.md, ribbon parts of
trajectory_grading/. BUT my import check shows that once the windowed lineage is deleted, these ALSO
become orphaned (imported only by the deleted code + their own tests):
  - loess_bootstrap.py, robust_reweighter.py, irls_reweighter.py (windowed Phase 1/4 reweighters)
  - spline_basis.py, curvature.py (imported only by windowed_solver/*)
  - coordinate_transform.py, measurement_models.py (imported only by __init__ + windowed lineage + own tests)
The launch order grants latitude to "remove now-orphaned ribbon-only shared utils that nothing else
imports" but ALSO says "removing anything OUTSIDE the named list FLOATS to the Admiral." These orphans
are outside the named list. **RECOMMENDATION: remove the full orphaned set** (leaves a clean
single-path `src/preprocessing/` = trajectory/ + trajectory_grading-survivors only; no dead utils).
Float to confirm before deleting beyond the named list. measurement_models.py is the one I'd flag for
extra care (it's a generic "Position/Speed observation model" that the new module's dynamics.py supersedes
conceptually but does not import — confirm it's not wanted as a salvage primitive).

### D2 — trajectory_grading/ salvage boundary (what survives into the new module)
Launch order: salvage only ribbon-free reused primitives (db_truth_loader, offline_loader) into the new
`loaders.py`; delete ribbon sector_anchor / strawman_candidate / pass-fail cross_residual / runner /
covariance_gate. The report_schema.py (GradingReport v1.0, a DURABLE committed contract per #446) and its
doc `docs/report_schemas/trajectory_grading_report.md` — the trust profile REPLACES the pass/fail framing,
so the new artifact schema is a NEW schema. **RECOMMENDATION: retire the whole trajectory_grading/ subpackage**
(salvage db_truth_loader + offline_loader into loaders.py; the sector_anchor co-estimation MATH is superseded
by e12_lib's loop co-estimation which goes into calibration.py). The GradingReport v1.0 schema doc gets
retired/replaced by the new trust-profile artifact schema. Confirm this retires a #446 committed contract
(producer+consumers+doc move together — all within this PR, no external consumer exists yet).

### D3 — Calibration generalization path (the first-class soft-spot deliverable)
Two acceptable paths per launch order: (a) robust automatic chi²-target routine, or (b) demonstrated
fixed/light set that generalizes. The lab evidence shows per-driver HPs vary too much for a single fixed
set to be obviously safe, so **RECOMMENDATION: ship the automatic chi²-target calibration routine as the
production path** (port the lab's held-out chi²-target fit, make it robust + bounded + deterministic), AND
document the generalization evidence by running it unattended across the Spain R drivers and reporting the
held-out reproduction. This is a build choice within my latitude (calibration approach is mine) — surfaced
for visibility, not a blocking decision unless the human prefers the fixed-set route.

## Out of scope (explicit)
- Validation breadth: wets, more circuits, pit/in-out-lap filtering, quali thin-n → follow-up triage.
- Any src/physics/* change (that is #449). Any src/evo|latent_power change.
- New estimation theory — if the lab result doesn't reproduce, STOP and return with evidence.
- Merging the PR (Admiral merges).
