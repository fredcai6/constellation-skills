# Data-pathway review: raw telemetry → lap ephemeris (2026-07-06)

Rigorous end-to-end review of the processing stream, audited against the intended road:
**(1) math correction (Matérn-7/2 filter) → (2) first physics pass (reliable accelerations +
quantified uncertainty) → (3) second physics pass (mass & compound corrections, first-principles
force allocation) → ephemeris {t, position, velocity, acceleration, mass, compound wear} with
covariance.**

Five parallel stage audits (ingestion, smoother, pass-1, pass-2, ephemeris build), every claim
carrying file:line evidence, spot-checked. This doc is the durable reference; it also serves as
source material for the planned full-pipeline explainer expansion.

---

## Verdict

The broad strokes ARE correct — every beat of the expected road exists in code, and two stages
are genuinely strong (ingestion is a faithful raw mirror; the smoother is a calibrated
Matérn-7/2 with full state covariance). But both stated fears are confirmed, with specific
line-level drop points:

1. **Known information is dropped at almost every seam.** Uncertainty is repeatedly computed
   honestly and then discarded exactly one call later. The single most representative fact:
   the decoupled braking filter's per-sample posterior `sigma_a` is passed into
   `BrakingView.fit` and never read — `fit_frontier(x, y, ...)` has no per-sample weight
   parameter at all (`frontier_fit.py:287-305`).
2. **The pass-1 → pass-2 transition is under-baked.** Exactly ONE quantity crosses the seam
   (the quali car envelope, as a centred point estimate, σ dropped). The k-prior seam built for
   this purpose is fed hardcoded literals. The race-stint views cold-start with flat priors
   even though the same car's quali posteriors sit in a store one query away — the injectable
   prior machinery exists on both sides and is simply not connected.

A third structural finding neither fear anticipated: **the pipeline is two parallel spines at
both pass 1 and pass 2, and the ephemeris consumes the older/weaker spine at each level.**

---

## Stage 0 — Ingestion (SOLID)

- The durable TelemetryStore (SQLite index + per-session zstd Parquet) stores FastF1's native
  per-stream messages **raw**: no merge, no resample, no interpolation; pos (~3.7 Hz) and car
  (~4-5 Hz) keep their own irregular grids (`telemetry_store.py:13-44`,
  `backfill_telemetry_store.py:160-161, 258-259`). Int downcasts are provably lossless;
  `session_time_s` forced float64 (`telemetry_store.py:322-349`).
- Channels dropped at ingestion have **no downstream consumer**: RPM, pos `Status`
  (OnTrack/OffTrack), wind/rainfall in tele_weather. Everything the physics side reads
  (X/Y/Z, Speed, Throttle, Brake, nGear, DRS, Pressure/AirTemp/Humidity, lap timing) is stored.
- The legacy row-store path (opt-in `--include-telemetry`) IS lossy (merge-interpolation +
  10× downsample) but is not the production path.
- **Friction, not loss**: per-lap Compound/TyreLife/FreshTyre/TrackStatus/sectors live only in
  the legacy `lap_times` SQL table (`schema.sql:30-50`), not the telemetry store — every pass-2
  consumer joins two stores with different keying. No single table holds the full weather set
  (tele_weather has Pressure but not Rainfall/TrackTemp; `sessions`/`weather` have the reverse).

## Stage 1 — Math correction (STRONG, with a mislabel and dead outputs)

- **Production is Matérn-7/2 (order=4), not 5/2.** Every live call site passes `order=4`
  (`session_fit.py:241`, `session_race.py:360`, `session_braking.py:100-101`); production
  entry-point defaults agree. `physics_adapter.py:7` ("Matern-5/2") and the arch-index note
  from #448 are stale.
- State per axis: [pos, vel, acc, jerk], white noise on jerk → differentiable acceleration.
  Production per-lap smoother is `NSStintSmoother`: anisotropic position noise, Student-t
  observation noise (auto-ν), curvature+|dv/dt| roughness bootstrap.
