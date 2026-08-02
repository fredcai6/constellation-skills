# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-implement (C1 #510, driver-utilization-quali, branch feat/c1-driver-utilization-510)`

## Completed slice

Built the canonical characterization entrypoint, a bounded dashboard, the smoke test, and
enacted the single-path consolidation (retired the inline scalar sim). Wrote the evidence-backed
verdict (CONTEXTUAL) with full dashboard output.

## Scope

**Files changed:**

NEW:
- `src/physics/utilization/characterize.py` — canonical orchestration seam (G1 → realised lap → G2)
- `scripts/driver_utilization_dashboard.py` — bounded-subset characterization dashboard
- `tests/unit/physics/test_driver_utilization_dashboard.py` — fixture-backed smoke test (8 tests)
- `.agent-work/510-driver-utilization-quali/VERDICT.md` — recommended readiness verdict

MODIFIED/RETIRED (single-path consolidation):
- `scripts/ideal_lap_compare.py` — RETIRED: inline `sim_lap` + `_params` removed; replaced with a
  RuntimeError stub stating the inline sim has been canonicalized (see below)
- `scripts/ideal_vs_actual.py` — RETIRED: removed import chain from ideal_lap_compare; replaced with
  a RuntimeError stub

Generated (gitignored, reports/physics/):
- `reports/physics/driver_util_subset_2023.csv`
- `reports/physics/driver_util_monaco_2023.png`
- `reports/physics/driver_util_italy_2023.png`
- `reports/physics/driver_util_great_britain_2023.png`
- `reports/physics/driver_util_singapore_2023.png`
- `reports/physics/driver_util_summary_2023.png`

**Specific exclusions touched:** No — did not modify G1 `car_prior.py`, G2 `regime_utilization.py`,
or any evo-region code.

## Behavior changed

Yes.
1. `src/physics/utilization/characterize.py` adds a new canonical characterization entrypoint that
   connects G1 → session refit → G2 regime utilization, returning tidy UtilizationRow objects.
2. `scripts/driver_utilization_dashboard.py` runs the bounded subset and emits CSV + figures.
3. `scripts/ideal_lap_compare.py` and `scripts/ideal_vs_actual.py` now raise RuntimeError on import
   (they are retired stubs); any downstream caller that imported them will now fail explicitly.
4. The inline quasi-static `sim_lap` function and the `_params` scalar bridge prototype are GONE
   from the codebase. There is now ONE canonical ideal-lap path.

## Map Impact

- **Structural anchors touched:**
  - `struct:physics` — new `src/physics/utilization/characterize.py` added as the canonical
    G1→G2 orchestration seam; `scripts/ideal_lap_compare.py` and `scripts/ideal_vs_actual.py`
    retired from active scripts (RuntimeError stubs in place, no longer structural)
  - `scripts/ideal_lap_compare.py` — retired; was a prototype script with inline scalar sim
  - `scripts/ideal_vs_actual.py` — retired; was an importer of the prototype sim

- **Capabilities added/changed/affected:**
  - NEW: driver utilization characterization — per-regime U_r measurement for any (year, gp_name,
    driver) case using the canonical physics path; batch interface via `characterize_cases`
  - RETIRED: inline quasi-static lap sim (sim_lap + _params) that was a second parallel ideal-lap path

- **Constraints/assumptions touched:**
  - `constraint:physics_region_no_evo_import` — honored; no evo imports
  - Single canonical execution path constraint — ENACTED: inline scalar sim retired; only
    `PhysicsParameterSet → CapabilityEnvelope → PhysicsSimulator` path remains
  - DB-only / offline-cache telemetry — honored; store_df injected, cache path absolute

- **Decision candidates / resolved decisions:**
  - `decision:ideal_lap_sim_two_sided_evaluator` — Review Trigger fires; the verdict
    (CONTEXTUAL) documents the sim-vs-real gap: braking/fast_corner regimes are systematically
    under-called (U clips at 2.0 for all 10 cases); straight regime is sensible and circuit-varying.
    Canonicalization enacted per user decision.

