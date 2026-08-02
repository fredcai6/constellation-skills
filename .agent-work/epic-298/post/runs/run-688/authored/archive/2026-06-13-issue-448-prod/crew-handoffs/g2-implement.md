# Implementer Handoff

## Gate
g2 — Test suite + committed end-to-end Spain R reproduction.

## Worktree
`C:/Programs/f1Brainz-worktrees/cmdr-448-prod` (branch issue-448-trajectory-estimator). Python is `py`, never
`python`. Tests via `py -m pytest`. The g1 module `src/preprocessing/trajectory/` is built and committed (HEAD).
The JointFusion test oracle is at `tests/oracles/joint_fusion_oracle.py`.

## Task
Write the test suite that proves the windowless trajectory estimator is correct and honest, AND a committed
end-to-end check that reproduces the lab's sector-gate result on 2022 Spain R using the PRODUCTION automatic
calibration. This is the gate that turns "lifted code" into "validated, reproduced estimator."

### Unit tests — `tests/unit/preprocessing/trajectory/` (fast; create `__init__.py` files as needed)
1. **Nesting oracle**: on a small span (synthetic or a short real slice), `StintSmoother` posterior pos/vel
   matches the dense-GP `JointFusion` (from `tests/oracles/joint_fusion_oracle.py`) to ~mm at the observation
   samples. The lab verified ~0.14 mm at-sample; assert a tolerance like ≤ a few mm. Use query nodes for any
   off-sample comparison (the smoother bridges them exactly).
2. **r==1 selftest**: `NSStintSmoother(..., lam==0 / r_drv all 1)` equals `StintSmoother` to ~1e-10 on the same fit.
3. **Synthetic gate**: generate a KNOWN analytic trajectory (e.g. a smooth parametric path with known speed),
   sample position+speed with known Gaussian noise, fit, and assert the recovered path is within tolerance AND
   the held-out per-class χ² (via `heldout_chi2_full` or the grading trust profile) is ≈ 1 (honest covariance).
4. **Honesty checks**: `nis_series` mean ≈ 1 on a well-specified synthetic fit; `pos_predvar`/`speed_predvar`
   are positive and finite; unit conversions correct (dm→m ×0.1, km/h→m/s ÷3.6 — test the loader conversion).
5. **Artifact round-trip**: write a trajectory product via `artifact.py`, read it back, assert all fields
   (trajectory samples, acceleration state, covariance, HPs, trust profile, schema version) are preserved.
6. **Trust profile shape**: `grading.py` returns a structured profile (per-class χ², NIS summary, crossing
   residuals), NOT a pass/fail boolean. Assert the shape.

### The committed end-to-end reproduction — `tests/integration/test_trajectory_spain_reproduction.py`
This is the load-bearing deliverable. Mark it as a slow/integration test (pytest marker or a module that the
fast suite excludes), and guard it to SKIP cleanly if the data is absent (so the fast suite stays green).
- Session: **2022 Spain R**. Data (absolute paths into the MAIN checkout, not the worktree):
  - Season DB: `C:/Programs/f1Brainz/data/f1_data_2022.db` (lap_times, sector times).
  - FastF1 cache: `C:/Programs/f1Brainz/outputs/cache` (offline; loaders.py enables it).
- Use the new module ONLY (`src.preprocessing.trajectory`), via `loaders.py` for the cache/DB reads.
- Inter-stream offset: the lab used delta = 0.06 for Spain R. You MAY pass delta=0.06 directly (the lab's
  KNOWN value) — the calibration under test here is the HP calibration (ell/sf/sig_pos), not delta. (If you
  instead call the module's `session_offset`, fine, but delta=0.06 is the validated value; don't let a delta
  re-fit be the thing that fails — the D3 deliverable is the HP calibration generalization.)
- For EACH driver with a usable green stint: pick the longest contiguous green stint (exclude in/out/pit laps,
  same heuristic as the lab `green_laps`/`longest_stint`), and fit the windowless `StintSmoother` over that whole
  stint using **`fit_stint_hp` AUTOMATIC calibration for EVERY driver** — do NOT use any hardcoded per-driver HP
  dict. Running `fit_stint_hp` unattended across all the Spain R drivers IS the Admiral-D3 generalization demo.
- Co-estimate the real sector loops (s1/s2/sf) at the official sector-boundary times (FastF1
  SectorNSessionTime), calibration-free (b=0), query the trajectory at each crossing, held-out A/B driver split
  (calibrate the loop line on driver-subset A, score crossing-TIME residuals on disjoint B and vice-versa), pool
  the held-out residuals with the robust inlier mask.