- HP calibration: chi²≈1-target grid+refine on interleaved held-out split
  (`_hp_search.py:164-200`), flying-window union (#538/#543). **Calibrated HPs are never
  persisted** — recomputed per run; only in-process caches exist.
- **Output covariance is GOOD at the adapter**: `smoother_to_processed_telemetry` emits the
  full 9×9 upper-triangle marginal state covariance per query (45 cov columns incl. pos-vel,
  pos-acc, vel-acc, cross-axis; `physics_adapter.py:107-129`). Dropped: jerk marginal + all
  jerk cross-terms (no slot in the 9-state map); cross-time covariance (expected).
- **Dead outputs**: the schema-v1 artifact writer (`artifact.py`) and trust profile
  (`grading.py`) have zero live consumers — package re-exports and tests only. The live path
  is 100 % in-memory DataFrames. The DB `processed_telemetry` table is likewise dormant.
- **Known-contaminated channels handled asymmetrically**:
  - `a_long` for regime classification: `np.gradient(speed_ms, t)` — bypasses the smoother's
    contaminated accel state (~15 m/s² stationary variance), but carries **no σ**, and the
    `KinematicSample.covariance` sitting next to it still describes the smoother's accel — the
    sample is internally inconsistent (`segment_classifier.py:47-53, 168-188`).
  - `a_lateral`: still reads the SAME contaminated 2-D accel state with no analogous fix or
    caveat (`segment_classifier.py:63, 158-166`).
  - Braking frontier: decoupled 1-D total-energy/force Kalman-RTS (honest per-sample
    `sigma_a = sigma_F/mass`) — WIRED as canonical (`session_braking.py:203-249`).
  - Traction/coast: raw `clean_longitudinal_from_raw`, scalar per-lap σ (honest nulls
    #523/#546 keep them there).
- `refine=True` (Student-t jerk prior + kind=3 raw anchor) is off by default in the library
  but `scripts/repopulate_g3wired_store.py` built the canonical `physics_estimates.db` WITH
  refine — the stored estimates carry the refined trajectory; the library default does not.
  kind=3 anchor σ is a hardcoded 0.5 floor (`accel_obs.py:47`, flagged "Open Q #3").
- Stale docstrings: `decoupled_longitudinal.py:68-69` + `decoupled_braking_input.py:27-30`
  still say "MEASURED-not-wired" — contradicted by `session_braking.py:213-214`.

## Stage 2 — First physics pass (GOOD ENGINE, LEAKY BOUNDARIES)

Parameter/uncertainty inventory (five views, shared cantilever `fit_frontier`, bootstrap 2×2
covariance n_boot=30, MAD-trimmed):

| View | Params | Cov treatment |
|---|---|---|
| Braking | brake_decel_ms2, brake_aero_decel_per_m | bootstrap + **diag-only** CdA/θ_R prior inflation |
| Traction | traction_accel_ms2, traction_aero_accel_per_m | same pattern |
| PowerDrag | max_power_w, drag_area_closed_m2 | conditioning-aware (analytic ridge cov on degenerate spans; floored when CdA<0.3) |
| Lateral | lateral_mech/aero_grip_g | bootstrap only (mass cancels) |
| Coast | rolling_decel, drag_area | pinball quantile, bootstrap |

Specific drops:
- **Per-sample σ dies at the fit boundary.** `fit_frontier` takes only (x, y): no weights in
  the kernel ridge, envelope loss, or bootstrap. Braking's honest per-sample sigma is stored
  as `sigma_obs` and never read (`braking_view.py:129-194`). The stored covariance is
  therefore *resampling variability*, not propagated measurement uncertainty.
- **Joint covariance dies at the pinning call.** `cda_prior_closed` returns marginal
  (μ, σ) only (`power_drag_view.py:70-79`); the (P_max, CdA) joint is discarded. b_b and b_t
  share the pinned CdA → genuinely correlated errors, structurally invisible in every store.
  Inflation is diag-only (`braking_view.py:180-182`, `traction_view.py:142-144`).
- **Store metadata inversion.** The NEW `estimate_store` drops n_samples/neff/bandwidth at
  `record_from_estimate` (`estimate_store.py:266-327`) and signals degeneracy by NULLing
  fields rather than a flag; the OLD `fit_store` persists a much richer reliability surface
  (chi2, sources, aero_identifiable, ceiling_trustworthy...). Neither store records assumed
  mass.
- **Old-engine mass bug.** `longitudinal_fit.py:44` bakes `MASS_KG=808.0` into the fit design;
  `session_fit.py:109` bakes it into every stored `drag_area_m2`. Wrong ~7 % for 2019-2021,
  no flag recorded. The layer2 path uses season-correct `quali_mass(year)` and is
  round-trip-consistent via `car_prior`.
- SYSTEMATIC_FLOOR 4 % nuisance floors are a flagged stopgap (#506)
  (`estimate_store.py:44-56`).

**Two independent fitting engines, three stores, no reconciliation:**
1. `fit_store` (per-driver) ← old `ParameterEstimator` (braking_fit/traction_fit/
   longitudinal_fit/lateral_envelope) → consumed by `ideal_lap/generator` + `sim_evaluator`.
2. `estimate_store` (per-constructor) ← five-view layer2 + CdA pinning → consumed by
   `car_prior` (C1) + `pool_driver`.
3. `race_stint_store` (per-driver-stint) ← stint_estimator age-decay reparameterization →
   consumed by the tyre stack.
Same physical session can hold two different braking/CdA answers; no production cross-check.

## Stage 3 — The pass-1 → pass-2 seam (UNDER-BAKED, as feared)

What crosses today:
- **Car envelope only, as a point.** `tyre_separation._car_offsets` reads the quali grip
  column, centres within session, subtracts as a fixed regressor; WLS weights use race-side σ
  only — quali σ read nowhere (`tyre_separation.py:261-275, 318, 353`).

What does NOT cross (but exists):
- **k priors**: `k_prior_mu=0.01, k_prior_sigma=0.02` hardcoded literals
  (`race_stint_batch.py:227-230`); never sourced from pooled posteriors.
- **View posteriors**: race-stint completeness views cold-start
  (`GaussianPrior2.cold()` σ=1e6, `_CDA0=1.2`, `_THETA_R0=0.15`;
  `stint_estimator.py:75-76, 677-687` — "no cross-view posterior to pin from") even though
  the same car's quali PowerDrag/Coast posteriors are in `estimate_store`. The injectable
  prior interface exists on BOTH sides; it is simply not connected across the seam.
- **Pass-1 σ of anything.**
- ρ is re-measured per race session (correct — physical condition, not a posterior).

Nature of the second pass: it never re-enters the trajectory level. Mass and compound enter
after smoothing, at the frontier-fit level (`stint_estimator._extract_kinematics`). Note the
evidence base: #523/#546 honest nulls showed pushing more physics into the trajectory filter
does NOT generalize (throttle/coast held on raw). Fit-level is a defensible architecture —
but only if pass-2 actually consumes pass-1 posteriors, which it currently doesn't.

## Stage 4 — Second physics pass (TWO SPINES; MASS = POINT COVARIATE)

- **Mass path**: pure a-priori model, no σ API anywhere (`mass_model.py`). Linear burn-down,
  measured SC_BURN_FRACTION=0.81, TEAM_OFFSETS empty. Enters: (a) mass-aware lateral decay
  `aero_scale=m_ref/mass` (de-biases fuel-burn drift leaking into k,
  `stint_estimator.py:520-534`); (b) traction drag term; (c) panel's single shared
  `age_mass` column (β_mass, additive). Never co-estimated; never uncertain.
  `RaceStintRecord` persists NO mass field — assumed mass unauditable from the store.
- **Wear spine A (promoted, feeds the ephemeris)**: CSV entry sweeps → per-corner panel
  (apex-speed observable; realized + capability κ; CR1 clustered covariance) → S×R ALS
  factorization + gauge-fixed factor covariance → `wear_model.db`
  (runs/cells/factors/cov). **`wear_model.db` and all input CSVs are untracked in git.**
- **Wear spine B (race-stint envelope decay)**: `race_stint_estimates` → `tyre_separation`
  (f_tyre vs g_track crossed model, PAVA monotone C-ladder, random-effects season pooling) →
  `tyre_supplant` cross-modal falsification (verdict CONTEXTUAL). Different observable
  (grip envelope vs apex pace), different units, never cross-validated in production against
  spine A.
- **Covariance discarded inside the panel**: `cluster_ols` computes the FULL CR1 covariance
  over all design columns — including the β_mass × per-compound-κ off-diagonals that encode
  exactly the fuel-burn↔age aliasing risk — and `_fit_core` extracts only `sqrt(diag(V))`
  (`panel.py:77-90, 237-313`). The shared-bias direction is invisible downstream.
- Burn-rate error aliasing: computed mass is ~linear in laps-into-stint, same axis as tyre
  age within a stint; a systematically wrong burn rate shifts β_mass and κ together —
  precisely the correlation the discarded off-diagonals would expose.

## Stage 5 — Ideal lap + ephemeris (POINT-ESTIMATE STORE WITH PLACEHOLDER σ COLUMNS)

Target contract vs `data/ephemeris.db` (`eph_state` + `eph_residual`,
`ephemeris_store.py:60-114`):

| Contract item | Status |
|---|---|
| t, s, x/y, v | ABSENT — `speed_profile`/`distance_profile` computed then discarded (`residuals.py:423-426`) |
| a_long/a_lat | ABSENT — `SimulatedLap` doesn't even return acceleration (`physics_data_models.py:456-463`) |
| mass | per-lap scalar; `mass_se` column hardcoded `None` (`residuals.py:413`) |
| compound/wear | compound + age + κ (capability/realized, both axes — Task 6) present; no absolute wear state; no κ σ columns at all |
| residual | present; `residual_se` hardcoded `None` (`residuals.py:432`) |
| covariance | ABSENT entirely |

Uncertainty discarded at identified points:
- FitStore covariance blobs loaded into `PhysicsParameterSet` then never used — `simulate_lap`
  always called `sample=False`; `monte_carlo_laps` exists but is only used by the separate
  C1/C2 utilization path (`generator.py:243-311, 555`).
- Wear cell se/se_cap inverse-variance-pooled to a POINT; pooled SE never returned
  (`wear_derate.py:134-262`).
- `source_versions_json` mass/smoother versions are admitted placeholders
  (`residuals.py:520-527`) — only wear_model_run_id is genuinely pinned.

Physics gaps in the build:
- **Banking silently absent**: `_banked_corner_cap` exists to re-apply fit-side de-conflation
  (#527) but the ideal-lap path never passes `bank_rad` — every ideal lap is flat-track
  (`generator.py:420-426`, `physics_simulator.py:547-551, 692-695`). Terrain grade/altitude
  likewise absent from `ideal_lap/*`.
- **Wrong-spine ceiling**: generator reads the OLD single-session fit_store (with its
  MASS_KG=808 drag bias), not the pooled covariance-bearing `car_prior`/EstimateStore ceiling.
  Zero cross-references between `ideal_lap/*` and `utilization/*` — two independent answers
  to "what is this car capable of."
- Fresh-tyre warmup magnitude dropped (boolean window only); derate touches A0/A2 but not the
  lateral grip ceiling (documented v1 limitations, `generator.py:75-98`).
- Only consumer today: `docs/pipeline/extract_bundle.py` (explainer). Terminal artifact.

## Cross-cutting: the two-spine problem

| Level | Spine consumed by ephemeris | Newer/covariance-bearing spine (not consumed) |
|---|---|---|
| Pass 1 ceiling | `fit_store` ← old ParameterEstimator | `estimate_store` ← five-view + pinning → `car_prior` |
| Pass 2 wear | `wear_model.db` ← CSV panel S×R | `race_stint_estimates` ← stint envelope decay → tyre_separation |

At both levels the covariance-bearing path is measured-not-wired into the final product.

## Branch/state anomalies

- `feat/fp-pilot-step1-deconfound` contains ONLY the docs/pipeline explainer delta vs main
  (all physics content already squash-merged via PR #585/#586). No deconfound work exists on
  it — repo-wide grep for "deconfound" hits only an archived #445 file. The branch name
  promises work that hasn't started.
- ~680 untracked files in the working tree including `wear_model.db`, `damage_integrals.db`,
  all panel/sweep CSVs, and a batch of scratch analysis scripts — the promoted wear store has
  no durable versioned home.

## Stale-doc ledger (quick fixes)

1. `physics_adapter.py:7` "Matern-5/2" → 7/2 (order=4).
2. `decoupled_longitudinal.py:68-69`, `decoupled_braking_input.py:27-30` "MEASURED-not-wired"
   → wired-canonical since #518 G3.
3. `accel_obs.py:47` σ_floor=0.5 hardcoded ("Open Q #3").
4. Arch-index #448 note says productionized 5/2.

---

# The plan (proposed 2026-07-06, pending user ratification)

Ordering principle: unify the spine first (everything downstream inherits it), then bake the
seam, then make uncertainty honest, then extend the ephemeris to the contract. Hygiene runs
parallel-cheap. Explainer expansion last (user-requested, lower priority).

**Phase 1 — One spine, one ceiling.**
Point `ideal_lap/generator` at the pooled covariance-bearing ceiling (`car_prior`/
EstimateStore); keep fit_store only for the power curve until power curves land in the
estimate path. Kills the MASS_KG=808 inheritance and the two-answers ambiguity. Add a
one-shot cross-check script (fit_store vs estimate_store per session) as a regression guard.

**Phase 2 — Bake the pass-1→pass-2 seam.**
(a) Pin race-stint completeness views from same-car quali posteriors (CdA, θ_R) via the
existing injectable-prior interface. (b) Feed k_prior from pooled compound-k posteriors
instead of literals. (c) Carry quali envelope σ into tyre_separation WLS weights
(1/(σ_race² + σ_quali²)). (d) Persist assumed mass (+ burn-rate source) on RaceStintRecord
and EstimateRecord. Explicit decision recorded: second pass stays FIT-level (trajectory-level
re-filter rejected on #523/#546 evidence) — "baked" means posterior-connected, not
trajectory-coupled.

**Phase 3 — Honest uncertainty through pass 1.**
(a) Per-sample weights in `fit_frontier` (braking's decoupled σ_a first; per-sample-ify
traction σ). (b) Keep the joint (P_max, CdA) 2×2 across the pinning call: full delta-method
inflation + persist pinned CdA (μ, σ) per record so cross-view correlation is
reconstructible. (c) Persist neff/n_samples/bandwidth + explicit degenerate flag in
estimate_store.

**Phase 4 — Ephemeris v2 (the contract).**
(a) Real σ sources: mass_se from a burn-rate/SC uncertainty envelope in mass_model; κ σ by
returning pooled SEs from wear_derate; residual_se via monte_carlo_laps over the ceiling
covariance blobs (already loaded, currently unused). (b) Per-lap covariance blob
{mass, κ_lat, κ_long, residual}; persist panel CR1 off-diagonals (β_mass×κ) in wear store.
(c) Persist the kinematic profile — t(s), v(s), a(s) (derivable), κ(s) — downsampled or
per-corner, with σ_v(s) from the MC. (d) Wire bank_rad/terrain into the ideal-lap track_df.
(e) Version/commit wear_model.db (or an exported run snapshot) so run pinning is real.

**Phase 5 — Hygiene (parallel, cheap).**
Stale-doc ledger above; persist calibrated smoother HPs per session; a_lateral contamination
decision (fix or flag); KinematicSample covariance inconsistency; branch rename/cleanup;
lap-metadata join friction (compound/track-status into tele_laps at next backfill, or
document the join as canonical).

**Phase 6 — Explainer full-pipeline expansion (user-requested).**
Restructure docs/pipeline from the five wear-centric beats into the full stream: ingestion/
store → smoother (the covariance story) → pass-1 five views + decoupled filter → the seam →
pass-2 mass/wear → ideal lap → ephemeris. The five stage audits behind this review are the
in-the-weeds source material.
