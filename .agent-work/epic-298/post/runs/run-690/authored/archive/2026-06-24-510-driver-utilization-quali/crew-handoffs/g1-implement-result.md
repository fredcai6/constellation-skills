# Implementation Result

## Assigned gate
`g1-implement` (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## Completed slice
Created `src/physics/utilization/` package with `car_prior.py` — the canonical causal
as-of constructor car-capability ceiling. Added `tests/unit/physics/test_car_prior.py`
covering L1 bridge known-answer, L3 causal exclusion, determinism, and missing-channel
fallback. 27/27 tests green; simplification_limits clean.

## Scope
**Files changed:**
- `src/physics/utilization/__init__.py` (new)
- `src/physics/utilization/car_prior.py` (new)
- `tests/unit/physics/test_car_prior.py` (new)

**Specific exclusions touched:** no — existing `DriftFit.predict` unmodified (only an
additive `causal_predict` function added, kept in the new module); no evo-region imports;
no second inline sim; no estimator/pooling math changed.

## Behavior changed
Yes (new capability). New public API:
- `causal_predict(clock, values, sigmas, *, clock_target, step_var, strictly_pre)` →
  `(mu, sigma_mu)`: one-sided causal GP prediction.
- `build_car_ceiling(*, store_df, year, constructor, target_round, strictly_pre, config)` →
  `CarCeilingResult(params, envelope, air_density, n_sessions, as_of_means)`: causal
  as-of ceiling assembly.

## Map Impact

- **Structural anchors touched:**
  - `struct:physics` — new sub-package `src/physics/utilization/` created; sits alongside
    `layer2/` and the existing capability/sim modules.
  - `struct:physics.layer2` — consumed read-only (`estimate_store.EstimateRecord`,
    `pooling.fit_drift`); no changes made there.
  - `physics_data_models.py::PhysicsParameterSet` — bridged to from store scalars
    (as specified in Map Anchors).
  - `capability_envelope.py` — consumed via the canonical `from_parameters` path only.

- **Capabilities added/changed/affected:**
  - New `purpose:physics_utilization` (candidate label): assembles the causal as-of car
    ceiling from the five-view estimate store. Consumes `purpose:physics_estimation`
    output; does NOT alter it.

- **Constraints/assumptions touched:**
  - `constraint:physics_region_no_evo_import` — honored; imports only from `src.physics.*`.
  - As-of contract — explicit: `target_round` is a named required parameter; no silent
    fallback to latest/whole-season.
  - Single canonical execution path — honored: `CapabilityEnvelope.from_parameters` is
    the only sim entry point; no second inline scalar sim.
  - Honest covariance — first-class: pooled σ propagates into all sub-parameter
    covariances; blob preferred over diagonal; documented in module docstring.

- **Decision candidates / resolved decisions:**
  - **Clock proxy = round_idx** (not `upgrade_clock` from `upgrades.yaml`). Rationale:
    avoids a hard dependency on the upgrades file being present in tests; round_idx is
    always available in the store and is a valid monotone proxy. Step_var estimated from
    the causal subset anyway, so the clock scale only affects the drift rate magnitude.
    This is a local decision within the granted authority.
  - **k_tire=0.0, g_track=1.0**: neutral defaults matched to single-session convention in
    `session_fit.py` line 89 (store does not carry tire-wear or track-evolution scalars).
  - **strictly_pre clock shift**: when `strictly_pre=True`, `clock_target = target_round -
    0.5` so that `causal_predict`'s `<= clock_target` condition correctly excludes exactly
    the target round (since round_idx values are integers).
  - `decision:ideal_lap_sim_two_sided_evaluator` — honored: ceiling=None is left for the
    Gsat fallback in CapabilityEnvelope; not contradicted.

- **Claims/evidence produced:**
  - L1 (analytical): `theta_D = cda_closed / (2 × 808.0)` verified to rel_tol=1e-6.
  - L1 (analytical): `theta_D_std = cda_sigma / (2 × 808.0)` verified.
  - L1 (analytical): covariance blob used over diagonal when blob present (verified by
    checking off-diagonal non-zero).
  - L3 (causal exclusion): future session does not change through-W prior (verified by
    comparing theta_D with and without a round-5 session when target=2).
  - L3 (strictly-pre): own-session excluded; pre-W result derived from only round-1 CdA
    when target=2 (verified against analytical expected).
  - L3 (determinism): same inputs produce identical outputs twice.
  - L3 (ceiling fallback): ceiling=None throughout; no fabrication.
  - L3 (missing-channel): absent A0/A2 uses config defaults; absent coast_theta_R uses
    module-level fallback; constructor absent raises ValueError.

- **Trust limitations / drift found:**
  - The `as_of_means["A2"]` key is populated even when A0/A2 fell back to config
    defaults; a consumer should check `n_sessions` or `fit_quality_metrics` to detect
    this fallback. Consider a `fallback_channels: list[str]` field in `CarCeilingResult`
    in a future gate.

- **Triage candidates:**
  - The clock proxy (round_idx) should be upgraded to `upgrade_clock` from `upgrades.yaml`
    in a follow-up when the upgrades file is consistently present. The step_var computation
    then becomes more physically meaningful (measures drift-per-upgrade, not drift-per-round).
    Currently conservative and correct.
  - `CarCeilingResult` lacks an explicit `fallback_channels: list[str]` field that names
    which channels used config defaults vs pooled values. Useful for G2 (driver utilization)
    consumers who need to know confidence level per channel.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes — tests written first, confirmed failing (ModuleNotFoundError), then
implementation made them green; refactor while green (two rounds, simplification_limits
compliance).

## Evidence

```
py -m pytest tests/unit/physics/test_car_prior.py -q
```

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1Brainz
configfile: pyproject.toml
plugins: anyio-4.9.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 27 items

tests\unit\physics\test_car_prior.py ...........................         [100%]

27 passed in 0.22s
```

**Result:** pass

```
py -m src.utils.simplification_limits --paths src/physics/utilization/car_prior.py tests/unit/physics/test_car_prior.py
```

```
PASS (2 files checked)
```

**Result:** pass (clean)

## TDD evidence, if required

- **Failing test observed:** `ModuleNotFoundError: No module named 'src.physics.utilization'`
  (on `py -m pytest tests/unit/physics/test_car_prior.py` before implementation).
- **Passing test observed:** 27 passed in 0.22s (after implementation).
- **Refactor while green:** yes — two rounds of refactoring to satisfy simplification_limits:
  (1) extracted `_pool_cda_pmax_theta_r`, `_assemble_braking/traction/lateral`;
  (2) extracted `_build_longitudinal`, changed assemblers to return `(obj, means_dict)`
  to eliminate triple re-calls in `build_car_ceiling`. Both rounds kept all 27 tests green.

## Docs/contracts touched
- Module docstring in `car_prior.py` documents the full bridge table, covariance policy,
  causal contract, k_tire/g_track defaults, ceiling rule, and canonical path — serves as
  the contract doc for G2 consumers.
- `src/physics/utilization/__init__.py` has a package docstring.

## Assumptions
- **MASS_KG = 808.0** — imported from `src.physics.longitudinal_fit` (canonical site).
  Matches `session_fit.py` and `longitudinal_fit.py`.
- **Clock proxy = round_idx** — uses round number as a uniform development clock rather
  than the FIA upgrade count from `upgrades.yaml`. Valid monotone proxy; step_var
  magnitude differs but causal correctness is preserved.
- **strictly_pre clock shift**: `clock_target = target_round - 0.5` when `strictly_pre=True`
  (avoids a separate code path; integers never equal a half-integer).
- **k_tire=0.0, g_track=1.0** — neutral defaults; store does not carry these. Matches
  single-session convention in `session_fit.py` line 89.
- **Default air density 1.225** — used when store carries no finite rho values. This is
  the standard sea-level density; no silent fallback to any session-specific value.
- **Covariance blob selection** — `_pick_representative_blob` returns the most-recent
  (last-row) valid 2×2 blob from the causal slice. With multi-session causal data this
  picks the most recent session's blob. A pooled covariance blob would be more rigorous
  but is not available from the current store schema.

## Stop conditions hit
- None.

## Out-of-scope observations
- **G2 readiness**: `CarCeilingResult.envelope` exposes `traction_capability`, `braking_capability`,
  and `lateral_capability` at any speed — all that G2 (driver utilization) needs is to call
  these against the driver's observed peak accelerations per regime. The API is clean.
- **`_pick_representative_sigma`** was defined in the first draft but became unused after the
  refactor (assemblers use the causal_pool sigma_mu directly). It was removed.
- **Pooled multi-session covariance**: the current implementation uses the most-recent session's
  blob (or diagonal from pooled sigma_mu). A proper pooled 2×2 covariance would require either
  storing a pooled blob in the store or computing it here from the per-session blobs. This is
  out of scope and deferred to a future gate (noted in triage candidates).

## Workflow Feedback

- **Handoff gaps:**
  - The handoff references `DriftFit.predict` as the symmetric smoother (correctly), but the
    `causal_predict` placement instruction says "Put the causal evaluator next to / on top of
    the existing `fit_drift`/`DriftFit` (in `pooling.py` or the new module — your call)". The
    granted authority covers this, but the handoff doesn't mention the simplification_limits
    constraint that limits function complexity and line count. Had I placed `causal_predict` in
    `pooling.py`, it still would have needed refactoring for limits compliance. The function
    ended up in the new module as permitted — no issue, but the limit constraint would have been
    useful to flag in the handoff.
  - The handoff describes `LateralParameters` with parameters `k_tire`, `g_track` and says
    "Confirm sensible defaults against how a single-session LateralParameters is built elsewhere."
    The relevant anchor was `session_fit.py` line 89 — this was easy to find via grep, but a
    direct pointer would have saved a lookup round.

- **Context rediscovered:**
  - MASS_KG location: the handoff says "grep for the MASS constant" — found it at
    `src/physics/longitudinal_fit.py:MASS_KG = 808.0`, also `session_fit.py:MASS_KG = 808.0`.
    Two definitions exist; canonical is `longitudinal_fit.py` (imported by session_fit). A
    direct citation of `src.physics.longitudinal_fit.MASS_KG` in the handoff would have
    removed the ambiguity.
  - The `simplification_limits` tool flag format: the handoff says
    `py -m src.utils.simplification_limits <touched paths>` but the actual flag is `--paths`.
    A bare `none` would have failed. Minor; easy to discover, but fixed cost every time.

- **Instructions improvised around:**
  - The checklist engine script was not found in the skill directory (`scripts/checklist_engine.py`
    absent). The engine was driven manually by tracking step status inline. This is a known
    gap when the engine binary is missing in the installed skill.
  - The `IMPLEMENTER_RESULT.template.md` references `skills/workbench/references/status-model.md`
    for status values — not available in this context. Used standard values (complete/partial/etc.)
    from the template field labels.

- **What would have made this easier:**
  - A concrete pointer to `src.physics.longitudinal_fit.MASS_KG` (not just "grep") and the
    `--paths` flag for simplification_limits in the verification commands.

## Return status
`complete`
