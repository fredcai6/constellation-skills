# Review Result

## Assigned Gate
`g2-review` (C1 #510, work-id `510-driver-utilization-quali`, branch `feat/c1-driver-utilization-510`)

## Result
`APPROVE`

No blockers. All close criteria satisfied. Three scrutiny points ruled (see below).
Four triage candidates flagged.

---

## Handoff compliance
The handoff asked for: pure core `regime_utilization()` with four non-overlapping regimes
(braking / slow_corner / fast_corner / straight), a thin integration wrapper
`estimate_driver_utilization()` using the canonical PhysicsSimulator path and MC covariance
propagation, honest σ, impure-split caveat, and 17 TDD tests covering the invariants.

All delivered. Public API matches spec. TDD contract is evidenced (red before green confirmed
in implement-result: `ModuleNotFoundError` before implementation, 17 passed after). Refactor
while green also confirmed (function split from 106 to 79 lines).

---

## Scope drift
**None.** New files only: `src/physics/utilization/regime_utilization.py` and
`tests/unit/physics/test_regime_utilization.py` (both untracked/uncommitted on the branch —
files exist on disk, not yet in a commit). `git diff main --` on all six excluded files
(`car_prior.py`, `sim_evaluator.py`, `physics_simulator.py`, `capability_envelope.py`,
`session_fit.py`, `ribbon.py`) returns empty. No `scripts/` changes. `test_car_prior.py` is
also untracked — a G1 artifact, not G2 scope.

Note: the implementation files are not yet committed. This is not a blocking concern for
review (the files exist and tests pass), but G3/Admiral should ensure a commit is created
before merge.

---

## Evidence verdict
**Green.** Independently re-ran:

```
py -m pytest tests/unit/physics/test_regime_utilization.py -q
→ 17 passed in 0.24s (Python 3.14.3, pytest-9.0.2)

py -m src.utils.simplification_limits --paths src/physics/utilization/regime_utilization.py tests/unit/physics/test_regime_utilization.py
→ PASS (2 files)
```

Both match implementer-reported results. TDD evidence (red → green → refactor) is documented
in the implement-result. Tests are behavior-focused (invariants, classification, covariance
monotonicity), not implementation-mirroring.

---

## Code/doc quality
Code is minimal, maintainable, and project-rule compliant:
- Module-level docstring is thorough; covers formula, honest covariance, car/driver caveat,
  lap-sampling limitation, and decision anchor.
- All regime thresholds are named module constants (`FAST_CORNER_ALAT_THRESHOLD`,
  `CURVATURE_THRESHOLD`, `BRAKING_DECEL_THRESHOLD` imported by name, `U_CLIP_MAX`,
  `MIN_REGIME_POINTS`, `DEFAULT_MC_SAMPLES`).
- `_build_regime_masks` has an inline `assert` that validates tiling at runtime.
- `_validate_inputs` provides field/expectation/actual error messages.
- `PhysicsSimulator` is a deferred import (`from src.physics.physics_simulator import ...`)
  inside `estimate_driver_utilization` — avoids circular imports.
- Function lengths respect simplification limits (confirmed).
- No inline magic numbers for regime thresholds.

---

## Map impact verdict

- **Evidence supports claimed change:** Yes. The new capability (driver utilization per-regime)
  is confirmed by 17 passing tests including real-sim covariance tests. Evidence backs the
  claimed structural addition and capability extension.

- **Constraints not violated:** Yes. `constraint:physics_region_no_evo_import` — confirmed by
  grep (empty result). `honest covariance first-class` — MC loop samples real envelope params.
  `single canonical path` — PhysicsSimulator only, no second inline sim.

- **Notes match the diff:** Yes. Implementer's Map Impact names `regime_utilization.py` (new),
  `sim_evaluator.resample_by_progress + BRAKING_DECEL_THRESHOLD` (reused), and
  `PhysicsSimulator._sample_parameters + simulate_lap` (canonical MC path). All accurate.

- **Decision candidates surfaced:** Yes. `U_r` formula, `FAST_CORNER_ALAT_THRESHOLD=25 m/s²`,
  and MC implementation path are all surfaced as explicit decisions. The private-method API
  gap is identified and triage-flagged.

- **Durable context routed:** Yes. Triage candidates for `monte_carlo_laps` API gap,
  `__init__.py` re-exports, mean-of-ratios refinement, and MC seed are flagged. Lap-sampling
  TODO hook is in the module docstring and function docstring.

---

## Reconciliation check
Map Impact notes accurately describe what the diff contains. The new module belongs to
`struct:physics` and extends `decision:ideal_lap_sim_two_sided_evaluator` (per-point Δv now
aggregated into per-regime U_r with σ). No structural contradiction with recorded
architecture. Cartographer should add `regime_utilization.py` to the architecture index and
flag the `__init__.py` re-export gap.

---

## Per-check findings

### Close criteria

**r4a — Frontier invariant (v_real==v_ideal → U_r≈1.0):** PASS.
`TestFrontierInvariant.test_frontier_all_regimes` uses `_four_regime_track()` with
`v_real=v_ideal.copy()` and asserts `|u−1.0|<1e-6` per populated regime. Non-tautological:
the full pipeline (gradient computation, masking, ratio path, clipping) is exercised. Formula
`mean(v/v)=1.0` is proven through the ratio path, not hardcoded.

**r4b — Uniform-0.9 invariant (v_real==0.9·v_ideal → U_r≈0.9):** PASS.
`TestUniform90Scaling.test_uniform_90_all_regimes` asserts `|u−0.9|<1e-6` per populated
regime. `np.clip(..., 0, 2.0)` does not interfere (0.9 < 2.0). Monotone test
`test_monotone_in_fraction` further confirms U_r increases from 0.5→1.0.

**r4c — Partition tiling (every point exactly once):** PASS.
`_build_regime_masks` is algebraically correct: `mask_straight = NOT(braking | slow_corner
| fast_corner)` where `slow_corner = (~braking) & is_slow` and `fast_corner = (~braking) &
is_fast`. Every point falls in exactly one of: {braking, non-braking slow corner, non-braking
fast corner, non-braking non-corner=straight}. Proven formally: `braking OR slow OR fast =
braking OR (NOT braking AND is_corner)`. Straight = complement = `NOT braking AND NOT
is_corner`. No gaps, no overlaps by construction. Inline `assert` in `_build_regime_masks`
catches runtime violations. Two separate tests: `test_masks_cover_all_points` (coverage) and
`test_masks_no_overlap` (all pairwise intersections == 0) on the four-regime track.

**r4d — Honest covariance (MC-propagated σ grows with envelope σ):** PASS.
`_mc_speed_profiles` calls `sim._sample_parameters(params, rng, joint=True)` + `simulate_lap`
in a loop, collecting per-point speed profiles. `_sigma_u_from_mc_speeds` computes std of
per-draw regime-mean ratios — a real Monte Carlo scatter, not nominal.
`TestCovarianceMonotonic.test_sigma_u_grows_with_envelope_sigma` runs `cov_scale=[0.01, 1.0,
100.0]` through full `estimate_driver_utilization` with real `PhysicsSimulator` (injected,
not mocked), `n_mc_samples=30`, `seed=42`. Asserts `sigma_u_straight` monotone non-decreasing.

**r4e — Impure-split caveat explicit in artifact:** PASS.
Caveat present at four levels in the source file:
1. Module-level docstring "Car/driver split caveat" section: "The split is ACKNOWLEDGED IMPURE"
2. `RegimeUtilization` dataclass docstring: `split_is_impure: always True`
3. `regime_utilization()` return: `split_is_impure=True` hardcoded
4. `estimate_driver_utilization()` docstring: `split_is_impure=True always`
Test `TestImpurityDocumented.test_result_has_impure_split_flag` asserts both presence and value.

**r4f — Reuse not duplication:** PASS.
Line 61: `from src.physics.sim_evaluator import BRAKING_DECEL_THRESHOLD, resample_by_progress`.
Both imported, not re-implemented. `BRAKING_DECEL_THRESHOLD` is the default for `decel_threshold`
parameter. `resample_by_progress` called directly. `PhysicsSimulator` is the single simulator.

**r4g — No evo import:** PASS.
`grep -rn 'evo_predictor' src/physics/utilization/` → empty.

**r4h — No inline magic numbers:** PASS.
All five regime-relevant constants are named: `FAST_CORNER_ALAT_THRESHOLD=25.0`,
`CURVATURE_THRESHOLD=1e-4`, `BRAKING_DECEL_THRESHOLD` (imported), `U_CLIP_MAX=2.0`,
`MIN_REGIME_POINTS=2`. Numerical epsilon guards (`1e-6`) are not regime thresholds.

---

## Three scrutiny point rulings

### Scrutiny 1: MC using `PhysicsSimulator._sample_parameters` (private method)
**RULING: APPROVE with triage candidate.**

`monte_carlo_laps` returns `LapTimeDistribution` (lap times only) — verified by reading
`physics_simulator.py`. There is NO public API that returns per-point speed profiles from
a Monte Carlo parameter sweep. The `_sample_parameters` + `simulate_lap` loop in
`_mc_speed_profiles` (lines 413–423) is structurally identical to the loop inside
`monte_carlo_laps` itself (lines 186–189 of `physics_simulator.py`). The implementation
reuses the simulator's own internal sampling machinery — it does not re-implement sampling
logic. The caller (`_mc_speed_profiles`) is within the same physics region and the
private-method usage is the correct path given the API gap. This is not a boundary violation;
it is a single-canonical-path use of internal machinery forced by an API gap.

Triage candidate: `PhysicsSimulator` should expose a public `monte_carlo_speed_profiles()`
or similar method that returns per-point speed profiles, allowing future callers to avoid
the private `_sample_parameters` path. This is a G3/follow-on issue, not a G2 blocker.

### Scrutiny 2: `U_r = mean(v_real_i / v_ideal_i)` (mean-of-ratios)
**RULING: DEFENSIBLE for first characterization. Note logged.**

Mean-of-ratios satisfies both L2 invariants exactly (frontier→1.0, uniform-0.9→0.9), proven
by the test suite. The formula is interpretable: "what fraction of the ceiling did the driver
average per track point in this regime?" The known limitation is equal-point weighting (ignores
GPS sampling density within a regime — a high-speed straight with many samples is weighted the
same per-point as a compressed braking zone). This does not distort the sign or direction of
the measurement; it is a first-order approximation. Distance-weighted or time-weighted integral
would be a natural refinement but is not required for a first characterization. BLOCK not
warranted. Triage candidate logged for G3.

