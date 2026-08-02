# x2 — Reference-lap machinery audit

Question: can the physics machinery emit a per-car per-weekend IDEAL (reference) lap
today, and which inputs are frontier-fits vs mean-fits end-to-end?

Read-only excursion over `C:\Programs\f1Brainz`. All paths/functions below were opened
and read directly (not inferred from docs).

## 1. Call path(s) that produce a reference lap today

There are **two distinct, non-unified** call paths that both end in
`PhysicsSimulator.simulate_lap`. Neither is what you'd design from scratch as "the"
reference-lap API — one is a diagnostic that admits it isn't trustworthy yet, the other
computes a full lap but throws the scalar away.

### Path A — `sim_evaluator.evaluate_session` (weekend-local, diagnostic)

`src/physics/sim_evaluator.py::evaluate_session(row, cache, ...)` — entry point,
one (year, gp, driver) row from the fit store.

1. Loads the one Q session (`session_fit.load_quali_session`).
2. Recovers `PhysicsParameterSet` — either reconstructed from a stored fit row
   (`fit_store.params_from_record`) or a fresh re-fit of **that single session's own
   telemetry** (`session_fit.fit_session_full` → `ParameterEstimator.estimate_parameters`,
   see §2/§3 — this is the weekend-local frontier-fit chain).
3. Builds track geometry via `ribbon.build_session_ribbon(session, [driver])` — a
   **median-pooled** XY line across that session's flying laps (`src/physics/ribbon.py`),
   not the driver's own shortest line.
4. `PhysicsSimulator().simulate_lap(track_df, params, sample=False)` (`src/physics/physics_simulator.py:50`)
   → `SimulatedLap(lap_time_s, speed_profile, distance_profile)` — this **is** a scalar
   per-car per-weekend ideal lap time.
5. Returns `sim_lap_s`, `real_lap_s`, `gap_pct`, Δv diagnostics (`sim_evaluator.py:338` `_session_metrics`).

**Caveat, in the code's own evidence file** (`reports/physics/P1a_sim_evaluator_findings.md`):
on a 20-session 2023 sample, `gap_pct` mean is 0.33%, median 0.95%, 47% of sessions have
the sim **slower** than the real lap. Expected ceiling gap was ~10%. Three causes cited:
(1) the median-pooled ribbon line is longer than the real fastest line, (2) sim/real
speed traces are mis-registered, (3) braking is under-called (~3.9g vs ~5g real). The
report's own conclusion: *"the ideal-lap-as-ceiling premise is compromised"* — i.e. Path A
runs end-to-end and returns a number, but that number is not yet a trustworthy ceiling.

### Path B — `car_prior.build_car_ceiling` → `regime_utilization` (pooled, production)

This is the path actually wired into the shipped #628 driver-utility gate (memory:
"Held-out gate VERDICT PASS").

1. `src/physics/utilization/car_prior.py::build_car_ceiling(store_df, year, constructor,
   target_round, strictly_pre=True)` — pools a constructor's **five-view EstimateStore**
   rows causally (§3) into one `PhysicsParameterSet` + `CapabilityEnvelope`
   (`CarCeilingResult`).
2. `src/physics/utilization/regime_utilization.py::estimate_driver_utilization` — calls
   `PhysicsSimulator.simulate_lap(track_df, ceiling.params, sample=False)`
   (`regime_utilization.py:584`, `_mc_speed_profiles` for the MC sigma draws) to get
   `nominal_lap`, then interpolates `v_ideal_on_grid` from `nominal_lap.speed_profile`.
3. That per-point ideal-speed profile is compared to the driver's own realised best-lap
   trace (`session_fit.fit_best_lap_trace`, weekend-local) via
   `regime_utilization` (ratio) or `driver_utility_observable.compute_regime_deficits`
   (absolute deficit, the anti-circularity-hardened sibling).
4. The **live batch driver**, `scripts/build_driver_utility_observables.py::_process_constructor`
   (line ~268), literally does: `ceiling = build_car_ceiling(..., strictly_pre=True)`,
   `nominal_lap = sim.simulate_lap(track_df, ceiling.params, sample=False)`,
   `v_ideal_on_grid = np.interp(...)` — this **is** a full per-car per-weekend reference
   lap simulation, run today, in production code (not just a test).