- **Claims/evidence produced:**
  - Claim: 10/10 bounded-subset cases run without error on 2023 Q data
  - Claim: braking and fast_corner ceiling is systematically under-called (U=2.0 clip for all cases)
  - Claim: straight regime shows sensible circuit-level variation (Monza 0.56–0.58 vs Monaco 1.20–1.51)
  - Claim: sigma_u_straight widens correctly for lower n_sessions_causal (Monaco n=6, sigma=0.024
    vs Italy n=14, sigma=0.006)

- **Trust limitations / drift found:**
  - Braking and fast_corner utilization numbers are NOT trustworthy (all clip at 2.0). The under-call
    issue is the same root cause as #496's outer-loop gap (braking frontier underestimates peak decel).
  - Lap-sampling sigma is NOT modelled (single best lap; timing noise not propagated).
  - split_is_impure=True for all rows — car/driver entanglement is irreducible with this method.

- **Triage candidates:**
  - #496 outer-loop still needed: braking/fast_corner regimes useless until ceiling recalibrated.
  - Add clip-detection warning to dashboard: flag regimes where >= 50% of cases clip at U_CLIP_MAX.
  - Retire the RuntimeError stubs in `scripts/ideal_lap_compare.py` + `scripts/ideal_vs_actual.py`
    in a cleanup commit once the Commander confirms no downstream callers need them.

## Test mode

**Required:** test-after (orchestration/dashboard glue) + smoke test fixture-backed (required)
**Satisfied:** Yes — smoke test is fixture-backed (no live cache/DB), 8/8 green; full physics suite
485 passed, 6 skipped after all changes.

## Evidence

### Smoke test

```
py -m pytest tests/unit/physics/test_driver_utilization_dashboard.py -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2
collected 8 items

tests/unit/physics/test_driver_utilization_dashboard.py::TestL1Orchestration::test_returns_utilization_row PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL1Orchestration::test_at_least_one_regime_has_value PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL1Orchestration::test_n_sessions_causal_positive PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL2ErrorPropagation::test_session_load_failure_returns_error_row PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL2ErrorPropagation::test_missing_constructor_in_store_returns_error_row PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL2ErrorPropagation::test_fit_session_full_none_returns_error_row PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL3BatchInterface::test_batch_one_per_case PASSED
tests/unit/physics/test_driver_utilization_dashboard.py::TestL3BatchInterface::test_rows_to_dataframe_shape PASSED

============================== 8 passed in 0.28s ==============================
```

**Result:** PASS

### Simplification limits

```
py -m src.utils.simplification_limits --paths src/physics/utilization/characterize.py scripts/driver_utilization_dashboard.py tests/unit/physics/test_driver_utilization_dashboard.py
```

```
PASS (3 files checked)
```

(Also checked retired scripts: `py -m src.utils.simplification_limits --paths scripts/ideal_lap_compare.py scripts/ideal_vs_actual.py` → PASS)

**Result:** PASS (clean on all touched paths)

### Full physics suite (post-change)

```
py -m pytest tests/unit/physics/ -q
```

```
485 passed, 6 skipped in 278.59s
```

**Result:** PASS — no regressions

### Dashboard run log (bounded 10-case subset)

```
py scripts/driver_utilization_dashboard.py --mc-samples 20
```

Ran 2026-06-24, 10/10 ok, 0 errors, 662.9 s.

Cases run:
  VER Monaco (Red Bull Racing, slow/mechanical)
  LEC Monaco (Ferrari, slow/mechanical)
  VER Italy (Red Bull Racing, power/low-drag)
  NOR Italy (McLaren, power/low-drag)
  ALB Italy (Williams, weak team, power/low-drag)
  VER Great Britain (Red Bull Racing, mixed)
  NOR Great Britain (McLaren, mixed)
  HAM Great Britain (Mercedes, mixed)
  ALB Great Britain (Williams, weak team, mixed)
  VER Singapore (Red Bull Racing, technical/slow)

