# Implementer Handoff

## Gate
g2 — Side-by-side braking frontier (synthesis F_vehicle vs incumbent raw-speed) + the
gravity-corrected F_vehicle frontier metric → produce the deciding numbers for the retire/wire
decision. **Measurement only — no production wiring.**

## Task
Two deliverables:

1. **Build the decoupled-estimator adapter** (the reusable seam G3/G5/G6 will productionize).
   A function that, for a driver's flying laps, runs `estimate_longitudinal` **per lap over the
   contiguous classified KinematicSamples** (terrain θ/z from the #497 z-map), and emits per-sample
   `a_long`, `F_vehicle`, and `sigma_a` **aligned to the same KinematicSamples** the production
   views consume. This replaces the scattered per-braking-sample `clean_longitudinal_from_raw`
   call with a contiguous-arc 1-D estimate.

2. **Side-by-side braking frontier comparison.** Using the adapter + the G1-confirmed DEFAULT HPs,
   fit `BrakingView` two ways on a representative multi-session set and compare:
   - **(A) Synthesis F_vehicle frontier** (the new path): feed the gravity-free `F_vehicle/m` with
     `theta=0` + per-sample `sigma_a` into `BrakingView.fit`.
   - **(B) Incumbent** (today's production): `clean_longitudinal_from_raw` `a_long` + real θ
     (i.e. the existing `prepare_braking_frontier` path).
   Report per circuit: `(a_b, b_b)`, covariance, `raw_p99` knee, and the resulting capability
   ceiling. State a clear **retire/keep recommendation** with the deciding numbers.

## Protected Intent
The synthesis frontier must recover the deep braking knee (a_b higher / correct-sign b_b) WITHOUT
introducing ringing, and carry honest per-sample σ. Gravity must be counted **exactly once** — see
the de-conflation note below; double-subtracting g·sinθ is the trap. The adapter you build is
load-bearing for three downstream gates, so its contract must be clean and reusable.

## The gravity de-conflation — get this exactly right (the crux)
`BrakingView.fit(v, a_long, sigma_kin, theta, ...)` de-conflates measured decel to pure braking
capability via: `y = -a_long - drag(CdA) - theta_R - g*sin(theta)`.

- The estimator's **`a_long` output** = `F_vehicle/m - g*sinθ` (the actual on-track accel, same
  quantity the raw sensor and `clean_longitudinal_from_raw` produce). If you feed THIS with the
  **real θ**, BrakingView's `-g*sinθ` removes gravity correctly — equivalent to the incumbent but
  with the deeper knee. Gravity counted once. ✓
- The estimator's **`F_vehicle/m`** is already **gravity-free**. If you feed THIS, you MUST pass
  **`theta=0`** to BrakingView so it does NOT subtract gravity again (it's already gone). Then
  `y = -(F_vehicle/m) - drag - theta_R`, and the drag+rolling removal yields pure braking
  capability. Gravity counted once (inside the estimator, via the full z-map). ✓ — **this is the
  "F_vehicle frontier metric" (comment item 3): gravity handled by the estimator's per-sample z-map
  rather than BrakingView's local-gradient θ, so it is more accurate on hilly/altitude circuits.**
- **NEVER** feed `F_vehicle/m` with the real θ (that subtracts gravity twice) or `a_long` with
  `theta=0` (that never subtracts it). Either is a silent bug.

Variant (A) = the `F_vehicle/m` + `theta=0` path. Recommend it as the favoured input precisely
because gravity is handled once by the estimator's z-map (the Mexico/PER altitude finding from G1
shows terrain matters). The side-by-side quantifies whether (A) beats (B) on `(a_b, b_b)` + ceiling.

## Test Mode
Test-after. Add unit tests for the adapter's pure logic (per-lap estimate alignment, the
F_vehicle/m → BrakingView feeding with theta=0, the σ propagation) that run WITHOUT the FastF1
cache (synthetic samples). The side-by-side itself is a script + report (telemetry-driven).

