# Implementer Handoff

## Gate
g2-implement (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## Task
Build `src/physics/utilization/regime_utilization.py`: the **per-regime driver-utilization estimator**. Given the
G1 car-capability ceiling (a `CarCeilingResult` from `src/physics/utilization/car_prior.py`, exposing
`.params` / `.envelope`), a driver's **realised best quali lap** (speed-vs-distance trace), and the session ribbon
geometry (distance, curvature), compute how much of the car's achievable lap the driver extracted — **decomposed
per regime** (slow corner / fast corner / braking / straight) — normalised to compare across circuits/cars, with
**honest covariance** propagated from the envelope covariance.

### Design: a pure core + a thin integration wrapper (KEEP THEM SEPARATE)

**(a) Pure core (fully unit-testable with arrays — NO FastF1, NO DB).** A function such as
`regime_utilization(distance, curvature, v_real, v_ideal, *, config) -> RegimeUtilization` that:
- Registers `v_real` and `v_ideal` on a shared distance/progress grid (reuse
  `src/physics/sim_evaluator.py::resample_by_progress` — do NOT duplicate it).
- Partitions every track point into exactly one of FOUR regimes (the masks must **tile** the lap — full coverage,
  no overlap):
  - **braking** — real speed dropping into a corner (`dv_real/ds < -decel_threshold`); reuse the threshold idea in
    `sim_evaluator.braking_zone_delta_v`.
  - **slow corner** vs **fast corner** — cornering points (high lateral demand / curvature) split by a
    downforce-loading cut. Use a NAMED CONSTANT threshold on the lateral-acceleration demand `a_lat = v² · |κ|`
    (slow corner = mechanical-grip-dominated low-`a_lat`/low-speed apex; fast corner = aero/downforce-dominated
    high-speed) — pick a defensible default (document it; e.g. an `a_lat` or apex-speed boundary) and make it a
    module constant / config field, not an inline magic number. Memory: slow-corner ≈ μ·g mechanical, fast-corner
    ≈ k_df aero.
  - **straight** — the remainder: low curvature, on throttle, not braking.
- Computes a per-regime utilization `U_r` = how close the realised speed rode the ceiling in that regime. Define it
  so a driver riding the ceiling scores ≈ 1.0 and a uniform 0.9× driver scores ≈ 0.9 (e.g. the regime-mean of
  `v_real / v_ideal`, clipped to a sane range). Also report a per-regime **consistency** (e.g. 1 − coeff-of-var, or
  the spread of the ratio) — "how much AND with what consistency" (issue wording). Return per-regime `U_r`,
  consistency, point counts, and the regime masks.

**(b) Thin integration wrapper** that takes the G1 envelope + a driver's realised lap + ribbon, runs the canonical
ideal-lap sim, and calls the pure core. Use `PhysicsSimulator` (the CANONICAL path — `simulate_lap` for the point
ideal, `monte_carlo_laps` for covariance; do NOT write a second inline sim). For the realised lap and ribbon, reuse
the EXISTING seams the way `sim_evaluator.evaluate_session` does (`session_fit.load_quali_session`,
`session_fit.fit_session_full` for `.best_distance`/`.best_speed_real`/`.best_lap_s`, `ribbon.build_session_ribbon`)
— but the ceiling/ideal lap comes from the **G1 car prior**, NOT the driver's own fit (that is the whole point of
C1: envelope = car, utilization = driver).

### Honest covariance (first-class)
Propagate the **envelope covariance** into the utilization: sample the car-ceiling parameters from their covariance
and run `PhysicsSimulator.monte_carlo_laps` (joint covariance sampling already exists) to get a per-point
**ideal-speed distribution**, then propagate to a **σ on each `U_r`**. The σ must GROW with the envelope σ (test
this). Note the lap-sampling term (the realised lap is a single best lap) — if you don't model it fully, state that
explicitly and leave a hook; do not silently treat the realised lap as noise-free if it materially understates σ.
**The car/driver split is acknowledged IMPURE** (driver and car are only ever observed together) — the artifact
must carry that caveat (docstring + a field/flag), and you must NOT over-claim a clean separation.

## Protected Intent
A driver-skill readout that is honestly bounded (covariance reflects the ceiling's uncertainty), per-regime (not a
single aggregate), reuses the one canonical sim path, and never pretends the car/driver split is pure. Measurement
only — NOT wired into evo.

## Test Mode
TDD required. Physics evidence at highest applicable L1–L4. Tests in `tests/unit/physics/test_regime_utilization.py`,
using SYNTHETIC arrays / injected ideal laps (NOT the live FastF1 cache or DB).