- **ASSERT: pooled held-out median ≤ 50 ms.** (Lab E10 reference: 20.21 ms, n≈509, p90 59.2 ms.) A reasonable
  reproduction lands tens of ms (≈15–30 ms median). Use the e12_run.py pipeline logic as your reference for the
  exact crossing/held-out/pooling mechanics (read it at the lab worktree — it is the validated runner; you are
  re-expressing it against the new module with automatic HPs for all drivers).
- Write the reproduced numbers (per-loop med/p90/n, pooled med/p90/n, the per-driver fitted HPs from
  `fit_stint_hp` showing they vary — the generalization evidence) to
  `.agent-work/issue-448-prod/evidence/spain_reproduction.json` AND a short `.md` summary.

## Honest-Null / STOP condition (critical)
If the automatic `fit_stint_hp` calibration does NOT reproduce ≤ 50 ms pooled held-out median across the Spain R
drivers, **STOP and report it in your IMPLEMENTER_RESULT as a BLOCKER** — do NOT fall back to hardcoded HPs, do NOT
loosen the assertion, do NOT invent new estimation theory. A non-reproduction is a float to the Admiral, and the
Commander will handle it. Report the actual number you got and the per-driver HPs.

## Close Criteria
- `py -m pytest tests/unit/preprocessing/trajectory -q` passes (fast unit tests green).
- The integration reproduction RAN and its evidence file exists with a pooled held-out median ≤ 50 ms (report the
  exact number). If it can't run for a data reason, say so explicitly; if it runs and FAILS the 50 ms gate, that is
  a BLOCKER to report (not a test you weaken).

## Allowed Scope
Create test files under `tests/unit/preprocessing/trajectory/` and `tests/integration/`, plus the evidence files
under `.agent-work/issue-448-prod/evidence/`. You MAY add small test fixtures/helpers under tests/. Do NOT modify
`src/preprocessing/trajectory/` source UNLESS you find a genuine port bug — if so, make the minimal fix and call it
out prominently in IMPLEMENTER_RESULT (the reviewer will scrutinize it).

## Specific Exclusions
- Do NOT use a hardcoded per-driver HP dictionary in the reproduction (automatic calibration only).
- Do NOT delete any old files (removal is g3).
- Do NOT touch src/physics, src/evo_predictor, src/latent_power.
- Do NOT modify the lab worktrees.

## Constraints
- `py` never `python`; tests `py -m pytest`. utf-8 child env when you capture subprocess output (set
  PYTHONUTF8/encoding so captured stdout doesn't crash on non-ASCII).
- DB read-only; cache offline. Reproduction is allowed to be slow (minutes) — run it in the FOREGROUND and report
  the real number; do NOT background it.
- numpy/scipy only.

## Map Anchors (inbound)
- **Capability:** windowless trajectory estimation honesty + sector-gate reproduction.
- **Constraint:** DB-only boundary; physics evidence bar (truth-anchored, units/bounds explicit).
- **Decision:** Admiral D3 — automatic calibration generalization demonstrated on the Spain R drivers.
- **Evidence to re-confirm:** nests JointFusion ~mm; r==1 NS==E10 1e-10; per-sample honest χ²≈1; 2022 Spain R
  pooled held-out median ≤ 50 ms (lab 20.21 ms).
- **Confidence flag:** calibration generalization is THE known soft spot — the automatic fit must reproduce
  unattended or it floats to the Admiral.

## Required Evidence
Test run outputs (unit + the integration reproduction), the `spain_reproduction.json`/`.md` with pooled median +
per-driver HPs (the generalization evidence), and a clear statement of the reproduced number vs the 50 ms gate.

## Verification Commands
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-448-prod
py -m pytest tests/unit/preprocessing/trajectory -q
py -m pytest tests/integration/test_trajectory_spain_reproduction.py -q -s   # slow; prints the reproduced number
```

## Suggested Model Tier
Stronger — numerical test design + a multi-driver held-out reproduction with a hard quantitative gate.

## Authority
Test design and fixtures are yours. The 50 ms gate, the automatic-calibration-only rule, and the STOP-on-non-repro
clause are ruled by the Admiral — do not relax them. delta=0.06 for Spain R is the validated lab value.

## Stop Conditions
Stop and return (as BLOCKER) if: the reproduction does not clear ≤ 50 ms with automatic calibration; the data is
missing; a port bug blocks the nesting/selftest and the fix is non-trivial; or you would have to violate an
exclusion.

## Return Format
IMPLEMENTER_RESULT to `.agent-work/issue-448-prod/crew-handoffs/g2-implement-result.md`: tests written, the unit
results, the REPRODUCED Spain R pooled held-out median (the number) vs 50 ms, the per-driver automatic HPs (showing
spread = generalization evidence), any source fix you made, blockers/stop-conditions, out-of-scope finds, workflow feedback.