**The gap**: `nominal_lap.lap_time_s` — the scalar ideal lap time — is computed inside
that call but **never read or persisted** anywhere downstream in Path B. Every consumer
(`RegimeUtilization`, `RegimeDeficits`, the persisted `driver_utility_observables` table)
only keeps the per-regime aggregates of the speed profile. So: the machinery to emit a
per-car per-weekend reference **lap time** exists and runs, but production code discards
it in favor of per-regime speed deficits. Recovering a scalar reference lap time from
Path B would be a one-line addition (`nominal_lap.lap_time_s`), not new infrastructure.

Neither path is deprecated/dead — Path A is a standalone diagnostic (`scripts/run_sim_evaluator.py`,
last evidence 2023Q sample only) and Path B is the live #628 pipeline. They are not
unified: Path A's params come from a from-scratch weekend-local re-fit; Path B's come from
the pooled five-view store.

## 2. Per-view frontier vs mean-fit table

The five views live in `src/physics/layer2/{braking,lateral,traction,power_drag,coast}_view.py`
and all except Coast share one fitting primitive, `src/physics/layer2/frontier_fit.py::fit_frontier`
(via `kernel_upper_ridge`, `frontier_fit.py:49`): a Gaussian-kernel local **q=0.90 upper
quantile** ridge, then a parametric envelope fit with a **one-sided (asymmetric) loss** —
points above the line are expensive, points below are cheap (`w_above=10.0, w_below=0.3`
in every view's `fit()` call) — explicitly built to cantilever over a declining/sparse tail
rather than average through it. That is a capability-frontier fit, not a mean fit, by
construction.

| View | File | Fit mechanism | Frontier or mean? | Evidence |
|---|---|---|---|---|
| Braking | `braking_view.py::BrakingView.fit` | `fit_frontier` on de-conflated decel, `q=0.90`, `w_above=10/w_below=0.3`, `b_b≥0` bound | **Frontier** | Docstring: "kernel local-upper-quantile ridge, then a one-sided envelope fit... cantilever over the declining tail" (`braking_view.py:1-16`) |
| Lateral | `lateral_view.py::LateralView.fit` | `fit_frontier` on de-conflated grip coefficient `mu_obs`, same q/w_above/w_below, both coefs ≥0 | **Frontier** | `lateral_view.py:94-181` |
| Traction | `traction_view.py::TractionView.fit` | `fit_frontier` on the **ascent only** (below power crossover) of the throttle-on hump | **Frontier** | Docstring explicitly distinguishes the frontier ascent from PowerDragView's descent (`traction_view.py:1-24`) |
| Power/Drag | `power_drag_view.py::PowerDragView.fit` | `fit_frontier` (pinned or joint) on the WOT descent, `tightness=` "lowest bounding curve" | **Frontier** | `power_drag_view.py:100-150`; this is the max-power/min-drag envelope, not an average throttle-on lap |
| Coast | `coast_view.py::CoastView.fit` | Parametric **quantile regression** (pinball loss, `tau=0.20`, lower envelope) of `decel = θ_R + CdA·ρv²/2m` | **NOT a capability frontier** — a physics-constant identification | Docstring, verbatim: *"This is NOT a capability frontier — every coast sample IS the physics curve"* (`coast_view.py:1-21`). The low-τ lower-quantile is there only to dodge MGU-K regen contamination (regen adds spurious deceleration on top of the clean physical curve), not to find a driver ceiling. |

Implication for the "utilization = circular" worry: Braking/Lateral/Traction/PowerDrag are
genuine capability-frontier fits, so utilization built from them is not simply refit
residual. Coast is different in kind — it identifies rolling resistance and cross-checks
CdA, and it feeds `theta_R`/CdA priors into the other views' de-conflation, but it does not
itself define a driver-capability axis, so a "coast utilization" would not mean what the
other four axes mean. (No such axis exists downstream — the four axes wired into
`driver_utility_observable.py`/`regime_utilization.py` are braking, slow_corner, fast_corner,
straight, i.e. braking+lateral+traction+power_drag territory; coast never appears as a
utilization regime.)

## 3. Weekend-locality of envelope inputs

**Each of the five views is fit per-session** (one weekend's Q session), not cross-session:
`src/physics/layer2/estimate_batch.py::run_estimate_batch` loads one quali session per
`(season, GP)`, groups drivers by constructor, and calls `session_estimator.estimate_session`
once per constructor — producing one `SessionEstimate` row per (year, gp, constructor)
persisted to the EstimateStore (`estimate_store.record_from_estimate`). So the raw
per-weekend evidence for all five views does exist and is durable (I did not open
`session_estimator.py` itself — see §4 nulls).

**Cross-session pooling** happens one layer up, in `car_prior.py`, and it is NOT the
`pool_random_effects` DerSimonian–Laird mechanism used elsewhere (e.g. G2's teammate-relative
pooling in `driver_utility.py`). It's a bespoke **one-sided causal** kernel,
`car_prior.causal_predict` (`car_prior.py:137-188`):

```
Var_i(target) = sigma_i^2 + step_var * max(0, clock_target - clock_i)
w_i = 1 / Var_i   (only sessions with clock_i <= clock_target, or < for strictly_pre)
mu = sum(w_i y_i) / sum(w_i)
```

`step_var` (random-walk wander per round) comes from `layer2.pooling.fit_drift` fit over
the same causal subset. This differs from `DriftFit.predict` (symmetric, leaks future
sessions) specifically to stay causal.

So the answer to "per-weekend or only pooled": **both, combined**. The G1 car-ceiling for
round W is a causally-weighted blend of that constructor's own weekend-local session
estimates up to (and optionally including) W, with more distant/uncertain sessions
downweighted by the drift variance. The two knobs that decide how "weekend-local" a given
ceiling is:

- `strictly_pre=False` (the `characterize.py` path): includes the target weekend's own
  session estimate in the pool — the ceiling can be dominated by that weekend's own
  evidence when only one session is causal (`causal_predict` degenerates to that session's
  own `(value, sigma)` when there is only one row).
- `strictly_pre=True` (the production `#628` gate path, `build_driver_utility_observables.py`):
  **excludes** the target round itself by construction — explicitly to stop the target
  weekend's own driver performance leaking into its own yardstick (`driver_utility_observable.py`
  docstring, "Anti-circularity"). This ceiling is a **purely predictive prior built from
  every session before this one**, not "this weekend's data."

Net: the machinery supports a purely-weekend-local reference lap (Path A, session_fit's
own re-fit, no pooling at all — but not currently trustworthy per §1), a same-weekend
pooled reference lap (Path B, `strictly_pre=False`), and a causally-pooled
*excluding*-this-weekend predictive reference lap (Path B, `strictly_pre=True`, what's
actually shipped and gate-tested). All three are mechanically available; only the third has
a documented pass/fail validation result.

## 4. Scoped nulls — not inspected

- `src/physics/layer2/session_estimator.py` (the per-session five-view orchestrator
  `estimate_session` itself) — read only its caller (`estimate_batch.py`), not its body.
- `src/physics/layer2/estimate_store.py` / `estimate_store_fields.py` internals beyond
  the `effective_axis_sigma` reference in `driver_utility.py`.
- `scripts/pool_physics_estimates.py` and `scripts/run_sim_evaluator.py` bodies (only
  grepped their existence / read their evidence artifacts, not their source).
- `driver_utility_gate.py` beyond its module docstring and constants — did not read the
  gate computation body or re-derive the PASS verdict.
- `src/physics/terrain.py` (banking-angle source feeding `LateralView`/`car_prior`'s
  `bank_rad` handling) — took the callers' docstrings at face value.
- `src/physics/fit_store.py` (`params_from_record`, the store-hit reconstruction path in
  `sim_evaluator._reconstruct_from_store`) — read the caller, not the store schema.
- No code was executed; no tests were run; all claims above are from direct source
  reading only.
- Did not check `upgrades.yaml` / development-clock mechanics beyond the one-line mention
  in `car_prior.py`'s own docstring.
- Did not survey callers of Path A (`sim_evaluator.evaluate_session`) beyond
  `reports/physics/P1a_sim_evaluator_findings.md` and `scripts/run_sim_evaluator.py`'s
  existence — did not confirm whether Path A has been re-run/fixed since that report
  (dated to the #492 P1a milestone; no newer sim_evaluator report file was found in
  `reports/physics/`).
