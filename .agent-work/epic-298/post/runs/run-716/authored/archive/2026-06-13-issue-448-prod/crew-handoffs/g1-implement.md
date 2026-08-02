# Implementer Handoff

## Gate
g1 — Build the windowless trajectory module.

## Worktree (cd here, stay here; ALL paths below are relative to this unless absolute)
`C:/Programs/f1Brainz-worktrees/cmdr-448-prod` — branch `issue-448-trajectory-estimator`.

## Task
Create `src/preprocessing/trajectory/` by **lifting + cleaning** the validated lab libraries from the
READ-ONLY sibling worktree `C:/Programs/f1Brainz-worktrees/expt-e12/scripts/experiments/`. You are
productionizing a single validated estimator (epic #445 lab ladder E1–E12). Port the math FAITHFULLY
(it is numerically validated), strip experiment cruft, give it clean module boundaries and input validation.
**Do NOT delete any existing files** — removal of the old pathways is a separate later gate.

## Source files to lift from (read-only; never modify the expt-e12 worktree)
- `e10_lib.py` — `matern52_sde`, `discretize`, `_block6`, `StintSmoother` (the windowless Kalman-RTS core),
  `banded_gap`. THE PRODUCTION CORE.
- `e11_lib.py` — `NSStintSmoother(StintSmoother)`, `build_roughness`, `driver_series` (state-dependent roughness).
- `e12_lib.py` — `fit_line`, `time_residuals`, `line_distance`, `crossing_from_smoother`, `local_kappa_v2`,
  `resid_stats` (sector-loop geometry co-estimation; loops calibration-free, b=0).
- `e10_fit.py` — `fit_stint_hp` (AUTOMATIC chi²-target HP fit for the windowless smoother — the PRODUCTION
  calibration path), `heldout_chi2_full`.
- `e4_fit.py` — `interleaved`, and the chi²-target objective pattern (`fit_window` is the JointFusion version;
  `fit_stint_hp` is its windowless analogue — port the windowless one).
- `e4_lib.py` — `enable_cache`, `load_session`, `driver_streams`, `_dedup` (offline loaders); `JointFusion`,
  `_m52` (the dense-GP reference — TEST ORACLE ONLY).
- `e4_run.py` — `session_offset` (one global inter-stream offset per session).
- `e6_lib.py` — `db_path`, `session_id`, `db_lap_times`, `driver_num`, `stint_span` (DB truth + stint plumbing).
  **DO NOT port** `tile_windows`/`fit_chain`/`stitched_traj`/`pick_reference_lines`/`line_crossings`/`gated_crossings`
  (the OLD cosine-stitch path — superseded).
- `src/preprocessing/trajectory_grading/db_truth_loader.py` and `offline_loader.py` — SALVAGE these into `loaders.py`
  (they already honor the DB-only boundary: read-only DB via `file:<path>?mode=ro` URI; cache-only offline raw streams).

## Target module layout — `src/preprocessing/trajectory/`
1. `dynamics.py` — `matern52_sde`, `discretize`, `_block6`, and named constants: `SIG_SPD = 0.49` (m/s speed
   sensor noise), `NOMINAL_OFFSET = 0.09` (s inter-stream offset), Matérn-5/2 position substrate. Pull `_m52`
   here too (the smoother does not need it, but `matern52_sde` documents P_inf as the analytic Matérn-5/2 value;
   keep `_m52` available for dynamics/oracle — your call whether it lives here or with the oracle).
2. `smoother.py` — `StintSmoother` (the FULL e10_lib core: `_build_timeline`, `_precompute_steps`, `_forward`
   iterated-EKF, `_backward` RTS, `fit`, `_state_at`, `_trend_pos`, `pos_at`/`vel_at`/`acc_at`/`speed_at`,
   `pos_predvar`/`speed_predvar`/`pos_cov2x2`, `nis_series`) + `NSStintSmoother`, `build_roughness`, `driver_series`
   from e11_lib. `banded_gap` can live here or in a small diagnostics helper.
3. `calibration.py` — `fit_stint_hp` (automatic chi²-target HP fit — PRODUCTION calibration), `interleaved`,
   `heldout_chi2_full`, `session_offset`, AND the loop geometry: `fit_line`, `time_residuals`, `line_distance`,
   `crossing_from_smoother`, `local_kappa_v2`, `resid_stats`.
4. `loaders.py` — salvaged `db_truth_loader` + `offline_loader` content (DB truth via `file:?mode=ro`; cache-only
   offline raw streams) PLUS `enable_cache`/`load_session`/`driver_streams`/`_dedup` from e4_lib, and the DB/stint
   plumbing from e6_lib (`db_path`, `session_id`, `db_lap_times`, `driver_num`, `stint_span`). **This is the ONLY
   module allowed to touch the FastF1 cache.**
5. `grading.py` — the TRUST PROFILE (replaces pass/fail gates): per-observation-class held-out χ² (via
   `heldout_chi2_full`), NIS summary (from `nis_series`), and sector-crossing residual at calibrated loops (the
   e12 held-out loop-residual logic). Returns a structured trust profile, NOT a pass/fail verdict.
6. `artifact.py` — on-disk trajectory-product artifact writer + reader (JSON): per-stint trajectory samples
   (t, X, Y, V), acceleration state, position covariance, HPs, and the trust profile. Downstream reads THIS, never
   the cache. Include a small schema version field.
7. `__init__.py` — export the clean public API (StintSmoother, NSStintSmoother, fit_stint_hp, session_offset,
   the loaders, grading entry point, artifact read/write). Do NOT re-export the old windowed/ribbon symbols.
8. TEST ORACLE: put `JointFusion` + `_m52` (dense-GP reference) in `tests/oracles/joint_fusion_oracle.py`
   (or a clearly-named `tests/` helper) — it is ONLY a nesting-equivalence oracle for tests, NOT production code.
   Do not import it from `src/`.

## Strip this lab cruft (do not carry it over)
- Hardcoded `EVID = "C:/.../expt-*/.agent-work/..."` paths and `os.makedirs(EVID, ...)`.
- Experiment-only logging / `print` scaffolding (keep a quiet optional `log` callback if a function already takes one).
- The e6 cosine-stitch / arbitrary-reference-line path (named above).
- `sys.path.insert(0, os.path.dirname(__file__))` hacks — use proper package-relative imports.

## Close Criteria (you must prove each)
- `py -c "import src.preprocessing.trajectory as t; print('ok')"` succeeds.
- `py -m src.utils.simplification_limits src/preprocessing/trajectory` is clean.
- No import of `src.evo_predictor`, `src.latent_power`, or `src.physics` anywhere in the new module
  (`grep -rn "evo_predictor\|latent_power\|src.physics\|src\.physics" src/preprocessing/trajectory` empty).
- No FastF1 cache read outside `loaders.py` (`grep -rn "fastf1\|enable_cache\|Cache\." src/preprocessing/trajectory`
  hits ONLY loaders.py).
- Public functions validate meaningful inputs with messages naming field/expectation/actual.
- A quick smoke: construct a `StintSmoother`, fit it on a tiny synthetic stint, query `pos_at`/`speed_at`/`nis_series`
  without error (a throwaway snippet is fine — the real tests are g2).

## Allowed Scope
Create files under `src/preprocessing/trajectory/` and the test-oracle file under `tests/`. You MAY add
`src/preprocessing/trajectory/__init__.py`. Do not modify `src/preprocessing/__init__.py` yet (g3 rewrites it;
the new subpackage importing cleanly on its own is enough).

## Specific Exclusions
- Do NOT delete or edit any windowed/ribbon files, or the existing `src/preprocessing/__init__.py` (g3 owns removal).
- Do NOT port the e6 cosine-stitch path.
- Do NOT write the full test suite (that is g2) — only a throwaway smoke to prove the module runs.
- Do NOT touch `src/physics/*`, `src/evo_predictor`, `src/latent_power`.

## Constraints
- Python is `py`, never `python`. Tests via `py -m pytest`.
- DB-only boundary: FastF1 cache read ONLY in `loaders.py`; downstream reads the artifact.
- Units/bounds explicit: X/Y decimetres→metres (×0.1), Speed km/h→m/s (÷3.6), σ_spd = 0.49 m/s, offset nominal +0.09 s.
- numpy/scipy only in the math. No new heavy deps.
- Lab worktrees are READ-ONLY reference.

## Map Anchors (inbound)
- **Structural:** `src/preprocessing/trajectory/` (NEW), struct:preprocessing child, physics region.
- **Capability:** windowless full-stint trajectory estimation (pos+vel+acc + honest covariance + trust profile).
- **Constraints:** `constraint:physics_region_no_evo_import`; DB-only boundary (cache only in loaders).
- **Decision anchors:** Admiral D2 (salvage db_truth_loader+offline_loader into loaders.py); Admiral D3 (automatic
  chi²-target calibration `fit_stint_hp` is the production path — port it as a first-class function).
- **Evidence expectations:** the SDE smoother must (g2) nest JointFusion to ~mm and r==1 NS must equal E10 to ~1e-10
  — so keep the oracle faithful and keep NSStintSmoother's r==1 path exactly reducing to StintSmoother.

## Required Evidence
- Output of the import smoke, the simplification_limits run, and the three boundary greps (evo/physics, cache).
- The throwaway smoke snippet's output (fit + query succeeds).
- List of files created and which lab source each maps to.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-448-prod
py -c "import src.preprocessing.trajectory as t; print('import ok')"
py -m src.utils.simplification_limits src/preprocessing/trajectory
grep -rn "evo_predictor\|latent_power\|src.physics\|src\.physics" src/preprocessing/trajectory ; echo "evo/physics grep done (expect empty)"
grep -rn "fastf1\|enable_cache" src/preprocessing/trajectory ; echo "cache grep done (expect only loaders.py)"
```

## Suggested Model Tier
Stronger — large faithful port across 6 modules with numerical-correctness risk and boundary rules.

## Authority
Module structure, file split, input-validation style, and naming are YOURS. The removal set, schema retirement,
and calibration approach are already ruled by the Admiral (do not change them). Do not delete anything (g3).
Do not invent new estimation theory — port the validated math as-is.

## Stop Conditions
Stop and return if: the lab math cannot be ported faithfully without modifying the experiment worktrees; a boundary
rule (cache-only-in-loaders, no evo/physics import) cannot be met; you must touch an excluded file; or you discover
the lab code does not run at all (a reproduction failure is g2's concern, but a hard import/run failure here blocks).

## Return Format
Return IMPLEMENTER_RESULT: files created (mapped to lab sources), the verification command outputs, the smoke
result, any assumptions, stop conditions hit, out-of-scope observations, and workflow feedback.