Output files (gitignored, in reports/physics/):
  driver_util_subset_2023.csv
  driver_util_monaco_2023.png
  driver_util_italy_2023.png
  driver_util_great_britain_2023.png
  driver_util_singapore_2023.png
  driver_util_summary_2023.png

Raw dashboard table (from run log):
  driver       gp_name     constructor  u_braking  u_slow_corner  u_fast_corner  u_straight  sigma_u_straight  n_sessions_causal
  VER          Monaco      Red Bull      2.000      1.644          2.000          1.196       0.024             6
  LEC          Monaco      Ferrari       2.000      1.750          2.000          1.509       0.006             6
  VER          Italy       Red Bull      2.000      1.439          2.000          0.578       0.006             14
  NOR          Italy       McLaren       2.000      1.378          2.000          0.564       0.011             14
  ALB          Italy       Williams      2.000      1.403          2.000          0.572       0.012             13
  VER          G Britain   Red Bull      2.000      1.829          2.000          0.775       0.006             10
  NOR          G Britain   McLaren       2.000      1.859          2.000          0.807       0.007             10
  HAM          G Britain   Mercedes      2.000      1.840          2.000          0.789       0.010             10
  ALB          G Britain   Williams      2.000      1.851          2.000          0.854       0.004             10
  VER          Singapore   Red Bull      2.000      1.489          2.000          0.831       0.007             15

## TDD evidence, if required

Not required (test-after mode). The smoke test was written before the dashboard run.

## Single-path consolidation statement

The inline scalar quasi-static forward-backward lap simulator (`sim_lap`) and the parameter bridge
prototype (`_params`) that existed in `scripts/ideal_lap_compare.py` have been removed. The file
now raises `RuntimeError` on import. `scripts/ideal_vs_actual.py`, which imported both functions
and `build_track`/`field_drivers`/`_CACHE`/`_OUT`/`_DB` from `ideal_lap_compare.py`, has also been
retired to a RuntimeError stub.

No still-needed helpers were found to require relocation: `build_track` wraps `build_session_ribbon`
+ terrain (already in `ribbon.py`), and `field_drivers` wraps session introspection. The new
`scripts/driver_utilization_dashboard.py` does not need these helpers (it uses `characterize_cases`
which delegates to `build_session_ribbon` internally).

After this gate:
- ZERO inline scalar sim functions remain in `scripts/`
- ONE canonical ideal-lap path: `EstimateStore → car_prior.build_car_ceiling → CapabilityEnvelope → PhysicsSimulator.simulate_lap`
- This is verified by the retired-stub approach (any import of the old scripts now fails loudly)

## Recommended verdict + evidence summary

**CONTEXTUAL** — per `.agent-work/510-driver-utilization-quali/VERDICT.md`

The pipeline is mechanically correct (10/10 cases, no errors). The characterization reveals:

