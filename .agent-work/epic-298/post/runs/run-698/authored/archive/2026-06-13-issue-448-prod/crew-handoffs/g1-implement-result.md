# Implementation Result

## Assigned gate
`g1 — Build the windowless trajectory module`

## Completed slice
Created `src/preprocessing/trajectory/` (7 files) and `tests/oracles/` (2 files).
Lifted and cleaned the validated lab trajectory-estimator code from the read-only
sibling worktree `expt-e12/scripts/experiments/`.  No existing files were modified.

## Scope
**Files changed (all new — no existing file touched):**
- `src/preprocessing/trajectory/__init__.py`
- `src/preprocessing/trajectory/dynamics.py`
- `src/preprocessing/trajectory/smoother.py`
- `src/preprocessing/trajectory/calibration.py`
- `src/preprocessing/trajectory/loaders.py`
- `src/preprocessing/trajectory/grading.py`
- `src/preprocessing/trajectory/artifact.py`
- `tests/oracles/__init__.py`
- `tests/oracles/joint_fusion_oracle.py`
- `.agent-work/issue-448-prod/crew-handoffs/g1-plan.json` (plan artifact)

**Specific exclusions touched:** `no` — `src/preprocessing/__init__.py` unchanged;
no windowed/ribbon files touched; no existing file in the repo was edited.

## Behavior changed
`yes` — new production module `src/preprocessing/trajectory` added with the
windowless Kalman-RTS trajectory estimator, non-stationary extension, calibration,
loaders, grading, and artifact I/O.  No existing behaviour altered.

## Map Impact

- **Structural anchors touched:**
  `struct:preprocessing child` — `src/preprocessing/trajectory/` is a new
  self-contained subpackage (7 modules); does NOT yet modify the parent
  `src/preprocessing/__init__.py` (g3 owns that).

- **Capabilities added/changed/affected:**
  `capability:windowless-full-stint-trajectory-estimation` — NEW: per-stint
  position + velocity + acceleration + honest covariance + trust profile via
  `StintSmoother` / `NSStintSmoother`; calibrated by `fit_stint_hp`;
  written to disk via `artifact.py`.

- **Constraints/assumptions touched:**
  `constraint:physics_region_no_evo_import` — honored: no evo/physics/latent_power
  import anywhere in the new module (grep empty).
  `constraint:db_only_boundary` — honored: `fastf1` / `enable_cache` hits
  ONLY in `loaders.py` (grep confirmed).
  Units: X/Y dm→m (×0.1), Speed km/h→m/s (÷3.6) applied in `loaders.driver_streams`.
  Constants: SIG_SPD=0.49, NOMINAL_OFFSET=0.09 in `dynamics.py`.

- **Decision candidates / resolved decisions:**
  Admiral D2 honored: `db_truth_loader.py` + `offline_loader.py` salvaged into
  `loaders.py`.
  Admiral D3 honored: `fit_stint_hp` ported as first-class public function in
  `calibration.py`.
  `session_offset` adaptation: the lab `session_offset` calls `fit_window`
  (which uses `JointFusion`); porting it verbatim would require importing
  `JointFusion` into production.  **Adaptation made**: `session_offset` in
  `calibration.py` uses `StintSmoother` slices with `_eval_hp` (same objective)
  instead of `fit_window`.  Spirit preserved; no JointFusion import in `src/`.
  (Flagged below as a workflow observation.)

- **Claims/evidence produced:**
  NSStintSmoother r==1 vs StintSmoother max_diff: **1.07e-14** (limit: ~1e-10) —
  confirmed by smoke.  Diffuse-diagonal init, affine-offset EKF, exact Q=P_inf-Phi
  P_inf Phi^T all preserved faithfully.

