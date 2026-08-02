# Reviewer Handoff

## Gate
g5 (RE-PLANNED) — Diagnose + fix the ideal-lap simulator over-acceleration (review). The fix corrects
a units bug that has confounded C1 since #510; G6 re-runs C1 on the corrected ideal lap.

## What Was Implemented
A one-line units conversion in `car_prior._build_longitudinal`: the store's `p_max` is TOTAL watts
(~629 kW), but `theta_P_values` is consumed as SPECIFIC power (W/kg = m²/s³) by the simulator/envelope/
`fit_power_trajectory`/`default_theta_P=300`. Fix: `theta_P_values=[p_max/MASS_KG]` + covariance
`/MASS_KG²` + units docstring + bridge-table rows. Result: RBR ideal-lap top speed on a pure straight
908.8 m/s → 94.80 m/s (ratio to analytic terminal velocity = 1.0000). New invariant test (RED→GREEN).
The capability MEASUREMENT (p_max value) is unchanged — only its unit representation at the assembly boundary.

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git diff HEAD -- src/physics/utilization/car_prior.py tests/unit/physics/test_car_prior.py
git status --short   # new: tests/unit/physics/test_ideal_lap_top_speed_invariant.py
```
Result: `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g5-implement-result.md`.

## Task Statement
Diagnose why the ideal lap over-accelerates (~207 m/s on the ribbon / 909 on a straight vs ~95 m/s
physical), fix it in the ideal-lap machinery without changing the capability measurement, with truth-anchored evidence.

## Close Criteria (each a review check)
- **The diagnosis is correct:** confirm the bug is the watts→W/kg units mismatch (store `p_max` is total
  watts; `theta_P` convention is specific power). Confirm the fix locus is the producer (`car_prior`), and
  that a blanket `/mass` in `physics_data_models.max_power` would be WRONG (double-divides the already-W/kg
  `fit_power_trajectory` path). Verify `fit_power_trajectory` / `default_theta_P=300` are indeed W/kg.
- **The fix works:** re-run the invariant test inline; independently probe the RBR ideal-lap top speed
  (build the ceiling via `car_prior.build_car_ceiling` on `data/physics_estimates_g3wired.db`, simulate,
  check max speed ≈ 95 m/s ≈ analytic terminal velocity, not ~207/909).
- **The measurement is unchanged:** confirm the store's `p_max` value is untouched and no fit/braking/
  traction/lateral/power-drag code changed — only the units representation at the `car_prior` boundary.
- **Covariance converted correctly:** the `theta_P` σ also divided by MASS_KG (variance /MASS_KG²).
- **Braking/cornering preserved:** confirm the forward-backward sweep still produces a plausible lap
  (the fix only caps straight-line top speed). The crew's synthetic spot-check: 81.3s lap, braking
  59.9→9.0 m/s, fast sweep 93.4 m/s — re-run or inspect.
- **Tests reproduce:** `py -m pytest tests/unit/physics/ -q` green (604 passed); `py -m src.utils.simplification_limits` clean. Re-run inline.

## Allowed Scope (what the implementation touched)
`car_prior.py` (units conversion + docstring), `test_car_prior.py` (updated expectations), new invariant test.

## Specific Exclusions (flag if touched)
Any capability fit (braking_fit/traction_fit/power_drag_view/lateral_envelope), the store, the utilization
layer/dashboard, `regime_utilization`/`U_CLIP_MAX`, `docs/architecture/**` — must be unchanged.

## Constraints
- Physics model change → L1-L4 truth evidence (the invariant test). `py` not `python`. One canonical path.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `car_prior.py`; `struct:physics` — `capability_envelope.py`, `physics_simulator.py`, `physics_data_models.py` (read-only verify the units convention).
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — the ideal-lap-as-ceiling contract; this fix makes the ideal lap physical (was aphysically HIGH since #510). Note for reconcile.
- **Evidence:** ideal-lap top speed ≈ terminal velocity; this unblocks the G6 C1 re-run.

## Evidence Produced
- Invariant test RED (921.5 vs 96.3) → GREEN (2 passed). Full physics suite 604 passed. Simplification PASS.
- Before/after RBR straight top speed: 908.8 → 94.80 m/s (ratio 1.0000). Braking/cornering spot-check PASS.

## Suggested Model Tier
Bounded (Sonnet) — the fix is a contained, well-evidenced units conversion; verify the units logic, re-run
the invariant test + a top-speed probe, confirm no measurement change + braking/cornering preserved. Escalate only if the units reasoning is ambiguous.

## Stop Conditions
BLOCK if: the diagnosis is wrong (not a units bug); the ideal-lap top speed is not physical after the fix;
a capability measurement/fit was changed; the covariance was not converted; braking/cornering regressed;
an excluded file was touched; tests don't reproduce.

## Return Format
Return REVIEW_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g5-review-result.md` with a
clear `verdict: APPROVE` or `verdict: BLOCK`, per-check findings (incl. YOUR probed top-speed number),
blockers, out-of-scope observations, and Workflow Feedback.