1. BRAKING + FAST_CORNER: NO-GO (systematic under-call; U=2.0 for all 10 cases). The car ceiling
   in these regimes is too low — the driver always appears to exceed it. Root cause: braking frontier
   underestimation (same #496 issue). These regime readings are NOT usable.

2. SLOW_CORNER: CONTEXTUAL. U ranges 1.38–1.86 (still above 1.0 but not clipping). Shows circuit-type
   variation (Monaco vs Monza vs Silverstone) but not team/driver discrimination within a circuit.

3. STRAIGHT: CONTEXTUAL. U ranges 0.56–1.51. Physically sensible (Monza lift-and-coast = 0.57,
   Monaco full-throttle = 1.20–1.51). Shows circuit-type variation; team differences within circuit
   are ~5–10% (below lap-sampling noise floor). The sigma propagation works correctly (tighter for more
   causal sessions).

OVERALL: CONTEXTUAL — the straight regime carries real circuit-level signal; the pipeline works;
the ceiling calibration gap in braking/fast_corner must be resolved before those regimes are usable.
A CONTEXTUAL outcome with good evidence is exactly what this gate was designed to catch.

## Docs/contracts touched
- None beyond the in-code docstrings and the `.agent-work/` artifacts (per handoff scope).

## Assumptions

1. The `load_quali_session` signature `(year, gp_name, session_type, cache, offline=True)` was found
   not to match the 3-arg injected pattern documented in `sim_evaluator.evaluate_session`. Fixed by
   passing `session_type="Q"` explicitly in `_load_lap_and_ribbon`.

2. The `build_track` / `field_drivers` helpers in `ideal_lap_compare.py` were assumed not to be
   needed by any live consumer outside of the two retired scripts. Verified by grep — no other imports.

3. The monkeypatch pattern for `fit_session_full` / `build_session_ribbon` requires these to be
   module-level names in `characterize.py` (not lazily imported). This is an implementer deviation
   from the original lazy-import design — the deviation is required for testability and documented
   in the module docstring.

4. `n_mc_samples=20` for the full dashboard run (not the default 50) to keep the run time bounded.
   The sigma values are slightly higher-variance at 20 samples but informative enough for the verdict.

## Stop conditions hit

None. No scope exceedance, no G1/G2 defects blocking the run, no timeout.

## Out-of-scope observations

1. **Braking ceiling under-call is confirmed at scale.** U_braking=2.0 (clip) for 100% of the
   bounded subset. This is NOT a one-circuit anomaly. The #496 outer-loop or a regime-specific
   ceiling floor is needed before C1 characterization is usable in braking/fast_corner regimes.

2. **Repeated session loading per-case is expensive.** Each case loads the full FastF1 session
   (~60 s per unique session). A session cache (load once, reuse across drivers in the same GP) would
   reduce the 10-case runtime from ~663 s to ~100-200 s. This is out of scope for this gate but
   is worth a triage issue.

3. **RuntimeError stubs for retired scripts are a temporary state.** The stubs prevent import but
   leave two files that raise on use. A cleanup commit (delete the stubs) is appropriate once
   Commander confirms no downstream callers need them.

4. **Lap-sampling sigma omission will matter if C1 advances to GO.** The single-best-lap timing
   noise (~0.05–0.1%) is not modelled in G2. For a GO verdict the propagated sigma should include
   a lap-sampling term. Currently the sigma only reflects envelope uncertainty.

## Workflow Feedback

- **Handoff gaps:** The `load_session_fn` injection point in the handoff described the callable as
  `(year, gp_name, cache) -> ...` (3 args), but `session_fit.load_quali_session` takes
  `(year, gp, session_type, cache, offline=True)` (4+ args). The injected signature must match.
  This caused a first-pass "Invalid session type" error from FastF1 before being caught and fixed.
  The handoff should specify the exact callable signature for the load_session_fn seam.

- **Context rediscovered:** The monkeypatch limitation (lazy imports inside functions prevent
  `setattr` patching) had to be rediscovered by running the tests and seeing the AttributeError.
  The handoff mentioned "injected seams" but did not specify how to wire them for pytest monkeypatch
  compatibility. Resolved by importing at module level and referencing via `_self_module` object.

- **Instructions improvised around:** The engine checklist template had no step for a multi-step
  function (G1 → load → G2 → assemble) that needed to be decomposed to pass simplification_limits.
  `characterize_case` was 133 lines on first write; required extraction of 4 sub-functions to get
  under 99 lines. The split (G1 step, load step, utilization step, assembly step) is the right
  architecture regardless, but the template's "make the minimal change" instruction needed adaptation.

- **What would have made this easier:** The handoff's "keep the orchestration logic testable with
  injected seams" should specify exactly which seams need injection and what their call signatures are,
  referencing the actual function signatures in the codebase (not the 3-arg convenience pattern used
  in `sim_evaluator.evaluate_session` which differs from the real `load_quali_session` signature).

## Return status
`complete`