### Scrutiny 3: Lap-sampling σ not modelled
**RULING: HONEST. Limitation is disclosed in the artifact.**

The lap-sampling understatement is disclosed in the source file (`regime_utilization.py`) at
two points:
- Module-level docstring: "The **realised lap is a single best lap** — its lap-sampling noise
  is NOT modelled here (one sample from the driver's lap-time distribution). A TODO hook is
  left for a future lap-sampling term."
- `estimate_driver_utilization()` docstring: "**Lap-sampling hook:** the realised lap is a
  single best lap — its lap-sampling noise is NOT modelled here. A future extension should add
  a lap-sampling sigma term and combine it in quadrature with the envelope sigma."

The `sigma_u_*` field is present (not omitted) with the envelope-only σ. Callers see the value
and the caveat together. The limitation is NOT hidden — it is actively flagged. This is honest.

---

## Blockers
None.

---

## Out-of-scope observations

1. **Implementation files not yet committed.** `src/physics/utilization/regime_utilization.py`
   and `tests/unit/physics/test_regime_utilization.py` are untracked (`??` in git status).
   Files exist and tests pass, but a commit is needed before merge. G3/Admiral should ensure
   this.

2. **`test_car_prior.py` also untracked** — this is a G1 artifact left uncommitted. Should
   be committed as part of G1 closeout, not G2 scope.

3. **`src/physics/utilization/__init__.py` re-exports.** `regime_utilization` is not
   re-exported from the package `__init__.py`. Direct import works but is inconsistent with
   `car_prior` pattern. Cartographer candidate.

4. **`CURVATURE_THRESHOLD` (1e-4 m⁻¹) vs PhysicsEstimatorConfig threshold.** The implementer
   notes a potential drift risk if the sim's own curvature threshold (from `PhysicsEstimatorConfig`)
   diverges from the module constant. A config-wiring to share the same value would prevent
   future drift. Triage candidate.

---

## Triage candidates (flagged in survey)

- **tc1** (from r4i): Expose `PhysicsSimulator.monte_carlo_speed_profiles()` public API
  returning per-point speed profiles to eliminate the `_sample_parameters` private call.

- **tc2** (from r5): Add `regime_utilization` re-export to `src/physics/utilization/__init__.py`
  for consistency with `car_prior`. Cartographer candidate.

- **tc3** (from r4j): Consider distance-weighted or time-weighted integral for `U_r` as a
  refinement over equal-point mean-of-ratios. G3/follow-on.

- **tc4** (from r4d): Make MC `seed` a named config field (e.g. `PhysicsEstimatorConfig`) so
  production `estimate_driver_utilization` calls are reproducible without caller-side seed
  threading.

---

## Workflow Feedback

- **Handoff gaps:** The `g2-review-handoff.md` says "Allowed Scope: Read-only reuse of
  car_prior/sim_evaluator/physics_simulator/ribbon/session_fit" but doesn't call out that the
  implementation files are expected to be untracked (not committed). This caused a minor
  confusion on whether `git status -s` showing `??` was expected behavior or a gap. A note
  that "files will be untracked pending Commander commit" would remove ambiguity.

- **Context rediscovered:** Had to read `physics_simulator.py` lines 128–220 to verify that
  `monte_carlo_laps` truly returns lap times only and that `_sample_parameters` is the correct
  internal path. The handoff correctly flagged the scrutiny point but didn't carry enough
  context to rule without reading the source. The implement-result's Workflow Feedback had
  already surfaced this, which was helpful context.

- **Instructions improvised around:** The REVIEW_SURVEY template has 6 items
  (r0–r5); the handoff specified 7 close criteria, 5 constraints, and 3 scrutiny points — 15
  distinct checks. I appended r4a–r4k as sub-items under r4-quality to keep every check
  engine-tracked without flattening them into a single finding. The engine's `append` verb on
  a survey handled this cleanly; no instruction was violated, just extended.

- **What would have made this easier:** A one-line note in the handoff confirming that the
  implementation files will be untracked (not committed) on the branch at review time, and
  that the review should verify files on disk (not git-tracked). This is a workflow pattern
  gap for any G2 review that follows a G2 implement without an intermediate commit step.

## Return status
`complete`
