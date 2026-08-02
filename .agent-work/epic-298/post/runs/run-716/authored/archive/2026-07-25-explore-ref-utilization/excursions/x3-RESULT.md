# x3 — Per-driver observables inventory: utilization + corner-type fingerprint

Question: what per-driver stores/observables exist today that could support (a) measuring
driver "utilization" of car capability at per-lap/per-corner/per-regime granularity, and
(b) a generalized per-driver corner-type fingerprint?

All row counts pulled live from the DBs under `C:\Programs\f1Brainz\data\` with the pinned
interpreter (`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`), 2026-07-24.
Read-only throughout — no writes to any DB.

## TL;DR ranking (best substrate first)

1. **`session_fits.apex_obs`** (`data/physics_fits.db`) — per-driver, per-session, per-corner
   `{v_apex, radius_m, a_lat, on_limit}` list. Best coverage (2019–2026 Q, ~3160 ok rows) at
   true corner granularity. Not yet paired against a car-capability ceiling per corner.
2. **`grip_bin_obs`** (`data/damage_integrals.db`) — per-driver, per-lap, per-32-bin-of-track-
   progress (~corner-phase resolution) friction/speed percentiles. Deepest volume (612,615
   rows) and includes stint/tyre-life/traffic context, but only 2023 (Q/R/S/SQ) + 2024 (R) —
   not full 2018–2026.
3. **`src/physics/utilization/*`** — the actual "utilization vs. car ceiling" machinery
   (Epic C1 #510, #628) is fully built and unit-tested: per-driver, per-**regime** (4 buckets:
   braking / slow_corner / fast_corner / straight) utilization ratio and absolute deficit
   against a causal (strictly-pre) car-capability ceiling, with proper pooling and a held-out
   falsifiability gate. **Code complete, but not run at scale** — no `driver_utility.db` or
   `driver_utility_observables.db` exists on disk today.
4. **`eph_residual.corner_json`** (`data/ephemeris.db`) — per-driver, per-lap, per-named-
   corner-segment transit time vs. ideal. Architecturally the cleanest "driver fingerprint"
   shape but a demo pilot only: 2,471 rows, single circuit (2023 Bahrain).
5. **`telemetry_store`** (`data/telemetry_store.db` + `data/telemetry_store_parquet/`) — the
   raw substrate everything above is derived from: 10–20 Hz per-driver X/Y/Z + Speed/
   Throttle/Brake/Gear/DRS, 894 sessions, 2018–2026, 2.6 GB compressed. Any new granularity
   is a fresh extraction pass over this.

Full detail below.

---

## 1. Physics estimate store (`data/physics_estimates.db`, table `session_estimates`)

- Code: `src/physics/layer2/estimate_store.py` (`EstimateStore`, `EstimateRecord`); read/reported
  via `scripts/pool_physics_estimates.py` → `src/physics/layer2/pool_driver.py`.
- **Granularity: session-level scalar, but pooled over the CONSTRUCTOR (both teammates), not
  per-driver.** Primary key is `(year, gp_name, session_type, constructor)`. The `drivers`
  column is a JSON list of the 1–2 drivers whose data fed the pooled fit (e.g.
  `["VER", "PER"]`), but the physics parameters themselves (drag area, braking/traction
  frontier, max power, lateral grip, coast) are fit jointly across both cars in that
  session — this is the **car ceiling**, not a driver-separated signal.
- Coverage: 1,597 rows total, **Q sessions only** (no R/FP/SQ), years 2019–2026:
  2019=210, 2020=170, 2021=220, 2022=220, 2023=220, 2024=240, 2025=240, 2026=77 (season in
  progress). `fit_status`: 1,562 `ok` / 35 `error`.
- Feasibility for driver-level utilization: **not directly** — it's the denominator (car
  ceiling), not the numerator. Driver-level signal is built on top of it by the
  `utilization/` package (§3).

## 2. Driver-utility layer (`src/physics/utilization/`) — purpose-built for this exact question

This package (Epic C1 #510, extended by #628) already implements "how much of the car's
capability did this driver extract" at **regime** granularity (4 track-position buckets that
tile a lap: `braking`, `slow_corner`, `fast_corner`, `straight`), not yet at individual-corner
granularity.

- **`car_prior.py`** — causal as-of car-capability ceiling: given the estimate store for one
  `(year, constructor)` and a target round `W`, builds a `PhysicsParameterSet` + covariance
  from sessions `round_idx <= W` (or `< W` in `strictly_pre` mode, which is the anti-leakage
  mode used downstream).
- **`regime_utilization.py`** (#510 G2) — pure function `regime_utilization(distance,
  curvature, v_real, v_ideal, ...)`: per-regime **ratio** `U_r = mean(v_real/v_ideal)` (≈1.0 =
  riding the ceiling), a consistency score (`1 − CV`), and THREE separately-tracked sigmas
  (MC envelope-uncertainty, lap-sampling SEM, and their quadrature combination). Explicitly
  documents the car/driver split as **impure** (`split_is_impure=True` always — the ceiling
  was itself fit from sessions this driver drove).
- **`driver_utility_observable.py`** (#628 G1) — same 4 regimes, but an **absolute deficit**
  `g = mean(v_ideal − v_real)` in m/s (never a ratio), computed against a **strictly-pre-round**
  causal ceiling specifically to avoid a driver's own lap leaking into their own yardstick.
- **`driver_utility.py`** (#628 G2) — pools G1's per-session per-axis deficits across sessions,
  per `(year, driver, constructor, axis)`, via `pool_random_effects` (DerSimonian-Laird
  random-effects, same mechanism used for cross-session physics params elsewhere) into a
  **teammate-relative** `delta` latent with explicit `resolved`/`unresolved` status
  (`MIN_RESOLVED_SESSIONS=3`). Writer: `write_driver_utility_db` → `data/driver_utility.db`
  table `driver_utility`.
- **`driver_utility_gate.py`** (#628 G3) — a genuinely falsifiable held-out validation harness:
  fits `delta` on TRAIN rounds, scores on disjoint HELD-OUT rounds (limb 1: RMSE improvement
  vs. car-only baseline; limb 2: centered cross-driver variance). Reports `honest_null` /
  `mixed` / `replicated` as a first-class outcome, not a pass/fail gate to game. The
  `straight` axis is explicitly flagged `confounded_negative_control=True` (the ceiling
  under-predicts straight speed — DRS/slipstream — so it never counts toward the verdict).
- **Batch builder**: `scripts/build_driver_utility_observables.py` — resumable CLI that builds
  ONE ceiling + ideal lap per `(constructor, round)`, computes G1 deficits per driver, writes
  tidy rows to `driver_utility_observables.db` table `driver_utility_observables`
  (`year, session_type, gp_name, round_idx, constructor, driver, axis, g_deficit, n_points,
  sigma_lapsampling, n_sessions_causal, error`).

**Coverage / status: code-complete and tested (per docstrings/gate), but I could not find
`data/driver_utility.db` or `data/driver_utility_observables.db` on disk** — this pipeline
has not been run at season scale (or was run and cleaned as an untracked/regenerable
artifact). Running the existing builder over the full `physics_estimates.db` + telemetry
store is a **rerun**, not new engineering, to get driver-level, regime-granularity
utilization for every Q session 2019–2026 (bounded by the underlying `session_estimates`
coverage above).

## 3. Per-corner apex observations, PER DRIVER (`data/physics_fits.db`, table `session_fits`, column `apex_obs`)

- Code: `src/physics/apex_extract.py` (`extract_apex_observations` → list of
  `ApexObservation(v_apex, radius_m, a_lat, on_limit, corner_index)`), invoked per-driver
  per-session inside `src/physics/session_fit.py` (`fit_driver`, around line 363) over that
  driver's flying laps (`processed`), then flattened into the `session_fits` row via
  `record_from_params` (`session_fit.py:99-142`).
- **Granularity: true per-corner, per driver, per session.** Verified content — VER's one Q
  session row carries 62 apex observations (multiple flying laps × ~15-20 corners), e.g.
  `{"v_apex": 20.03, "radius_m": 37.3, "a_lat": 10.76, "on_limit": false}`. `corner_index` is
  the ordinal within a lap traversal, **not a stable cross-session physical-corner ID** — apex
  events from different laps/sessions at "the same" physical corner are not pre-matched to
  each other; matching would need to go by `radius_m` bucket or lap-order alignment.
- Coverage: `session_fits` has 3,160 `fit_status='ok'` rows (plus 33 explicit failure rows:
  `no_accel_samples`/`no_laps`/`no_speed_stream`), **Q sessions only**, 2019=420, 2020=340,
  2021=440, 2022=440, 2023=440, 2024=479, 2025=480, 2026=154 — i.e. essentially every driver
  in every quali session across the whole tracked history.
- Feasibility: **computable now, no new extraction** for a corner-radius-binned driver
  fingerprint (bin `apex_obs` by `radius_m` per driver across many sessions to get an
  apex-speed-vs-corner-tightness curve — the natural "how does this driver handle slow vs.
  fast corners" signal). What's **missing** is normalization against the car's own capability
  at that radius (i.e., joining to `session_estimates`'/`car_prior`'s ceiling per corner) —
  raw `v_apex`/`a_lat` conflate car and driver exactly like everything else in this repo
  (documented `split_is_impure` caveat applies here too, just not labeled in this module).

## 4. Sub-lap grip-utilization bins, PER DRIVER PER LAP (`data/damage_integrals.db`, table `grip_bin_obs`)

- Code: `src/physics/layer2/grip_bin_obs.py`. Built for the tyre-wear/grip-decay "truth
  channel C4", not originally for driver fingerprinting — but the schema is directly usable
  for one.
- **Granularity: per (year, gp_name, session_type, driver, stint_num, lap_number, bin)**, where
  `bin` is one of 32 track-progress bins (`N_BINS=32`) restricted to corner samples
  (`a_lat > 3 m/s²`). Per occupied bin: `mu_comb_p90` (combined-slip friction utilization,
  p90 of `sqrt(a_lat²+a_long²)/g`), `mu_lat_p90`, `v_mean`, `n_samples`, plus per-row
  `compound`, `compound_c_number`, `tyre_life`, `mass_kg`, `gap_ahead_s` (traffic), and
  `is_last_stint_lap`/`follows_interruption` flags. `src/physics/layer2/corner_descriptors.py`
  already converts `(mu_lat_p90, v_mean)` → `(radius_m, lateral_g)` — i.e. there is already a
  converter from these bins into a corner-type (radius) axis.
- Coverage: **612,615 rows** — by far the largest observable found. But only
  `2023 Q=14968, R=184571, S=26913, SQ=7379` and `2024 R=378784`; **no 2018-2022 or 2025-2026,
  and no 2024 Q/FP**. 24 distinct drivers in the 2023 slice (full grid).
- Feasibility: this is sub-lap (finer than the 4-regime utilization layer, coarser than
  per-corner-instance apex extraction — 32 fixed bins per lap regardless of actual corner
  count/geometry). **Computable now** as a per-driver, per-corner-phase-bin fingerprint
  (mean/percentile grip utilization per bin per driver, trended across a stint for
  consistency), still needs pairing against a car ceiling to separate car from driver.
  Because bins are position-fraction-of-lap rather than corner-anchored, cross-circuit
  generalization (same "bin 14" ≠ same corner type at another track) needs the
  `corner_descriptors.py` radius conversion as the generalizing axis, not the raw bin index.

## 5. Ephemeris residuals with per-corner breakdown (`data/ephemeris.db`)

- Code: `src/physics/ideal_lap/residuals.py` + `src/physics/ideal_lap/ephemeris_store.py`
  (not read in depth — schema inspected directly).
- Tables `eph_state` / `eph_residual`, **PK-equivalent grain = per (run_id, year, gp, session,
  driver, lap)**. `eph_residual` carries `observed_lap_s, ideal_lap_s, residual_s,
  residual_se`, **and `corner_json`** — verified content: a list of per-track-segment
  `{start_m, end_m, transit_s}` dicts (15 segments for Bahrain — reads as one per named
  corner/straight sector). This is architecturally the cleanest "driver lost/gained time
  HERE, at a fixed car state" shape of anything found, because `residuals.py`'s own docstring
  states the residual "IS ... at a fixed car state, the driver signal."
  `eph_state` additionally carries `kappa_realized_lat/long` vs `kappa_cap_lat/long`
  (realized vs. capability curvature-derived accel) and `mgmt_discount_lat/long` — i.e. a
  driver-management-discount concept already named in the schema, per lap.
- Coverage: **thin — 2,471 rows across 3 `eph_runs`, all `(2023, Bahrain)`.** This reads as a
  demo/pilot slice for the ideal-lap-generator design doc
  (`docs/superpowers/specs/2026-07-05-ideal-lap-generator-ephemeris-design.md`), not a
  season-wide backfill. `residuals.py`'s own docstring scopes it to "race sessions only, for
  circuits the wear model has measured" (Q/FP explicitly deferred).
- Feasibility: the per-corner transit-time fingerprint shape already exists and is race-lap
  driver-level with a fixed-car-state control — but needs a real backfill pass (same
  `build_run`/`write_run` machinery, just run over more circuits/years) before it's usable as
  a general driver fingerprint, not a new design.

## 6. Per-driver, per-lap kinematic integrals (`data/damage_integrals.db`, table `damage_lap_integrals`)

- Grain: `(year, gp_name, session_type, driver, stint_num, lap_number)` — whole-lap scalar,
  not sub-lap. Carries `mean_corner_speed`, `grip_level`, `grip_n_samples`, plus a large set
  of tyre-damage integrals (`int_v`, `int_alat_abs`, `int_alat_sq`, `int_fzv`, and several
  "un"/"uen"-suffixed damage-unit variants — tyre-wear-oriented, not utilization-oriented).
- Coverage: 27,875 rows, `2023 Q=720/R=8715/S=1215/SQ=358`, `2024 R=16867`. Same season
  footprint as `grip_bin_obs` (built alongside it).
- Feasibility: usable now as a coarse per-lap driver utilization proxy (`mean_corner_speed`,
  `grip_level`) but adds nothing beyond what `grip_bin_obs` aggregated-per-lap would already
  give; not corner-type-differentiated.

## 7. Per-driver, per-stint physics fits during races (`data/race_stint_estimates.db`)

- Code: presumably `src/physics/layer2/race_stint_store.py` / `stint_estimator.py` (not read
  in depth). Grain: `(year, gp_name, session_type, driver, stint_num)` — **per-driver** (not
  constructor-pooled, unlike `session_estimates`), scalar per stint: lateral/traction/
  braking/power/drag/coast parameters + sigmas + covariances, `cumulative_track_laps`,
  `tyre_life_start/end`, `n_clean_laps`.
- Coverage: 7,840 rows, `R` sessions only, years 2019–2026 (roughly 800–1200/year, growing).
- Feasibility: this is a genuinely driver-separated (not team-pooled) physics-capability
  signal, but at stint/session granularity — same "session-level scalar" limitation as
  `session_estimates`, just per-driver instead of per-constructor. Not corner-level, but a
  candidate anchor if per-corner signal needs a driver-specific (not just constructor-pooled)
  denominator during races.

## 8. Related but NOT a driver fingerprint: `src/physics/wear/fingerprint.py`

- Named "fingerprint" but answers a different question: `corner_fingerprint()` characterizes
  what a **(circuit, corner)** IS as a tyre-wear sensor (apex/shed/gain speeds relative to
  local level, pit-reset refund, lap-to-lap noise, traffic sensitivity) — it groups internally
  by `(driver, stint)` for within-stint slope fits, but the fingerprint output is pooled
  across the field, not per-driver. Promoted from `scripts/corner_fingerprint.py`, spec
  `docs/superpowers/specs/2026-07-04-wear-model-productization-design.md`. Flagging so it
  isn't confused with a driver-conditioned fingerprint.

## 9. Telemetry store — the raw substrate (`data/telemetry_store.db` + `data/telemetry_store_parquet/`)

- Code: `src/data/telemetry_store.py` (`TelemetryStore`), per #541/PR #555.
- Grain: raw per-sample streams per driver per flying-lap-containing stint — `pos` (X/Y/Z
  decimetres) and `car` (Speed/Throttle/Brake/Gear/DRS) at native FastF1 rate (10–20 Hz),
  stored as zstd Parquet, one directory per session under `telemetry_store_parquet/<session_id>/
  {pos,car}.parquet`; SQLite side carries the session/driver/lap/weather index.
- Coverage: `tele_sessions`=894 (2018–2026, "all session types" per the module docstring —
  I did not independently break this down by year/session_type), `tele_drivers`=17,942,
  `tele_laps`=489,656, `tele_weather`=88,686. Parquet tree = 894 session directories, 2.6 GB
  total. Note: the legacy `tele_pos`/`tele_car` SQLite tables are vestigial (0 rows each) —
  the actual sample data lives entirely in the sibling Parquet files, not in those tables.
- Feasibility: this is the ultimate fallback — **any** new granularity (per-corner with a
  stable circuit-corner ID, per-sample capability comparison, whatever) can be recomputed
  from here via a fresh extraction pass (mirroring `apex_extract.py` or `grip_bin_obs.py`),
  since it is the fullest-coverage, highest-resolution store. It requires new extraction code
  to reach any of the higher-level shapes above for years/sessions those don't already cover.

---

## Feasibility verdicts by target granularity

| Target granularity | Verdict |
|---|---|
| **Per-lap driver utilization** (scalar corner-speed proxy per lap) | Computable NOW from `damage_lap_integrals` (`mean_corner_speed`, `grip_level`) or by aggregating `grip_bin_obs` per lap — but only for the 2023(+2024 R) footprint those stores cover. For the full 2019–2026 span, needs a rerun of the existing `grip_bin_obs`/`damage_lap_integrals` batch builders (not new engineering) or use of `race_stint_estimates`/`session_estimates` scalars (coarser, per-stint/session). |
| **Per-regime (4-bucket) driver utilization vs. car ceiling** | Code-complete (`src/physics/utilization/*`, Epic #510/#628) with a proper causal ceiling and a falsifiable held-out gate — but **not yet run/persisted at scale**. This is the most directly "utilization"-shaped existing pipeline; running it is the lowest-effort path to a real driver-utilization signal. |
| **Per-corner (individual apex/segment) driver utilization vs. ceiling** | Partially computable now: raw per-corner observations exist (`session_fits.apex_obs` 2019–2026 Q; `grip_bin_obs` 32-bin sub-lap 2023+2024 R; `eph_residual.corner_json` transit-time 2023 Bahrain pilot only), but **none of them is yet paired against a per-corner car-capability ceiling** in a persisted store — that pairing exists only at the coarser 4-regime granularity (§3 above). Building it would mean re-running the `driver_utility_observable` masking logic at per-corner-instance granularity (using `arcs.py`/`corner_descriptors.py` segmentation) instead of the 4 macro-regime masks — a moderate NEW pass over already-extracted intermediate data, not a from-scratch raw-telemetry extraction. |
| **Generalized per-driver corner-TYPE fingerprint** (radius-binned, cross-circuit) | Raw material exists and needs no new telemetry extraction: `session_fits.apex_obs` gives `(v_apex, radius_m, a_lat)` per corner per driver per session across nearly the whole tracked history (2019–2026 Q), and `grip_bin_obs` + `corner_descriptors.py` give a second, denser (but 2023/2024-only) route to the same `(radius_m, lateral_g)` descriptor pair. **No existing code aggregates either into a per-driver, car-normalized, cross-circuit corner-type curve** — this is a genuinely new analysis/aggregation pass, but one that consumes already-built, already-populated stores rather than raw telemetry. |

---

## Scoped nulls — what I did NOT inspect

- Did not read `scripts/build_physics_estimates.py` / the actual `EstimateStore` writer path
  (only the pooling/report script `scripts/pool_physics_estimates.py` and the store module
  itself) — coverage numbers above come from live DB queries, not from reading the builder.
- Did not read `src/physics/layer2/race_stint_store.py`, `stint_estimator.py`,
  `race_stint_batch.py`, or `ephemeris_store.py` bodies — schemas were inspected directly via
  `PRAGMA table_info`; row semantics beyond the column names are inferred, not confirmed by
  reading the build code.
- Did not read `src/physics/layer2/session_lateral.py`, `session_traction.py`,
  `session_braking.py`, `session_coast.py`, `power_drag_view.py`, `braking_view.py`,
  `lateral_view.py`, `coast_view.py`, `regime_readiness.py`, `regime_rollup.py`,
  `observability_router.py`, `mixture_stability.py`, `property_mixture.py`,
  `decoupled_*`, `tyre_separation.py`, `tyre_supplant.py`, `traffic.py`, `race_priors.py`,
  `damage_batch.py`, `damage_candidates.py`, `damage_scoring.py`, `damage_store.py`,
  `throttle_report.py`, `estimator_report.py`, `braking_report.py`, `lateral_report.py`,
  `coast_report.py`, `scoreboard.py` — the ~40 remaining `src/physics/layer2/*.py` files not
  named above were not opened; some may hold additional per-driver views not captured here.
- Did not inspect `src/physics/weekend_state/*` (frame/floor/gate_f6/gate_spec/holdout/
  layer2_evolution/layer3_fieldcar/layer4_car/model) at all.
- Did not confirm the `telemetry_store`'s 894-session breakdown by year or session_type
  (FP/Q/S/SQ/R split), nor whether all session types are represented for all years — took the
  module docstring's "894 sessions 2018–2026, all session types" claim from
  `[Telemetry store Parquet mirror]` project memory at face value rather than re-querying
  `tele_sessions` grouped by year/session_type.
- Did not check `data/f1_data_<year>.db` `session_classifications` coverage for years other
  than 2023/2024 (spot-checked those two only); did not inspect `race_start_order`,
  `weekend_entry_list`, `session_gap_weather`, `session_surface_features`, or
  `processed_telemetry` tables in the per-year DBs.
- Did not check whether `data/driver_utility.db` / `data/driver_utility_observables.db` exist
  under any worktree other than the current checkout, or whether they were ever built and
  subsequently cleaned (git-ignored per the module's own docstring, so no git history check
  was possible without more digging).
- Did not read `src/physics/layer2/pool_driver.py` (referenced by
  `scripts/pool_physics_estimates.py` but not opened).
- Did not examine `src/physics/ideal_lap/generator.py`, `pvat_writer.py`,
  `ephemeris_store.py`, or `wear_derate.py` bodies — only `residuals.py`'s docstring/header
  and the `ephemeris.db` schema were inspected.