## Close Criteria
- A reusable adapter exists (new function/module, e.g. `decoupled_braking_input.py` or a function
  in an existing layer2 module) with a clean contract: `(session, driver, ...) -> per-sample
  a_long/F_vehicle/sigma_a aligned to the classified KinematicSamples`, terrain θ/z from the z-map
  (loud `altitude_assumed_flat` when absent).
- A side-by-side report at `reports/physics/braking_sidebyside_2023Q.{json,md}` (gitignored) with,
  per circuit + both cars: A-vs-B `(a_b, b_b)`, covariance, `raw_p99` knee, ceiling, and which is deeper.
- A clear **retire/keep recommendation** (A favoured if it is at least as deep AND better-or-equal
  calibrated, with the terrain advantage on hilly circuits) with the deciding numbers.
- `py -m pytest tests/unit/physics/layer2/ -q` green; `py -m src.utils.simplification_limits` clean on touched paths.
- NO production view modified (measurement only).

## Allowed Scope
- New adapter module/function under `src/physics/layer2/`.
- A comparison script `scripts/braking_sidebyside_518.py` (or similar).
- `tests/unit/physics/layer2/` — adapter unit tests.
- `reports/physics/` (gitignored).
- You MAY add an `altitude_at_positions(px, py, profile)` helper to `terrain.py` mirroring
  `gradient_at_positions` (same nearest-centerline projection, returns `profile["altitude_m"][idx]`)
  — the adapter needs per-sample z, and only θ has a helper today.

## Specific Exclusions
- Do NOT modify `prepare_braking_frontier`'s production path, `session_braking`/`session_traction`/
  `session_coast`, `BrakingView.fit`, `clean_longitudinal_from_raw`, the `EstimateStore`, or
  `car_prior`. That wiring is G3. This gate is measurement only.
- Do NOT retire `clean_longitudinal_from_raw` here (that is the G3 decision-dependent step).

## Constraints
- `py` not `python`.
- `constraint:physics_region_no_evo_import` — no evo-region imports.
- `decision:two_cycle_external_anchor_design` — the estimator's anchor stays the TV-denoised RAW
  `a_long`; never re-read from a smoothed trajectory.
- Honest covariance: carry per-sample `sigma_a` into the frontier `sigma_kin` (do not broadcast a
  scalar where per-sample σ is available).
- One canonical path eventually — but here the adapter is ADDITIVE (no production switch yet).
- Physics model change → L1-L4 evidence (the estimator already has L1 `synthetic_step_recovery`;
  add adapter-level invariants).

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `decoupled_longitudinal.py` (`estimate_longitudinal`),
  `braking_view.py` (`BrakingView.fit`, `clean_longitudinal_from_raw`), `session_braking.py`
  (`prepare_braking_frontier`, `_driver_samples`, `_to_kinematic_samples`), `terrain.py`.
- **Capability:** physics capability-frontier measurement — the braking-frontier input.
- **Constraints:** `decision:two_cycle_external_anchor_design`; `constraint:physics_region_no_evo_import`.
- **Decision anchors:** `decision:smoother_rounds_braking_knee` — the retire caveat resolves via
  these numbers; `decision:decoupled_1d_longitudinal` — the wiring it gates.
- **Decision pressure:** retire/keep `clean_longitudinal_from_raw` — your report is the input to the
  human's decision (the Commander surfaces it; you do NOT decide it).
- **Evidence:** side-by-side `(a_b,b_b)`+cov+ceiling; gravity-corrected F_vehicle frontier metric.