## Close Criteria
- `src/physics/utilization/regime_utilization.py` with the pure core + thin wrapper as above.
- `tests/unit/physics/test_regime_utilization.py` green, covering:
  - **L2 frontier:** a synthetic driver whose `v_real == v_ideal` scores `U_r ≈ 1.0` in every populated regime.
  - **L2 uniform-0.9:** `v_real == 0.9·v_ideal` scores `U_r ≈ 0.9` in every populated regime.
  - **L1/L2 partition tiling:** the four regime masks cover every point exactly once (no gaps, no overlaps) on a
    synthetic track with all four regimes present.
  - **L2 covariance monotonic:** inflating the envelope covariance increases each `U_r` σ (honest, not nominal).
  - regime-boundary behavior: a known slow vs fast corner lands in the right bucket given the `a_lat` threshold.
- `py -m src.utils.simplification_limits` clean on touched paths.

## Allowed Scope
NEW: `src/physics/utilization/regime_utilization.py`, `tests/unit/physics/test_regime_utilization.py`. Reading/
reusing: `src/physics/utilization/car_prior.py`, `sim_evaluator.py`, `physics_simulator.py`, `ribbon.py`,
`session_fit.py`, `capability_envelope.py`, `physics_config.py`. You MAY add a small regime-config constant block.

## Specific Exclusions
- No batch run / dashboard / verdict (that is G3). No `scripts/` changes.
- No second inline lap sim. No change to G1 `car_prior.py` (consume it; if you find a real defect, STOP and report,
  do not patch it here).
- No evo-region import. Do not change `sim_evaluator.py` (reuse its pure helpers; if you must extend, prefer adding
  to the new module).

## Constraints
- `constraint:physics_region_no_evo_import`. Single canonical execution path (PhysicsSimulator only). Honest
  covariance first-class (propagate envelope σ; not nominal). Regime thresholds are named constants/config, not
  inline magic numbers. `py` not `python`. Validate public inputs (field/expectation/actual). Highest-applicable
  L1–L4 evidence.

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `src/physics/utilization/regime_utilization.py` (new); `sim_evaluator.py`
  (Δv seed, reused pure helpers); `physics_simulator.py` + `ribbon.py` (ideal lap + geometry); G1
  `utilization/car_prior.py` (ceiling source).
- **Capability:** driver utilization measurement (per-regime extraction of the car frontier) — new; extends
  `decision:ideal_lap_sim_two_sided_evaluator` (the sim-vs-real gap IS the driver-utilisation signal).
- **Constraints:** physics_region_no_evo_import; honest covariance first-class; single canonical path.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — the gap is the driver signal (its Review
  Trigger fires on this layer); per-point Δv is the primary read. Do not contradict; surface candidates.
- **Evidence expectations:** frontier→~1, 0.9→~0.9; mask tiling; covariance monotonic in envelope σ.

## Required Evidence
- `py -m pytest tests/unit/physics/test_regime_utilization.py -q` (green).
- `py -m src.utils.simplification_limits --paths <touched>` (clean).
- A short note on: the `U_r` definition, the slow/fast `a_lat` threshold + default, and the covariance method
  (MC over envelope σ) incl. how lap-sampling is handled or hooked.

## Verification Commands
```bash
py -m pytest tests/unit/physics/test_regime_utilization.py -q
py -m src.utils.simplification_limits --paths src/physics/utilization/regime_utilization.py tests/unit/physics/test_regime_utilization.py
```

## Suggested Model Tier
Stronger-ish: the regime partition correctness, the utilization definition meeting the frontier/0.9 invariants, and
honest covariance propagation carry the risk. Lean on the L2 invariant tests.

## Authority
Decided (do not relitigate): envelope = car (from G1 car prior), utilization = driver; per-regime decomposition into
slow/fast corner + braking + straight; canonical sim path = PhysicsSimulator; the split is acknowledged impure
(covariance owns it). You may decide: the exact `U_r` and consistency formulas (meet the invariants), the slow/fast
`a_lat` threshold default (document it), and the MC sample count (sane default).

## Stop Conditions
Stop and return if: allowed scope must be exceeded; an exclusion must be touched; the frontier/0.9 invariants cannot
be met with a defensible `U_r`; honest covariance cannot be propagated from the envelope; or a real defect in G1
`car_prior.py` blocks consumption.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/510-driver-utilization-quali/crew-handoffs/g2-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence (pasted pytest + simplification_limits output),
assumptions (incl. `U_r` formula, `a_lat` threshold, MC count, lap-sampling handling), stop conditions, out-of-scope
observations, and Workflow Feedback.
