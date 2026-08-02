# Review Result

## Assigned Gate
`g3-review (C1 #510, driver-utilization-quali, branch feat/c1-driver-utilization-510)`

## Result
`APPROVE`

## Handoff compliance
All deliverables present and correct:

- `src/physics/utilization/characterize.py` — canonical G1→realised lap→G2 orchestration seam built; wires `build_car_ceiling` → `session_fit`/`ribbon` → `estimate_driver_utilization`; returns `UtilizationRow` objects.
- `scripts/driver_utilization_dashboard.py` — bounded 10-case dashboard, outputs to gitignored `reports/physics/`, n_mc_samples=20 for bounded runtime.
- `tests/unit/physics/test_driver_utilization_dashboard.py` — 8 fixture-backed tests covering orchestration, error propagation, batch interface.
- `.agent-work/510-driver-utilization-quali/VERDICT.md` — CONTEXTUAL verdict with circuit-coverage, separability, covariance-honesty, split_is_impure caveat, and recommended actions.
- `scripts/ideal_lap_compare.py` and `scripts/ideal_vs_actual.py` — retired to RuntimeError stubs; `sim_lap` and `_params` are gone.

The close criteria entrypoint wiring check passes: `_build_ceiling` → `_load_lap_and_ribbon` → `_utilization_row_from` maps exactly to the G1→realised→G2 contract.

## Scope drift
None. The diff against main shows only `scripts/ideal_lap_compare.py` and `scripts/ideal_vs_actual.py` as modified source files. All new files (`characterize.py`, `driver_utilization_dashboard.py`, `test_driver_utilization_dashboard.py`, `VERDICT.md`) are within allowed scope.

Exclusions confirmed honored:
- G1 `car_prior.py` — untouched.
- G2 `regime_utilization.py` — untouched.
- No evo imports anywhere in new or modified files.
- No full 216-row sweep.
- `reports/physics/*` gitignored, not staged.
- `data/telemetry` cache untouched (not in diff).

## Evidence verdict
Evidence is present and verified:

- **Smoke test:** Re-run confirmed 8/8 pass in 0.26s. No live cache/DB: all I/O seams injected (stub `load_session_fn`, monkeypatched `fit_session_full` and `build_session_ribbon`). 0.26s runtime is definitive offline proof.
- **Dashboard run:** 10/10 ok, 662.9s (implementer-reported; dashboard table included in implement result; circuit-sensible u_straight variation is independently interpretable as pipeline-health signal).
- **Simplification limits:** PASS on all 5 touched paths (implementer-reported; `characterize.py` was refactored from 133 lines to sub-function extraction before commit).
- **Full physics suite:** 485 passed, 6 skipped (implementer-reported; no regression).

Test mode is test-after (orchestration glue), as specified. TDD was not required.

## Code/doc quality
Clean. Module-level imports of `fit_session_full`/`build_session_ribbon` in `characterize.py` are a documented implementer deviation from lazy-import (required for pytest monkeypatch compatibility); the module docstring explains the rationale. All functions are under simplification_limits. Docstrings on public functions are thorough.

One wording error in VERDICT.md line ~12: "slow-corner ceiling is **over-estimated**" should be "under-called" — U>1 means the realised lap is faster than the ideal ceiling, meaning the ceiling is too low (under-called), not too high (over-estimated). The substantive separability and verdict conclusions are correct; only the one-line regime label is wrong. This is a secondary observation (not a blocker).

## Map impact verdict

