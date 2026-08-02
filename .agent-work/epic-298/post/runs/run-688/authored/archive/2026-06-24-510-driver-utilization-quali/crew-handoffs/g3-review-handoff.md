# Reviewer Handoff

## Gate
g3-review (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## What Was Implemented
The C1 characterization gate: a canonical orchestration seam `src/physics/utilization/characterize.py` (G1 car
ceiling → realised driver lap → G2 regime utilization), a bounded-subset dashboard
`scripts/driver_utilization_dashboard.py` (10 driver-sessions, 2023 Q, outputs to gitignored `reports/physics/`), a
fixture-backed smoke test `tests/unit/physics/test_driver_utilization_dashboard.py` (8 tests), the single-path
consolidation (retired the inline `sim_lap`/`_params` in `scripts/ideal_lap_compare.py` + `scripts/ideal_vs_actual.py`
to RuntimeError stubs), and a recommended readiness verdict `.agent-work/510-driver-utilization-quali/VERDICT.md`
(CONTEXTUAL). Implementer result: `.agent-work/510-driver-utilization-quali/crew-handoffs/g3-implement-result.md`
(read it in full). VERDICT.md: read it in full.

## How to Inspect the Diff
`git status -s` — project changes are: NEW `src/physics/utilization/characterize.py`,
`scripts/driver_utilization_dashboard.py`, `tests/unit/physics/test_driver_utilization_dashboard.py`; MODIFIED
`scripts/ideal_lap_compare.py`, `scripts/ideal_vs_actual.py` (retired to stubs). Ignore `.agent-work/**` churn.
**Confirm `reports/physics/*` outputs are NOT staged/tracked** (must be gitignored) and the 38 GB cache is untouched.

## Task Statement
Build the single canonical driver-utilization characterization run + traceable dashboard + recommended GO/CONTEXTUAL/
NO-GO verdict, and consolidate the ideal-lap sim onto one canonical path. Full task:
`.agent-work/510-driver-utilization-quali/crew-handoffs/g3-implement-handoff.md`.

## Close Criteria (each a review check)
- The entrypoint wires G1 `build_car_ceiling` → realised lap (session_fit + ribbon) → G2
  `estimate_driver_utilization` and returns tidy per-regime rows; the dashboard reproduces the readout.
- **Single canonical path:** the inline scalar `sim_lap` + `_params` are GONE; no second ideal-lap sim remains;
  retired scripts have no live consumers (the implementer claims grep-verified — spot-check it).
- The smoke test is genuinely fixture-backed (NO live cache/DB) and green (re-run it).
- VERDICT.md is evidence-backed (coverage, separability, covariance honesty) and does NOT over-claim a clean
  car/driver separation (split_is_impure caveat present).
- `constraint:physics_region_no_evo_import` held; `simplification_limits` clean; no regressions (implementer reports
  full physics suite 485 passed — spot-check by re-running the smoke test at minimum).

## THE central scrutiny point — is the verdict's headline finding TRUE?
The dashboard shows **`u_braking = 2.0` and `u_fast_corner = 2.0` (the clip ceiling) for ALL 10 cases**, and
`u_slow_corner` 1.38–1.86 (also > 1). U_r = mean(v_real/v_ideal); U > 1 means the realised lap is FASTER than the
simulated "ideal" ceiling — i.e. the ideal is NOT a ceiling in those regimes (a systematic under-call). The
implementer attributes this to the known braking-frontier under-call (#496 / `decision:smoother_rounds_braking_knee`).
**Your most important job:** decide whether this is a GENUINE characterization finding (the measured car-prior ceiling
really does under-call braking/fast-corner capability — making CONTEXTUAL the honest verdict) OR a CHARACTERIZE-LAYER
BUG that fakes it. Specifically rule out / confirm:
1. **Progress-fraction registration:** `resample_by_progress` registers real vs ideal by `u = s/s_total`. Could the
   ideal and real laps' different speed profiles mis-register corner/braking points enough to inflate the ratio to
   2.0 everywhere? (A small mis-registration would not push EVERY case to the hard clip — but confirm the magnitude
   is physical, not an artifact.)
2. **Units / capability sign:** is the car-prior ceiling's braking capability physically too low (e.g. the braking
   `b_b<0` weak-channel fallback, or the absent-ceiling Gsat fallback producing too-low cornering grip)? Cross-check
   against `decision:ideal_lap_sim_two_sided_evaluator` (small/negative gap = under-call suspect — this is that
   signal firing per-regime).
3. **Is U=2.0-everywhere consistent with a real under-call** (the ideal sim genuinely carries too little speed in
   braking + fast corners), and is the straight regime (U 0.56–1.51, circuit-sensible) evidence the pipeline is
   otherwise sound?
If it is a genuine under-call finding → APPROVE (CONTEXTUAL is honest; the under-call is the valuable result, with the
braking-ceiling reachback to #496). If it is a characterize-layer bug → BLOCK with the specific defect.

## Secondary scrutiny points (judge, but not necessarily blocking)
- **RuntimeError stubs vs deletion:** the two prototype scripts were retired to stubs that raise on import, not
  deleted. Is that an acceptable single-path consolidation (loud tombstone + a cleanup-commit triage), or should they
  be deleted now? Recommend APPROVE-with-triage unless you see a reason deletion is required.
- **VERDICT.md wording:** line ~12 calls slow-corner ceiling "over-estimated", but U>1 means the ceiling is
  *under*-called (ideal too slow). Flag the wording mismatch (the substantive separability conclusion is fine).
- **n_mc_samples=20** for the dashboard (vs default 50): acceptable for a characterization verdict? (σ slightly
  noisier; verdict doesn't hinge on tight σ.)
- **Module-level imports for monkeypatch testability:** the implementer made `fit_session_full`/
  `build_session_ribbon` module-level names in `characterize.py` (a deviation from lazy import) for test patching.
  Confirm this is clean (full suite passed) and not a smell.

## Allowed Scope
NEW: characterize.py, driver_utilization_dashboard.py, test_driver_utilization_dashboard.py, VERDICT.md,
reports/physics/* (gitignored). MODIFIED/RETIRED: ideal_lap_compare.py, ideal_vs_actual.py. Read-only reuse of
G1/G2/sim_evaluator/physics_simulator/ribbon/session_fit/estimate_store.

## Specific Exclusions (flag if touched)
No full 216-row sweep; no modification of G1 `car_prior.py` or G2 `regime_utilization.py`; no evo import; no
committed reports/cache.

## Constraints the Implementation Must Respect (each a check)
- `constraint:physics_region_no_evo_import`; single canonical execution path (inline sim retired); DB-only +
  offline-cache telemetry; derived artifacts out of git; `py` not `python`; public input validation.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (characterize.py, dashboard); retired `scripts/ideal_*`; `src/physics/utilization/*`
  (G1+G2); `data/physics_estimates.db`, `data/telemetry`.
- **Capability:** driver utilization characterization → dashboard + readiness verdict.
- **Constraints:** single canonical execution path; DB-only/offline-cache; derived artifacts out of git.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — its Review Trigger fires; the verdict consumes
  the sim-vs-real gap as the driver signal; the single-path canonicalization is the user's decision (this gate enacts
  it). Flag any contradiction as a candidate.
- **Evidence expectations:** reproducible dashboard + fixture smoke test green; VERDICT.md GO/CONTEXTUAL/NO-GO with
  coverage + separability + covariance-honesty evidence.

## Evidence Produced
- `py -m pytest tests/unit/physics/test_driver_utilization_dashboard.py -q` → 8 passed. **Re-run.**
- `py -m src.utils.simplification_limits --paths ...` → PASS (3 files; retired scripts also PASS).
- Full physics suite 485 passed, 6 skipped (implementer-reported).
- Dashboard run: 10/10 ok, 662.9 s; CSV + 5 figures in reports/physics/.

## Suggested Model Tier
Stronger-ish — the verdict-attribution judgment (true under-call vs characterize bug) is the crux and carries the
risk; it needs reading the registration + ceiling-fallback code, not just the tests.

## Stop Conditions
BLOCK if: the diff/outputs cannot be accessed; the smoke test is not fixture-backed or fails; a second ideal-lap sim
survives; an exclusion was touched; reports/cache were staged; or the central scrutiny reveals the U=2.0 finding is a
characterize-layer bug (not a real under-call).

## Return Format
Return REVIEW_RESULT to `.agent-work/510-driver-utilization-quali/crew-handoffs/g3-review-result.md`: verdict (literal
APPROVE or BLOCK), per-check findings, an EXPLICIT ruling on the central scrutiny point (true under-call finding vs
bug) with your reasoning, rulings on the secondary points, blockers, out-of-scope observations, Workflow Feedback.