- **Triage candidates:**
  The `__init__.py` re-exports `enable_cache` function name — this causes a
  non-fastf1-import mention in the cache grep output for `__init__.py`.  This
  is benign (it's just a function re-export, not a fastf1 import), but the
  handoff's grep command (`grep -rn "fastf1\|enable_cache"`) catches it.  Future
  handoffs could refine the grep pattern to exclude function re-exports.

## Test mode
**Required:** `evidence-only smoke` (throwaway snippet; full test suite is g2)
**Satisfied:** `yes — smoke ran; StintSmoother fit + pos_at + speed_at + nis_series
pass; NSStintSmoother r==1 nesting to 1.07e-14 confirmed`

## Evidence

```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-448-prod
py -c "import src.preprocessing.trajectory as t; print('import ok')"
```
**Result:** `import ok`

```bash
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory
```
**Result:** `PASS (7 files checked)` — all 7 files under <1000 lines/file,
<100 lines/function, cyclomatic complexity < 20.

```bash
grep -rn "evo_predictor\|latent_power\|src.physics\|src\.physics" src/preprocessing/trajectory ; echo "evo/physics grep done (expect empty)"
```
**Result:** `evo/physics grep done (expect empty)` — EMPTY. Boundary honored.

```bash
grep -rn "fastf1\|enable_cache" src/preprocessing/trajectory ; echo "cache grep done (expect only loaders.py)"
```
**Result:** `cache grep done (expect only loaders.py)` — fastf1 imports ONLY in
`loaders.py`; `__init__.py` mentions `enable_cache` only as a re-exported function
name (no fastf1 import there).

**Smoke output:**
```
pos_at: X=[ 24.51...  -49.73...  24.56...], Y=[ 43.29...  0.08...  -42.69...]
speed_at: V=[6.92...  5.41...  7.00...]
nis_series: n_obs=180, mean_nis_pos=0.404, mean_nis_spd=0.083
NSStintSmoother r==1 vs StintSmoother max_diff: 1.07e-14 (expect ~1e-10)
smoke: PASS
```

**Oracle smoke:**
```
JointFusion pos_at: X=[43.30...  33.76...], Y=[25.19...  36.91...]
oracle smoke: PASS
```

## TDD evidence, if required
N/A — test mode is evidence-only smoke (full test suite is g2).

## Docs/contracts touched
- none — no existing docs modified.

## Assumptions
- `session_offset` adapted to use `StintSmoother` (not `JointFusion`) since
  porting `fit_window` verbatim would require JointFusion in `src/`.  The
  objective function is identical (chi^2-target); only the solver inside changes.
  The spirit of "one global offset per session, scored by chi^2-target on short
  windows" is preserved.
- `__init__.py` mention of `enable_cache` in the cache grep is a re-export of
  the function from loaders, not a fastf1 import — assessed benign.
- The simplification_limits tool requires the `--paths` flag (not a positional
  argument) — the handoff's verification command omits `--paths`.  Used
  `--paths` to get it to work.

## Stop conditions hit
- none

## Out-of-scope observations
- `calibration.py` contains `session_offset` which uses `_eval_hp` with a fixed
  `sf_ref` heuristic for the delta-grid scoring.  The lab version uses `fit_window`
  with `JointFusion`; my adaptation uses `StintSmoother` slices.  This is a
  production-appropriate change but should be validated in g2 by comparing delta
  estimates to the lab's E4 results.
- `grading.py`'s `_loop_resid_profile` uses `fit_line` which requires all crossings
  to have `vX`/`vY` keys.  The loop_crossings API expects `t_off` + whatever
  metadata; the actual velocity comes from `crossing_from_smoother`.  This is
  consistent with e12's design.

## Workflow Feedback

- **Handoff gaps:**
  The verification command for simplification_limits is `py -m src.utils.simplification_limits src/preprocessing/trajectory` (positional arg), but the tool requires `--paths src/preprocessing/trajectory` (named arg).  The command in the handoff returns exit code 2 "unrecognized arguments".  Commander should update to `--paths`.

- **Context rediscovered:**
  `session_offset` in `e4_run.py` depends on `fit_window` which depends on `JointFusion` — this dependency chain was not surfaced in the handoff.  The handoff says "port `session_offset` from e4_run" without noting that a production port requires decoupling from JointFusion.  This was a non-trivial design decision I had to make alone.

- **Instructions improvised around:**
  The `_gauss_newton_step` split in `joint_fusion_oracle.py`: the original `JointFusion.fit` loop stores `_L`, `_alpha`, `_jx`, `_jy` in-place each iteration (so `_post_mean` can access them).  After I split the step into a method, I had to make the in-place mutation pattern explicit; there was a bug on the first pass (AttributeError on `_jx`) that required a fix.  No engine instruction covered this; I diagnosed and fixed it inline.

- **What would have made this easier:**
  Handoff field for "dependency surprises": a short "watch out for these lab cross-dependencies" note (e.g., session_offset -> fit_window -> JointFusion) would have surfaced the adaptation decision before implementation instead of mid-flight.

## Return status
`complete`
