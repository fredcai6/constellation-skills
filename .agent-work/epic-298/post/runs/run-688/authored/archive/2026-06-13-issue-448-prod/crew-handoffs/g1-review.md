# Reviewer Handoff

## Gate
g1 — review the windowless trajectory module build.

## Worktree
`C:/Programs/f1Brainz-worktrees/cmdr-448-prod` (branch issue-448-trajectory-estimator). Python is `py`. The
g1 build is committed (HEAD). The implementer result is at
`.agent-work/issue-448-prod/crew-handoffs/g1-implement-result.md` — read it first.

## What was implemented
A new module `src/preprocessing/trajectory/` (dynamics.py, smoother.py, calibration.py, loaders.py, grading.py,
artifact.py, __init__.py) lifted+cleaned from the READ-ONLY lab worktree
`C:/Programs/f1Brainz-worktrees/expt-e12/scripts/experiments/` (e10/e11/e12/e10_fit/e4_fit/e4_lib/e4_run/e6_lib)
plus salvaged db_truth_loader/offline_loader. JointFusion went to `tests/oracles/joint_fusion_oracle.py`.

## Task statement (what good looks like)
A faithful, cruft-free port of the validated estimator with clean module boundaries, ready for the g2 test suite.

## How to inspect the diff
`git show --stat HEAD` then read the new files. Compare key functions against the lab originals (read-only) under
`C:/Programs/f1Brainz-worktrees/expt-e12/scripts/experiments/` to confirm the math was ported faithfully (not subtly altered).

## Close Criteria (verify each; BLOCK on any failure)
- `py -c "import src.preprocessing.trajectory as t; print('ok')"` succeeds.
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory` is clean.
- `grep -rn "evo_predictor\|latent_power\|src\.physics" src/preprocessing/trajectory` is EMPTY (no cross-region import).
- `grep -rn "fastf1\|enable_cache\|Cache\." src/preprocessing/trajectory` hits ONLY `loaders.py`.
- Lab cruft stripped: NO `EVID`, NO `os.makedirs(EVID`, NO `sys.path.insert`, NO experiment-only print/logging
  scaffolding, and the e6 cosine-stitch path (tile_windows/fit_chain/stitched_traj/pick_reference_lines/
  line_crossings/gated_crossings) is NOT present.
- Numerical-faithfulness spot-checks (the load-bearing invariants):
  - `matern52_sde` P_inf and `discretize` (Q = P_inf - Phi P_inf Phi^T) match the lab exactly.
  - StintSmoother keeps the diffuse-diagonal init (P[0,0]=P[3,3]=1e6, P[1,1]=P[4,4]=1e4, acc marginal from P_inf,
    NO pos-acc cross term at t=0), the per-axis linear detrend with velocity-trend add-back, and the affine-offset
    iterated-EKF speed update. Confirm NSStintSmoother with r==1 reduces to StintSmoother (implementer reports
    max_diff 1.07e-14 — re-run a quick check if you can).
- Named constants present: SIG_SPD=0.49, NOMINAL_OFFSET=0.09 (or similar), kernel orders documented.
- Salvaged loaders preserve the read-only DB pattern (`file:<path>?mode=ro` URI) and cache-only offline loading
  (raises if session not cached; no network fetch).
- Public functions validate meaningful inputs with messages naming field/expectation/actual (spot-check; note gaps).
- `fit_stint_hp` is present as a first-class public function in calibration.py (the production automatic calibration).

## Specific things to watch
- `session_offset` was adapted to use StintSmoother (not JointFusion, which is barred from src/). Confirm the
  objective is the same chi²-target spirit and that it does not import the oracle. (Functional correctness of the
  delta it returns is validated in g2, not here — here just confirm the adaptation is clean and boundary-safe.)
- The trust profile in grading.py must NOT be a pass/fail gate — it should return per-class held-out χ², NIS summary,
  and crossing residuals as a structured profile.

## Constraints
- Do NOT modify code (review only). If you find a defect, report it in REVIEW_RESULT as a BLOCK with the exact
  file/line and the fix needed.
- Do NOT modify the lab worktrees.

## Map Anchors (inbound)
Inherits g1-implement anchors: struct:preprocessing child; constraint:physics_region_no_evo_import; DB-only boundary;
Admiral D2 (salvage loaders) + D3 (automatic calibration); evidence: nesting + r==1 invariants.

## Required Evidence
The outputs of the verification greps/commands, your spot-check notes on numerical faithfulness, and a clear
APPROVE or BLOCK verdict with reasons.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-448-prod
py -c "import src.preprocessing.trajectory as t; print('import ok')"
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory
grep -rn "evo_predictor\|latent_power\|src\.physics" src/preprocessing/trajectory ; echo "(expect empty)"
grep -rn "fastf1\|enable_cache\|Cache\." src/preprocessing/trajectory ; echo "(expect only loaders.py)"
grep -rn "EVID\|os.makedirs\|sys.path.insert" src/preprocessing/trajectory ; echo "(expect empty)"
```

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), the close-criteria checklist with pass/fail per item, any
defects (file/line/fix), out-of-scope observations, and workflow feedback. Write it to
`.agent-work/issue-448-prod/crew-handoffs/g1-review-result.md`.