- **Evidence supports claimed change:** Yes. The dashboard table demonstrates (a) the pipeline runs 10/10 without error, (b) u_braking/u_fast_corner clip at 2.0 for all cases confirming the ceiling under-call, (c) u_straight shows circuit-level variation (Monza 0.56–0.58, Monaco 1.20–1.51) consistent with F1 track types, (d) sigma_u_straight widens correctly for fewer causal sessions. All claims in the Map Impact section are backed.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` honored; single canonical execution path enacted (inline sim gone); DB-only/offline-cache constraint honored; derived artifacts gitignored.
- **Notes match the diff:** Yes. Structural, capability, constraint, and decision anchors stated in Map Impact all match what the diff shows. Retired scripts correctly demoted from structural.
- **Decision candidates surfaced:** `decision:ideal_lap_sim_two_sided_evaluator` Review Trigger correctly fired; the verdict documents the sim-vs-real gap per-regime. Single-path canonicalization is correctly noted as user-authority decision enacted.
- **Durable context routed:** Triage candidates present in implement result (braking ceiling under-call confirmed at scale, session caching for runtime, RuntimeError stub cleanup, lap-sampling sigma omission). One additional item for routing: `scripts/ver_monza_kde.py` is now broken (imports from retired `ideal_lap_compare.py`) — this should go to Triage for cleanup alongside the stub deletion.

## Central scrutiny ruling — GENUINE UNDER-CALL FINDING

**Verdict: GENUINE CHARACTERIZATION FINDING, not a characterize-layer bug. APPROVE stands.**

Three independent lines of evidence:

**1. Progress registration is correct.**
`resample_by_progress` (in `sim_evaluator.py`, lines 52–65) normalises both the target distance grid (simulator ribbon) and the source distance axis (driver best lap) to progress fraction `u = s/s_total` before interpolating. This is a well-defined, physically correct registration. A misregistration artifact could shift individual ratios but cannot push ALL 10 diverse cases (4 circuit types, 5 constructor classes, including Monza power-track and Monaco street circuit) to exactly the hard clip ceiling of 2.0 in braking AND fast_corner simultaneously, while leaving u_straight at circuit-sensible values (0.56–1.51). The two regimes would need to misregister in exactly the same direction on every circuit for this to be a registration artifact.

**2. Ceiling under-call mechanism is confirmed in code.**
`car_prior.py` module docstring (line ~54): `lateral.ceiling` is **always None** from this path — "not fabricated" is explicit. `CapabilityEnvelope.from_parameters` (line ~79–93): `ceiling_trustworthy = False` when `lat.ceiling is None` (which is always, for this path). This means the Gsat fallback tyre-saturation ceiling is absent — the lateral envelope is anchored to the mechanical A0+A2v² model only, without the measured tyre ceiling that would cap it at the correct level.

For braking: when `b_b >= 0`, the measured frontier `a_brake(v) = a_b + b_b*v²` is used; when `b_b < 0`, the fallback is `braking_grip_ratio × lateral`. **Both** are known conservative. The MEMORY note `decision:smoother_rounds_braking_knee` documents: raw p99 5.3g vs smoothed p90 4.3g — the GP prior fights the braking knee, underestimating peak deceleration in both the measured frontier path and, through the lateral anchor, the population-ratio fallback. This is the known documented under-call that `decision:ideal_lap_sim_two_sided_evaluator` was designed to detect (small/negative gap = under-call suspect).

For fast corners: the lateral ceiling absent (`ceiling=None`) means cornering grip is the A0+A2v² polynomial, which flattens at high speed rather than saturating at the tyre limit. Fast corners are high-a_lat → this regime pushes the lateral grip to its polynomial maximum, which is below what the measured tyre ceiling would permit.

**3. The straight regime is the pipeline sanity signal.**
u_straight shows:
- Monza (power/low-drag): 0.56–0.58 — physically correct lift-and-coast behavior on a high-speed circuit
- Monaco (street/slow): 1.20–1.51 — physically correct full-throttle on short straights
- Silverstone (mixed): 0.775–0.854 — intermediate, as expected
- Singapore (technical/slow): 0.831 — consistent with street circuit pattern

This is exactly the circuit-type discrimination a physically correct straight-regime utilization should show. If the pipeline had a systematic bug (inverted ratio, wrong axis, registration failure), u_straight would not reproduce this physically interpretable pattern. The straight regime is operating correctly; the under-call is specific to braking and fast_corner as expected from the known ceiling calibration gap.

**Conclusion:** The U=2.0 clip for braking and fast_corner in all 10 cases is the two-sided evaluator firing per-regime, exactly as `decision:ideal_lap_sim_two_sided_evaluator` predicted (under-call signal). CONTEXTUAL is the honest verdict. The under-call result is the valuable characterization output — it identifies which regimes need #496's outer-loop or regime-specific ceiling recalibration before being usable.

## Reconciliation check
No concerns beyond what is documented. `struct:physics` should route `characterize.py` as a new canonical seam; the implement result's Map Impact section carries this correctly. Triage candidates (ceiling recalibration, clip-detection warning, session caching, stub cleanup, `ver_monza_kde.py` repair) are all present. No drift from the recorded architecture that Commander must reconcile beyond Map Impact.

## Blockers
None.

## Out-of-scope observations

1. **`scripts/ver_monza_kde.py` is broken by the retirement.** This diagnostic script imports `sim_lap`, `_params`, `build_track`, `field_drivers`, `_CACHE`, `_OUT`, `_DB` from `scripts/ideal_lap_compare.py` (line 36–38). After the RuntimeError stub retirement, importing `ver_monza_kde.py` raises `RuntimeError`. This script is NOT in `tests/` or `src/`, so it does not gate the physics suite. However it will fail if anyone tries to run it. Triage candidate: update or delete `ver_monza_kde.py` in the same cleanup commit as the stub deletion (once Commander confirms no downstream callers need these scripts).

2. **VERDICT.md wording error — "over-estimated" vs "under-called."** Line ~12: "Slow-corner regime: CONTEXTUAL — partially separable but ceiling is **over-estimated**." U_r > 1 means the realised lap is faster than the ideal ceiling → the ceiling is **under-called** (too low), not over-estimated (too high). The word direction is inverted. The separability verdict and recommended actions are substantively correct; only the one-line description is wrong. Non-blocking; correct before the verdict is presented to users.

3. **RuntimeError stubs vs deletion.** The stubs are a reasonable loud-tombstone approach; the implement result explicitly calls out cleanup-commit as a triage item. APPROVE-with-triage is the correct call here; no reason to demand deletion now.

4. **n_mc_samples=20 acceptability.** For a CONTEXTUAL verdict that does not hinge on tight sigma, n=20 is acceptable. The sigma propagation is demonstrably correct (widens for fewer causal sessions). A GO verdict that uses these sigmas for inference would want n_mc_samples closer to the default 50. Acceptable for this gate.

5. **Module-level import deviation.** The module-level imports of `fit_session_full` and `build_session_ribbon` in `characterize.py` deviate from the lazy-import convention but are required for pytest monkeypatch compatibility. Documented in the module docstring. Full physics suite passes (485/0 fail). Acceptable; not a smell.

6. **Lap-sampling sigma omission.** The realised lap is a single best lap; its timing noise (~0.05–0.1%) is not modelled. Acknowledged in the module docstring of `regime_utilization.py` and in VERDICT.md. Acceptable for CONTEXTUAL; must be addressed before GO.

## Workflow Feedback

- **Handoff gaps:** The handoff's "verify no live consumers" check was framed as grep for imports of `ideal_lap_compare`/`ideal_vs_actual` without specifying the scope (`tests/`, `src/`, or all `scripts/`). When I grep'd all of `scripts/`, `ver_monza_kde.py` showed up as a live consumer — which is correct but the handoff didn't clarify whether `scripts/` consumers should be a BLOCK or an observation. Interpreting "live consumers" as `tests/` and `src/` (since CI runs those) is the right call; scripts/ diagnostics are not CI-gated. The handoff should specify "no test/src consumers" explicitly.

- **Context rediscovered:** Had to grep for `b_b` behavior and `ceiling=None` by reading `car_prior.py` and `capability_envelope.py` directly. The handoff mentioned the `b_b<0` weak-channel fallback but did not point to the specific fallback paths in code (which function, which line), requiring manual traversal. Pre-linking the exact fallback logic in the handoff's scrutiny section would reduce reviewer read-time.

- **Instructions improvised around:** The engine template's six survey items (r0–r5) do not map cleanly to a constraint-per-check review. I appended r4a through r4g and r5/r6 as extra items, which is compliant with the `append` verb, but the template doesn't explicitly document that pattern. Clarifying the template to say "append one item per inherited constraint rule" would remove ambiguity.

- **What would have made this easier:** The handoff's central scrutiny section is excellent and thorough — it was the right structure. One concrete improvement: include a one-line reading of what `resample_by_progress` actually does (it normalizes to [0,1] before interpolating), so the reviewer can confirm the registration without needing to grep for the function. The current text says "could progress-fraction mis-registration inflate..." which implies uncertainty; the code makes it unambiguous and the handoff could note "read sim_evaluator.py lines 52–65 to confirm."

## Return status
`complete`