## Exact seams (verified from source)
- `estimate_longitudinal(t, v, a_long_raw, regime, *, theta=None, z=None, mass_kg=MASS_KG, tv_lambda=0.10, sig_v=0.15, sig_a_brake=35.0, sig_a_other=4.0, sig_a_soft_brake=0.10, sig_a_soft_other=30.0) -> DecoupledLongitudinalResult(a_long, sigma_a, f_vehicle, a_soft_obs, is_brake, altitude_assumed_flat)`. `theta` (rad) and `z` (m) MUST be supplied together or both omitted. `f_vehicle` is in NEWTONS; `F_vehicle/m` (m/s²) = `f_vehicle / mass_kg`.
- `session_braking._driver_samples(session, driver, *, refine=False, cache=None) -> (processed_df, control_df, raw_xyz_laps, spd_d)`; `_to_kinematic_samples(processed, control) -> list[KinematicSample]` (each has `.timestamp_ms`, `.position` (x,y), `.speed`, `.regime`). The raw per-sample `a_long_raw` for the estimator comes from `clean_longitudinal_from_raw(spd_d["t"], spd_d["V"], sample_times_s) -> (v_at, a_long_at, sigma)` — this is the RAW sensor read the estimator's anchor is built from (NOT a smoothed trajectory; honors the anchor invariant).
- `braking_view.BrakingView.fit(v, a_long, sigma_kin, theta, *, cda_closed: ParamPrior, theta_R: ParamPrior, mass_kg, rho, prior: GaussianPrior2, ...) -> BrakingViewResult(a_b, b_b, covariance, ...)`. Use `cold_start_braking_supporting(cda_closed_mu=1.2, theta_R_mu=0.15)` for the supporting priors and `GaussianPrior2.cold()` for the (a_b,b_b) prior, matching `run_braking_view_on_session`.
- `terrain.build_terrain_profile(all_xyz_laps, min_laps=3) -> dict{distance_m, altitude_m, theta_rad, x_m, y_m, ...}`; `gradient_at_positions(px, py, profile) -> theta[]`. Add `altitude_at_positions` for z.
- `load_quali_session(year, gp, "Q", cache="data/telemetry") -> result` (`result[0]`=session, `result[1]`=rho).
- `MASS_KG` at `src.physics.longitudinal_fit.MASS_KG` (=808.0).
- FastF1 XYZ are in DECIMETRES — `_driver_samples` already returns metres-scaled processed telemetry, but raw `spd_d`/`pos_d` XYZ for the terrain profile need ×0.1 (the existing `prepare_braking_frontier` uses `_driver_samples`' xyz which is the raw pos stream — match its handling).

## Data Locations (absolute; main checkout)
- DB `C:/Programs/f1Brainz/data/f1_data_2023.db`; FastF1 cache `C:/Programs/f1Brainz/data/telemetry` (offline).
- Representative side-by-side set: **Bahrain, Monaco, Belgium, Monza, Singapore, Mexico × VER, PER**
  (RBR — the C1 reference; spans braking severity + flat/hilly/altitude). Expand if a circuit is ambiguous.
- Reports → `C:/Programs/f1Brainz/reports/physics/` (gitignored).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/ -q` (green) + `py -m src.utils.simplification_limits` (clean).
- The side-by-side report with the A-vs-B per-circuit table and the retire/keep recommendation + deciding numbers.
- A note confirming gravity is counted once in each variant (cite the de-conflation reasoning).

## Suggested Model Tier
Stronger (Opus) — the adapter is load-bearing for 3 downstream gates and the gravity-de-conflation
is a subtle correctness point; silent double-counting or mis-alignment must be avoided.

## Authority
- Scope/sequencing/verdict-producing decided by the user. Retire/keep is the user's call — you
  produce the numbers + recommendation, you do NOT decide retirement.
- You decide the adapter's internal contract + the side-by-side mechanics within scope.

## Stop Conditions
Stop and return if: the adapter cannot align the per-lap estimate to the classified samples; the
gravity-de-conflation cannot be made unambiguous; allowed scope must be exceeded; a production view
must be touched; required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g2-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence (with the KEY side-by-side numbers per
circuit: A vs B a_b/b_b/ceiling, which is deeper, terrain effect), the retire/keep recommendation,
assumptions, stop conditions hit, out-of-scope observations, and **Workflow Feedback**.
