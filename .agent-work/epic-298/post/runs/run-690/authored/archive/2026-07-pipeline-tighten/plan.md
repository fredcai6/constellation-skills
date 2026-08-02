# Pipeline tightening — telemetry → ephemeris (epic plan, v2)

Executes the 2026-07-06 data-pathway review (`.agent-work/pipeline-review-2026-07-06/review.md`).
Goal: stop dropping known information at seams, bake the pass-1→pass-2 transition, and land an
ephemeris carrying {t, position, velocity, acceleration, mass, compound wear} with honest σ and
covariance. Branch: `feat/pipeline-tighten`.

**v2 (2026-07-06): every task verified against source by five independent plan-review passes;
~35 amendments folded in. One NEW pre-existing bug found during verification (Task 8). Task
numbering changed from v1 — do not cross-reference v1 numbers.**

## Decisions pending user ratification (execution gate)

- D1 **Ceiling becomes per-constructor** (Task 1): teammates share the pooled estimate-store
  ceiling; residual = driver vs the CAR. Default flip (`ceiling_source="estimate_store"`).
- D2 **Second pass stays fit-level** — no trajectory re-filter with mass/compound (per
  #523/#546 honest nulls); "baked" = posterior-connected. RATIFIED with user direction: the
  true trajectory-level second fit is deferred, NOT dropped — filed as an actioned research
  follow-up at closeout (Task 16).
- D3 **Pooled k-priors deliberately weakened** (2× σ, floor 0.02) to avoid laundering the
  #511 stint-length artifact back in. RATIFIED with user direction: pooled compound constants
  are LONG-TERM important (one of the few season invariants) and must not be neglected — the
  track-specific-wear confound is acknowledged; the long-term k-prior source should migrate to
  the DE-CONFOUNDED compound constants (tyre_separation f_tyre / S×R R-factors), filed as a
  follow-on at closeout (Task 16).
- D4 **PVAT = the MEASURED smoother trajectory** persisted into `processed_telemetry`
  (Task 10), joined to `eph_state` by natural key (year,gp,session,driver,lap) — this
  SUBSTITUTES for the review's Phase 4(c) "simulated ideal-lap v(s) profile with MC σ_v(s)";
  the measured state estimate is the honest ephemeris channel, the ideal profile is a model
  construct we can persist later if wanted. RATIFIED with user direction: exactly ONE
  trajectory store — Task 10 also retires the dead schema-v1 artifact writer
  (`preprocessing/trajectory/artifact.py`, zero live consumers) so no competing format lingers.
- D5 **residual_se via per-driver MC sensitivity grid** (age×mass, interpolated), not per-lap
  MC; 4×4 per-lap covariance blob is delta-method approximate. Adds ~288 simulate_lap calls
  per driver (~4-5× current per-driver sim budget for an ephemeris build).
- D6 **wear_model.db versioned as committed JSON run-snapshot** (`params/wear/`), and Task 12
  is explicitly sanctioned to read real `data/wear_model.db` and COMMIT the run-4 snapshot
  (goes beyond the schema-peek carve-out).
- D7 **Default flips ship ON**: Task 1 ceiling source; Task 3 quali pins + pooled k-prior in
  `populate_race_stints`. Both are the two-spine/seam fixes the review recommends.
- D8 **Backfill reality**: `data/physics_estimates.db` holds 2023 ONLY (220 rows) vs
  fit_store 2019-2026 (3193). Until the estimate store is backfilled, the new ceiling spine
  is live for 2023 and falls back elsewhere. Backfill runs are a closeout checklist item
  (see Wave 6), not a task.
- D9 **SINGLE CANONICAL PATHWAY (ratified 2026-07-06)**: this pipeline is THE pathway; no
  competing pathways or exploratory spurs survive the epic -- each is either (a) retired,
  (b) wired into the canonical path, or (c) explicitly documented as a non-competing role
  (e.g. wear spine B measures grip-envelope decay, spine A the pace-observable derate).
  Concrete rulings: backfill target = `data/physics_estimates.db` with the current
  (post-T6, refine-on) pipeline -- `physics_estimates_g3wired.db` retired after backfill;
  Task 16 gains a competing-pathway sweep producing a retire/wire/document verdict per
  spur (known list: old ParameterEstimator->fit_store engine [full retirement = dedicated
  follow-on issue; this epic confines it to power-curve + fallback roles], sim_evaluator's
  unconditional re-fit, grading.py trust profile (test-only), CoastView dead prior_theta_R param [RESOLVED by Wave-6 fixwave: param removed per D9], HPStore production wiring, ephemeris fit_store-fallback flip decision
  post-backfill, kappa_panel-vs-k_stint cross-validation diagnostic).

## Wave structure (parallel worktrees within a wave; merge between waves)

| Wave | Tasks | Ordering constraints honored |
|---|---|---|
| 1 | T1, T3, T5, T13 | disjoint files |
| 2 | T2, T4, T6, T14 | T4 after T3; T6 after T5 (rebase views); T4∥T6 verified independent (grip σ columns already exist in store); T4+T14 touch session_race.py in different functions — non-overlapping hunks |
| 3 | T7, T8, T10 | disjoint (wear files / physics_simulator / PVAT+session_race hooks) |
| 4 | T9, T12 | T9 after T1+T6+T7+T8; T12 after T7 (both wear/store.py) |
| 5 | T11 | after T9 (generator.py rebase; its own stated dependency) |
| 6 | T15, T16, final whole-branch review, controller backfill checklist | docs only |

Controller repopulation checklist (Wave 6, MANDATORY per user — "repopulate everything at
the end"): estimate-store backfill for all seasons (`scripts/backfill_estimate_store.py` — the canonical runner, replaces the deleted repopulate_g3wired_store.py; long-running, background batches; D9: full --refit rebuild so the whole store is one post-T6 refine-on vintage); `populate_race_stint_estimates` full
rerun (new provenance columns + pins live) — ORDER OF OPERATIONS (final review #4): run
scripts/migrate_race_stint_store_seam.py FIRST, then rerun with --refit, YEAR-ASCENDING so
each season's pooled k-prior can draw on the prior season's rows; wear `batch.py` full rerun (panel cov columns) +
`export_wear_run` + commit refreshed snapshot; PVAT export (size a full backfill first; at
minimum 2022-2026 race sessions, extend after size check); ephemeris rebuild (new run_id);
`extract_bundle.py` + `build.py` + republish explainer artifact.

## Global Constraints

- Python is `py` (Windows launcher). Tests: `py -m pytest tests/unit/physics tests/unit/preprocessing -x -q` (narrow to your task's test files first, then the affected package).
- `constraint:physics_region_no_evo_import`: nothing under `src/physics/` or `src/preprocessing/` may import evo-region packages. `src/preprocessing/` additionally NEVER imports `DatabaseManager` (read-only sqlite URIs only — packets/preprocessing.md:28-32).
- No FastF1 imports outside `src/data/` + the sanctioned physics seams. The DB/telemetry store is the data source.
- Unit conventions per `docs/architecture/reference/physics-unit-conventions.md`: `_g` = producer/store space, `_ms2` = consumer/sim space; conversions ONLY at the sanctioned `car_prior` seams. Lateral aero conversion is `×GRAVITY_MS2/ρ`, NOT `×GRAVITY_MS2` (car_prior.py:466-546).
- **Backward compatibility**: unless the task says otherwise, default call paths must be byte-identical (new behavior behind new optional params/columns with None/off defaults).
- Store schema changes: purely-additive `ALTER TABLE ... ADD COLUMN` guarded by `PRAGMA table_info` — mirror `scripts/migrate_lap_times_enrichment.py` / `scripts/migrate_sessions_round_num.py` (NOT the rename-shaped `migrate_physics_store_columns_525.py`); stores with self-healing `_ensure_*_columns` writers extend that mechanism instead of a separate script.
- NEVER write to `C:\Programs\f1Brainz\data\*` from a task (unit tests use tmp_path fixture DBs). Read-only peeks for schema ground truth allowed. Sole exception: Task 12's sanctioned run-4 snapshot export (D6).
- Work only inside your assigned worktree; edit only files on your task's ownership list; commit in the worktree with message suffix:
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`
- Match surrounding code style; comments only for non-obvious constraints.

---

## Task 1: Ideal-lap ceiling from the pooled estimate spine

**Goal:** `generator.py` reconstructs the car ceiling from the OLD per-driver `fit_store` row (`_load_fit_row`/`_ceiling_from_row`; `_std` hardcoded 0.0 at generator.py:264-265; MASS_KG=808.0 baked into stored drag via longitudinal_fit.py:44). Switch the capability side to `src/physics/utilization/car_prior.build_car_ceiling` (covariance-bearing, per-constructor), keeping fit_store ONLY for the power curve + fallback. **This task lands FIRST among the four generator.py tasks (1 → 7 → 9 → 11).**

**Verified ground truth:** `build_car_ceiling(*, store_df, year, constructor, target_round, strictly_pre=False, config=None) -> CarCeilingResult` (car_prior.py:553); `CarCeilingResult.params` IS a fully-populated `PhysicsParameterSet` with real `_std`/covariance (car_prior.py:126, 347-355, 404-406, 420-422, 543-546) — **no field mapping needed**, and outputs are already consumer `_ms2` space (do not convert anything).

**Changes:**
- `ideal_lap()` gains `ceiling_source: str = "estimate_store"` (| `"fit_store"`) and `estimate_db_path: str = DEFAULT_ESTIMATE_DB` (new constant mirroring `DEFAULT_FIT_DB`) plus an injectable `estimate_df` seam for tests (analogous to `fit_row`/`ribbon` injection).
- `_ceiling_from_estimate(...)`: constructor from the fit_store row (`FitRecord.constructor`, fit_store.py:33); `target_round` from `FitRecord.round_idx` (fit_store.py:30) — None/NaN round_idx → fallback; `strictly_pre=False` (session's own values feed its own ceiling — matches current semantics). Call `build_car_ceiling(...)` and use `.params` directly.
- Power curve: unchanged (`_power_curve_from_row` on the fit_store row).
- Fallback: missing/bad estimate row → `_ceiling_from_row` + `ceiling_source_used="fit_store_fallback"` on `IdealLapResult` (new field). `residuals.py`: `source_versions_json` gets an AGGREGATE `ceiling_sources` entry — a driver→source map (it is per-driver, the dict is run-level; a scalar is wrong).
- Reality note (D8): estimate store is 2023-only today; other years exercise the fallback until backfill.

**Ownership:** `src/physics/ideal_lap/generator.py`, `src/physics/ideal_lap/residuals.py` (threading + source aggregation only), tests. Do NOT touch `car_prior.py`; report BLOCKED if its API is insufficient.

**Acceptance:** synthetic tmp-path stores: (a) estimate path yields non-zero `_std` + covariance on the parameter set; (b) missing estimate row → fallback + flag recorded; (c) `ceiling_source="fit_store"` byte-identical to pre-change; (d) driver→source aggregation lands in source_versions. Existing ideal-lap tests green.

## Task 2: fit_store vs estimate_store divergence cross-check script

**Goal:** the two pass-1 engines can disagree with no production check. `scripts/compare_capability_stores.py` via public `FitStore.load_fits()`/`EstimateStore.load()`.

**Verified column mapping (use exactly this):**
- Comparable with real σ on both sides: `brake_decel_ms2`, `brake_aero_decel_per_m`, `traction_accel_ms2`, `traction_aero_accel_per_m` (fit-side σ = sqrt(diag) of the `braking_covariance`/`traction_covariance` JSON blobs; estimate-side `_sigma` columns).
- Lateral: fit-side `lateral_mech_grip_ms2`/`lateral_aero_grip_ms2` (already m/s², σ from `lateral_covariance` blob); estimate-side `lateral_mech_grip_g`/`lateral_aero_grip_g` (+`_sigma`) convert **mech: ×GRAVITY_MS2; aero: ×GRAVITY_MS2/ρ with ρ from the estimate row's own `rho` column** (car_prior's sanctioned Jacobian). A bare ×g on aero manufactures fake divergence.
- Drag: fit-side `drag_area_m2` has NO σ anywhere (confirmed) — compare vs `drag_area_closed_m2` normalized by the ESTIMATE-side σ alone, labeled `sigma_source=estimate_only` (do not fake a combined σ).
- Aggregation fit→constructor: UNWEIGHTED mean across the constructor's driver rows (σ absent for drag makes IVW non-uniform); handle N≠2 drivers gracefully.
- Output: per-session table (stdout CSV or `--out`), flag >2σ, summary median |Δ|/σ per param; `--fits-db`/`--estimates-db` args. Note in --help: estimate store currently 2023-only.

**Ownership:** `scripts/compare_capability_stores.py`, `tests/unit/physics/test_compare_capability_stores.py` (pure-function core tested on synthetic frames; one tmp-DB end-to-end).

## Task 3: Race-stint priors from the quali posterior (the seam, part 1)

**Goal:** race-stint fits cold-start (`_CDA0=1.2`/`_THETA_R0=0.15` at stint_estimator.py:75-76; k-prior literals at race_stint_batch.py:227-230). Connect the seam.

**Verified ground truth:** the pins that matter are the **`ParamPrior` scalars** passed as `cda_closed=`/`theta_R=` into `_try_braking` (stint_estimator.py:663-687) and `_try_power_drag` (690-712). The `GaussianPrior2.cold()` arguments there are separate output-pair MAP priors — DO NOT touch them. **CoastView's `prior_theta_R` is accepted and NEVER USED** (coast_view.py:79-135, pre-existing dead param) — pins genuinely affect Braking + PowerDrag only; file a follow-on issue for CoastView, don't assume it responds. `pool_random_effects(values, sigmas, *, sigma_floor=1e-9) -> PooledParameter` confirmed (pooling.py:41). `EstimateStore` has NO per-row getter — use `.load(year=year, session_type="Q", status="ok")` then filter `gp_name`/`constructor` in Python. `RaceStintData` has NO constructor field and the batch has no driver→constructor map — build one from the quali EstimateStore's `drivers` JSON-list column, mirroring `tyre_separation._driver_constructor_map` (tyre_separation.py:252-258). `StintEstimate` is `@dataclass(frozen=True)` (stint_estimator.py:160) built by BOTH `_skeleton_estimate` (773) and `_assemble_estimate` (800) — extend both factories together.

**Changes:**
- New `src/physics/layer2/race_priors.py`:
  - `quali_pins(year, gp, driver, estimates_db_path) -> RaceViewPins` — resolves constructor internally via the drivers-JSON map; returns `ParamPrior` fields `cda_closed`/`theta_R` (σ inflated ×1.5, module constant, race≠quali conditions) or None fields when no ok-row.
  - `k_prior(prior_stint_rows, compound, axis) -> (mu, sigma, source)` — pool PRIOR-season `race_stint_estimates` k via `pool_random_effects`; weaken `sigma = max(2*sigma_pooled, 0.02)`, clamp mu to [0, 0.05] (docstring: #511 k-ladder is substantially a stint-length artifact — guide, don't dictate). Fallback → literals (0.01, 0.02, source="literal_default").
- `stint_estimator.estimate_stint`: optional `view_pins: RaceViewPins | None = None` replacing the cold `ParamPrior`s in `_try_braking`/`_try_power_drag` when provided; default None = byte-identical. Extend `StintEstimate` (+both factories) with provenance: `k_prior_source`, `quali_pin_used`, `mass_kg_mean`, `mass_kg_start` (mass copied trivially from the stint's `RaceStintData.mass_kg` array — session_race.py:136 — threaded via the batch; NO `_extract_kinematics` changes).
- `race_stint_batch.populate_race_stints`: `estimates_db_path=None`, `use_quali_pins=True`, `use_pooled_k_prior=True` params; build the constructor map once per (year,gp); resolve k-prior per compound from prior-season rows of the SAME store it writes; thread pins + populate the new StintEstimate fields. CLI flags `--no-quali-pins`/`--no-pooled-k-prior`.

**Ownership:** `src/physics/layer2/race_priors.py` (new), `stint_estimator.py`, `race_stint_batch.py`, `scripts/populate_race_stint_estimates.py`, tests (new test_race_priors.py + extended stint tests).

**Acceptance:** pins-from-synthetic-store test (Braking+PowerDrag posteriors shift toward pin; Coast explicitly NOT asserted); no-row → cold path byte-identical; k-prior pooling/weakening/fallback; constructor-map resolution incl. driver-not-found → pins None.

## Task 4: Carry σ across the seam + persist provenance in the race store

**Goal:** `tyre_separation` WLS uses race-side σ only (`w = 1/st**2`, line 318) with the quali envelope as an exact point (`_car_offsets`, 261-275); the race store lacks mass/provenance columns. **Lands after Task 3 (same batch functions) — implementer must read post-T3 code fresh.**

**Verified ground truth:** quali grip σ columns ALREADY exist in `session_estimates` (`lateral_mech_grip_g_sigma`, `lateral_aero_grip_g_sigma`, `traction_accel_ms2_sigma`) and the loader is `SELECT *` (tyre_separation.py:595) — no Task 6 dependency. `k_prior_mu`/`k_prior_sigma` columns ALREADY exist in `race_stint_estimates` (race_stint_store.py:108-109, populated at 243-244) — do NOT re-add.

**Changes:**
- `tyre_separation._car_offsets`: read the σ column named by each `AxisSpec.quali_col` alongside the value; transform through the identical log/linear Jacobian; WLS weight becomes `w = 1/(base_sigma² + car_sigma²)`. Simplification (state in docstring): the session-mean centring's own uncertainty is IGNORED (averages ~10 constructors). Missing σ → weight unchanged; count exposed in the result summary.
- `race_stint_store`: FIVE new columns only — `mass_kg_mean`, `mass_kg_start`, `burn_rate_source`, `k_prior_source`, `quali_pin_used`. Additive migration `scripts/migrate_race_stint_store_seam.py` (ADD COLUMN + PRAGMA guard pattern). `record_from_stint_estimate` maps the new StintEstimate fields (from T3).
- `burn_rate_source` data path: `session_race.py` narrowly added to ownership — `RaceStintData` gains `burn_rate_source: str`; stop discarding `_burn_source` at session_race.py:979 (`resolve_race_burn_rate` already returns `(value, source)`). One field + one line.

**Ownership:** `tyre_separation.py`, `race_stint_store.py`, `race_stint_batch.py` (column population), `session_race.py` (the one field+line above ONLY), `scripts/migrate_race_stint_store_seam.py`, tests.

**Acceptance:** combined-σ weighting shifts WLS as expected on synthetic heteroscedastic quali σ; σ-missing fallback identical; migration idempotent (run twice on an old-schema tmp DB); round-trip all five columns; burn_rate_source lands non-null through the batch on a synthetic session.

## Task 5: Per-sample measurement weights in the frontier fit

**Goal:** `fit_frontier` (frontier_fit.py:287-305) takes only (x, y); braking's honest per-sample `sigma_a` is never read. Make the fit measurement-aware; `sigma=None` byte-identical.

**Verified ground truth:** fits are ALREADY deterministic (`seed: int = 0` default, frontier_fit.py:304; `_bootstrap_cov` uses its own `default_rng(seed)` at 238). `_envelope_loss` operates on the 60-node RIDGE, not samples — **per-sample weighting CANNOT enter there**; it enters ONLY via (a) `kernel_upper_ridge` weighted quantile and (b) bootstrap resampling; the envelope inherits transitively. `kernel_upper_ridge` sorts by **y** (`order = np.argsort(y)`, line 68) — sigma must be permuted by that same order. The existing `neff[i] = sw*sw/sum(w*w)` (line 79) is already the Kish form — combined weights flow through with NO separate change. Only THREE views call `fit_frontier` (Traction, PowerDrag, Lateral — Coast is pinball regression, coast_view.py:56-72); all need ZERO changes for byte-identity since sigma defaults None.

**Changes:**
- `fit_frontier(..., sigma: np.ndarray | None = None)`. Precision weights computed ONCE from the full sample: `w_i = clip((median(sigma)/sigma_i)**2, 0.1, 10)`; passed into every `kernel_upper_ridge` call (point estimate AND inside bootstrap draws) multiplied into the kernel weight after the y-sort permutation.
- Bootstrap: **branch** — sigma None/uniform keeps the literal `s = rng.integers(0, x.size, x.size)` (byte-identity trap: `rng.choice` with uniform p does NOT reproduce `rng.integers` draws); non-uniform weights use `rng.choice(n, size=n, p=w/Σw)`.
- `BrakingView.fit`: pass its per-sample `sigma_kin` slice (skip when `np.ptp(sigma)==0` — a broadcast scalar adds nothing). Other views: untouched.

**Ownership:** `frontier_fit.py`, `braking_view.py`, tests (test_frontier_fit*, test_braking_view*).

**Acceptance:** exact-equality regression (sigma=None → identical coef+cov, seed fixed); synthetic heteroscedastic test (5× noise variation — weighted fit recovers frontier with lower error); weighted-neff sanity; existing layer2 tests green.

## Task 6: Joint CdA covariance across the pin + persist fit-quality metadata

**Goal:** `cda_prior_closed` collapses the joint to a marginal; view inflation is diag-only; `record_from_estimate` drops n_samples/neff/bandwidth; degeneracy is NULL-signaled only; mass unrecorded. **Lands after Task 5 (rebase onto its views).**

**Verified ground truth:** class is `PowerDragResult` (power_drag_view.py:41). Its `covariance` already carries a real cross-term in the joint branch (analytic ridge cov, 126-131) and is legitimately diagonal in the pinned branch (108-111). **First-order, the CdA cross-sensitivity of the intercept is ~0** (a CdA shift moves the observable exactly along the v² design column — the linear fit absorbs it into the slope); real cross-terms arise only from bound-activation (`b≥0`) / envelope-partition effects and are NOT analytically derivable (bounded Nelder-Mead over a kernel-ridge target). `pd_degenerate` is already computed locally in `record_from_estimate` (estimate_store.py:297). Consumers (`utilization/car_prior.py`, `pool_driver.py`, `regime_readiness.py`) are column-name-driven — new columns are safe.

**Changes:**
- `PowerDragResult.joint_prior()` → (mu 2-vec, cov 2×2) for (P_max, CdA), replicating `cda_prior_closed`'s degenerate fallback guard (74-79) — degenerate → wide default prior, never a fake CdA=0 pin.
- View inflation: **numerical Jacobian** — refit at `cda.mu ± h` with bandwidth HELD FIXED at the selected value; `J = (coef₊ − coef₋)/(2h)`; `cov += outer(J,J)·cda.sigma²`. Expectation documented in code + tests: ≈0 (matching today's diag) on healthy sessions; non-trivial only near degenerate/bound-active fits.
- `estimate_store` new columns (additive, via the store's ensure/ADD-COLUMN pattern + migration script): `braking_n_samples/_neff/_bandwidth`, `traction_n_samples/_neff/_bandwidth`, `power_drag_n_samples/_neff/_bandwidth` (n_samples for power_drag = `n_closed`; neff scalar = `float(ff.neff.min())`, matching the `neff_floor` gate's own reduction — new field on the three Result dataclasses), `power_drag_degenerate` (store the existing local flag; keep NULLing behavior for pooling), `mass_kg_assumed` (from the existing `m = quali_mass(year)` at session_estimator.py:112, threaded via a new `SessionEstimate.mass_kg`). **No `pinned_cda_*` columns** — they'd duplicate `drag_area_closed_m2/_sigma` byte-for-byte under current wiring.

**Ownership:** `power_drag_view.py`, `braking_view.py`, `traction_view.py`, `session_estimator.py`, `estimate_store.py`, `scripts/migrate_estimate_store_metadata.py`, tests.

**Acceptance:** joint_prior degenerate-guard test; numerical-Jacobian test on a synthetic bound-active fit (off-diagonal changes) AND a healthy fit (≈ old diagonal); store round-trip of every new column; migration idempotent; consumer unit tests (car_prior/pool_driver/regime_readiness) green.

## Task 7: Mass σ model + wear SEs surfaced + β_mass×κ covariance retained

**Goal:** mass has no σ API; wear-cell SEs are pooled to points; the panel's β_mass×κ covariance is discarded before persistence.

**Verified ground truth:** NO calibration-residual spread exists anywhere to source σ_burn from (`season_burn_rate_estimate` collapses to the mean and discards spread, burn_rate_calibration.py:394-447; `session_fuel_features` has no spread column) — that branch is UNIMPLEMENTABLE without out-of-scope plumbing; drop it. `cluster_ols` returns only `(beta, sqrt(diag(V)), r)` — V is internal (panel.py:77-90). `wear_runs` has NO ensure-columns helper (unlike `wear_cells`'s `_ensure_wear_cells_columns`, store.py:92-111) and `write_run` is a hardcoded 7-column INSERT (124-136). `kappa_for_corner` has THREE call sites: generator.py:343 (owned here) + residuals.py:383-385, 393-396 (NOT owned — Task 9's).

**Changes:**
- `mass_model`: `race_mass_sigma(...)` — `σ_burn = 0.08 × burn_per_lap` UNCONDITIONALLY (named constant; `burn_rate_source` param informational only), integrated over laps-since-start; SC-fraction uncertainty ±0.05 absolute on non-green laps; quadrature. Plus `MODEL_VERSION` constant.
- `wear_derate`: `return_sigma: bool = False` flag on `kappa_for_corner` (and internals) — default returns floats byte-identically; `return_sigma=True` returns (κ, σ) with σ = max(IVW pooled SE, weighted between-cell std). generator.py:343 opts in and threads `kappa_lat_sigma`/`kappa_long_sigma` onto `IdealLapResult` (additive optional fields — precedent `corner_times`). residuals.py call sites UNTOUCHED (Task 9 migrates them). Known simplification (docstring): the S-factor-scaled branch (wear_derate.py:222-228) does not propagate S's own factor-covariance.
- `panel.cluster_ols`: `return_cov: bool = False` flag (both existing callers unmodified); `_fit_core` opts in and extracts `V[ix["age_mass"], ix[f"age_{c}"]]` per compound into `kappa_{c}_massbeta_cov` fields; `batch.py` pools a per-run `massbeta_kappa_corr_lat/long` (Fisher-z mean across corners) onto the run row.
- `wear/store.py`: new `_ensure_wear_runs_columns` helper mirroring the wear_cells one; `write_run` extended for the two new columns.

**Ownership:** `mass_model.py`, `wear_derate.py`, `generator.py` (line-343 opt-in + IdealLapResult fields only), `wear/panel.py`, `wear/batch.py`, `wear/store.py`, tests.

**Acceptance:** mass σ grows over stint + SC-lap test; κ σ: tight-cell-dominates and dispersed-cells tests; panel off-diagonal on NEAR-collinear synthetic data (exactly-collinear degenerates pinv+CR1) strongly negative; `return_sigma=False`/`return_cov=False` paths byte-identical; ensure-columns retrofits an old-schema tmp wear DB.

## Task 8: Fix Monte-Carlo traction sampling (pre-existing simulator bug)

**Goal (found during plan verification):** `PhysicsSimulator._sample_parameters` (physics_simulator.py:294-305) constructs perturbed parameter sets WITHOUT `traction=` — every MC draw silently falls back to the lateral-derived traction cap (`TractionParameters` is Optional-None, physics_data_models.py:435-442), i.e. a DIFFERENT physics model than the nominal lap. No `_sample_traction` exists (contrast `_sample_braking`, 401-434); `TractionParameters` isn't even imported (23-30). This invalidates any MC-derived σ (Task 9's critical path) and biases existing MC consumers (utilization C1/C2 path).

**Changes:** add `_sample_traction` mirroring `_sample_braking` (2×2 `traction_covariance` when present, else std-diagonal, else passthrough); forward `traction=perturbed` in `_sample_parameters`; import `TractionParameters`.

**Ownership:** `src/physics/physics_simulator.py`, `tests/unit/physics/test_physics_simulator*.py`.

**Acceptance:** MC draws carry `traction is not None` when the nominal has it; perturbed traction params vary across draws with covariance-consistent spread; nominal-lap behavior unchanged; draws with `traction=None` nominal unchanged (fallback preserved).

## Task 9: Populate ephemeris σ + per-lap covariance blob

**Goal:** `residuals.py` hardcodes `mass_se: None` (413) / `residual_se: None` (432); no covariance anywhere; ceiling covariance loaded then unused (simulate_lap always sample=False). **Lands after Tasks 1, 6, 7, 8.**

**Verified ground truth:** `_burn_source` is already resolved-and-discarded at residuals.py:313. The per-driver caching block (residuals.py:318-341) is the natural home for the MC grid. `ephemeris_store` already self-heals columns via `_ensure_eph_state_columns` on every write — extend that; NO separate migration script needed. `IdealLapResult` optional-field precedent: `corner_times`.

**Changes:**
- `mass_se` from Task 7's `race_mass_sigma` (thread `_burn_source` into it); `kappa_lat_se`/`kappa_long_se` new eph_state columns from Task 7's sigma flag — migrate the two residuals.py `kappa_for_corner` call sites (383-385, 393-396) to `return_sigma=True` here.
- `residual_se` via per-driver MC grid: `monte_carlo_laps` (n=48) at age {0,10,25} × mass {race start, race end} on the ceiling covariance (now real, Tasks 1+8); bilinear-interpolate `sigma_ideal(age, mass)` per lap; finite-difference `dLap/dmass`, `dLap/dkappa` from the same grid. Runtime note: ~288 extra simulate_lap per driver ≈ 4-5× current per-driver budget — acceptable, log timing.
- `eph_state.cov_json`: 4×4 over (mass_kg, kappa_lat, kappa_long, residual_s) — diagonal from the σ above; mass×κ from Task 7's pooled `massbeta_kappa_corr_*` scaled by the two σ; mass×residual and κ×residual via the grid sensitivities (delta-method). **PSD repair: eigenvalue-clip reconstruction** (eigh → clip negatives to 0 → reconstruct); store the repaired matrix; docstring marks the blob approximate-by-construction.
- `source_versions_json`: `mass_model_version` = `mass_model.MODEL_VERSION`; `smoother_version` = new constant in `src/preprocessing/trajectory/__init__.py` (Matérn order + calibration scheme tag).

**Ownership:** `residuals.py`, `ephemeris_store.py`, `generator.py` (MC glue only — derate section, not the ribbon section), `src/preprocessing/trajectory/__init__.py` (constant only), tests.

**Acceptance:** synthetic end-to-end: all σ columns non-null; cov_json symmetric + eigvalsh ≥ −1e-9 post-repair; grid-interpolation unit test; zero-covariance ceiling → residual_se≈0.

## Task 10: Persist the PVAT trajectory product

**Goal:** the smoother's per-sample state + full covariance (`smoother_to_processed_telemetry`, 45 `cov_i_j` columns) is discarded after each fit; the DB table `processed_telemetry` (src/data/schema.sql:132-157) is dormant (zero callers of `insert/get_processed_telemetry` — confirmed). Persist the MEASURED trajectory as the ephemeris kinematic channel (D4).

**Verified ground truth:** current table has Cartesian px..az + DIAGONAL sigmas only — needs SEVEN new columns: `s_m`, `v_ms`, `a_long_ms2`, `a_lat_ms2`, `sigma_v`, `sigma_a_long`, `sigma_a_lat`, plus `cov_v_along` (8). The velocity-frame delta-method projection needs exactly `cov_{3,4,6,7}` pairs — all present among the stored 45 (indices: v=(vx,vy)=(3,4), a=(ax,ay)=(6,7); z-axis contributes zero). `insert_processed_telemetry` (_telemetry_store.py:32-91) does NOT accept the adapter's output shape — the writer does real mapping work. **Writer lives in PHYSICS, not preprocessing**: `src/physics/ideal_lap/pvat_writer.py` — preprocessing NEVER imports DatabaseManager (packets/preprocessing.md:28-32, read-only URIs only); physics already has the import precedent (fuel_features.py:170).

**Changes:**
- Extend `processed_telemetry` schema additively (+ `insert_processed_telemetry` accepts the new fields).
- `src/physics/ideal_lap/pvat_writer.py`: `write_lap_pvat(db, processed_df, keys, downsample_hz=None)` — a_long/a_lat = tangential/normal projections of the smoother accel state (docstring: this is the 2-D state channel with its honest σ; the decoupled braking product is a separate fit-side signal); σ + cov_v_along via the (3,4,6,7) Jacobian.
- Opt-in hook threaded through the FULL 4-hop chain: `load_race_stints` → `_prepare_fitted_laps` (session_race.py:876-912) → `_fit_driver_laps` (622-684) → `_fit_clean_lap_row` (567-619, where the adapter df exists at 602) — `pvat_db=None` default at every hop; year/gp/session keys threaded down to the writer (currently stop at `_fit_driver_laps`).
- CLI `scripts/export_pvat.py --year --gp --session --db`.
- **Single-store mandate (D4)**: retire the dead schema-v1 artifact path — delete `src/preprocessing/trajectory/artifact.py`, its package re-exports (`src/preprocessing/__init__.py`, `src/preprocessing/trajectory/__init__.py`), and its tests (`test_artifact_roundtrip.py`; keep `grading.py`/trust-profile — diagnostic, not a store). Verified zero live consumers. Task 16 reconciles the map + retires `docs/report_schemas/trajectory_trust_profile.md`'s artifact-schema half if applicable.

**Ownership:** `src/data/schema.sql`, `src/data/database/_telemetry_store.py`, `src/physics/ideal_lap/pvat_writer.py` (new), `src/physics/layer2/session_race.py` (hook threading only), `scripts/export_pvat.py`, tests.

**Acceptance:** tmp-DB round-trip exact; Jacobian projection vs hand-computed rotation of a diagonal cov; default path writes zero rows.

## Task 11: Wire terrain banking into the ideal lap

**Goal:** `_extract_track_profile` reads `bank_rad` (physics_simulator.py:692-695) and `_banked_corner_cap` exists (def at 541), but `_track_df_from_ribbon` (generator.py:420-426) emits only distance/curvature/drs — ideal laps are flat-track. **Lands after Task 9 (last generator.py task).**

**Changes (amended join mechanism):**
- Use the codebase's established POSITION-BASED join, not distance interp (terrain and ribbon derive arc-length independently — a distance join can silently misalign banking): `terrain.banking_at_positions(px, py, profile)` (terrain.py:419-438; the pattern session_lateral.py:43 / session_traction.py:78 / stint_estimator.py:922-933 already trust). `ribbon.build_ribbon`'s dict already carries `px`/`py` (X_med/Y_med, ribbon.py:142) — currently discarded by `_track_df_from_ribbon`; use them.
- Terrain computed ONCE per (year, gp) — new injectable `terrain: Optional[dict] = None` param on `ideal_lap()` threaded like `ribbon`; `residuals.py` builds it once before the per-driver loop (pooled-XYZ, the established pattern), passes it down.
- NO slope/grade column — `_extract_track_profile` consumes only distance/curvature/drs/bank_rad (verified); drop the conditional.
- Missing terrain → no bank_rad column → NaN fallback, byte-identical to today; log once.

**Ownership:** `generator.py` (ribbon/track_df section), `residuals.py` (once-per-gp terrain build), tests.

**Acceptance:** synthetic banked-corner test — lateral cap rises vs flat, magnitude consistent with `_banked_corner_cap`'s formula; no-terrain path byte-identical; a MISALIGNMENT guard test (banking attached at the correct s-position via the position join, not shifted).

## Task 12: Version the wear model (committed run snapshot)

**Goal:** `data/wear_model.db` is untracked; promoted runs need a committed home (params/gold precedent confirmed: params/gold/compound_prior/, runtime_bundles/). **Lands after Task 7 (both touch wear/store.py).**

**Verified ground truth:** the loader is `store.load_model(db_path, run_id=None)` (store.py:172-226) — NOT in wear_derate.py; both real callers (`generator._resolve_wear_model` at 394-413, `residuals.build_ephemeris` at 466-474) go through it, so the fallback lives INSIDE `load_model` with zero caller changes. `sqlite3.connect` silently CREATES a missing file — check `Path(db_path).exists()` BEFORE connecting, don't catch-after. Run 4 confirmed latest (2019-2026, created 2026-07-05). `wear_cells` is already summary-only — export it whole.

**Changes:** `scripts/export_wear_run.py --run-id N` → `params/wear/wear_run_<N>.json` (deterministic key order); `load_model` DB-first (existence-checked) → newest snapshot fallback + explicit snapshot-path arg; export + COMMIT run 4 (sanctioned real-data read, D6).

**Ownership:** `scripts/export_wear_run.py`, `src/physics/wear/store.py`, `params/wear/`, tests.

**Acceptance:** WearModel-from-DB == WearModel-from-its-snapshot round-trip; missing-DB → snapshot fallback WITHOUT creating an empty db file; run-4 snapshot committed and loads.

## Task 13: Stale-doc and known-inconsistency hygiene batch

All four citations verified exact. Changes (comments/docstrings only, no behavior):
1. `physics_adapter.py:7` "Matern-5/2" → Matérn-7/2 (order=4 is production).
2. `decoupled_longitudinal.py:68-69` + `decoupled_braking_input.py:27-30` — "MEASURED-not-wired" → wired-canonical since #518 G3 (braking only; throttle/coast on `clean_longitudinal_from_raw` per #523/#546).
3. `segment_classifier.py` — (a) a_lateral (158-166): note it reads the 2-D smoother accel state; lateral projection trusted per #496, asymmetry deliberate, σ semantics unreviewed; (b) `_extract_covariance` (168-188): note the covariance describes the smoother state, NOT the `np.gradient` a_longitudinal beside it.
4. `docs/architecture/index.md` line 28 (#448 entry): append "(production later moved to Matérn-7/2, order=4 — 2026-07-06)". packets/preprocessing.md:17 already says 7/2 — index lags packet.

NOT in scope (follow-on issues, controller files them): `accel_obs.py:47` σ_floor=0.5 (code change, Open Q #3); CoastView dead `prior_theta_R` param (Task 3 finding).

**Ownership:** exactly those four files. **Acceptance:** test collection green; diff contains no executable-code changes.

## Task 14: Persist per-session smoother HP calibration

**Goal:** `calibrate_session_hp` (_smoother_fit.py:441-503) recomputes the chi²-target search every run. Persist per session.

**Verified ground truth:** `SmootherHP` fields (416-435) all plain float/int/None — serializable. Production callers reach it via the `calibration.py` facade re-export (59-73) — no facade edit needed. `session_fit` calls from `_calibrate_hp_for_driver` (222, call at 239-243), SHARED by `fit_driver` (333) and `fit_session_full` (464) — thread the opt-in through `_calibrate_hp_for_driver`. `session_race._calibrate_driver_hp` (324, call at 357-362). Injectable-path + tmp-DB test discipline matches every existing store.

**Changes:** `src/preprocessing/trajectory/hp_store.py` (new; `data/smoother_hp.db` default, path-injectable) keyed (year,gp,session_type,driver,order,calibration_scheme_tag) → SmootherHP fields + chi2 + created_at + code_version; `calibrate_session_hp(..., hp_store=None, session_key=None)` — hit returns stored, miss searches then stores, None default byte-identical; opt-in threaded through `_calibrate_hp_for_driver` + `session_race._calibrate_driver_hp`. Scheme tag incorporates order + flying-window-union flag.

**Ownership:** `hp_store.py` (new), `_smoother_fit.py`, `session_fit.py`, `session_race.py` (calibration seams only), tests.

**Acceptance:** round-trip + hit/miss on tmp DB; second call hits cache (monkeypatch `fit_stint_hp` to raise → proves no re-search); default path unchanged.

## Task 15: Explainer — full-pipeline expansion

As v1, unchanged in substance: restructure `docs/pipeline/` from five wear-centric beats to the full stream (ingestion/Parquet mirror · Matérn-7/2 smoother + covariance · decoupled filter · five views + CdA pin · stores/ceiling · the SEAM as now built · mass σ · wear pass (condensed) · ideal lap + banking · ephemeris state/PVAT/covariance · versioning/guards); mine `.agent-work/pipeline-review-2026-07-06/review.md` for the in-the-weeds prose; extend `extract_bundle.py` for new real numbers (per-field graceful degradation when stores lack refreshed runs); regenerate bundle + explainer. **Ownership:** `docs/pipeline/*` only.

## Task 16: Architecture-map reconciliation (mandatory closeout)

The repo's convention (docs/DOCUMENTATION.md:25; unbroken "Reconciled" chain in index.md) requires it. Reconcile for: new modules `layer2/race_priors.py`, `ideal_lap/pvat_writer.py`, `preprocessing/trajectory/hp_store.py`; new committed artifact class `params/wear/`; extended `processed_telemetry` (now LIVE — the dormant-table note in packets/data.md and the open structural question about the unwired artifact boundary both change); `physics→data` edge evidence (pvat_writer imports DatabaseManager); the ceiling-source change in ideal_lap (packets/physics.md); new estimate/race-store columns (packet prose). Run `py scripts/check_arch_map.py` green. Follow-on issues filed: accel_obs σ_floor; CoastView dead param; estimate-store backfill epic; **true trajectory-level second pass (mass/compound in the filter) — deferred research follow-up (D2, user-directed)**; **k-prior source migration to de-confounded compound constants (f_tyre / S×R) — long-term (D3, user-directed)**; artifact.py retirement map cleanup (D4).

**Ownership:** `docs/architecture/**` (packets, index, overlays as needed).
