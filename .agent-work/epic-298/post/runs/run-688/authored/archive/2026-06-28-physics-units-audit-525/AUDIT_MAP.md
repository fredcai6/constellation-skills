# #525 G1 — Physics Unit-Convention Map (producer → consumer)

**Gate:** G1 evidence-only audit. **No code touched.** Every claim below is read
from source on branch `feat/physics-units-audit-525`. The architecture packet
(`docs/architecture/packets/physics.md`) was the starting index; each convention
claim was re-verified in the cited file.

## How to read this

Each channel lists every **producer** (writes a parameter) and every **consumer**
(reads it), with the **exact formula** and **unit** each side assumes. Two
distinct stores exist; conflating them is the #1 source of error, so they are
named explicitly throughout:

- **Layer-1 `FitStore`** (`fit_store.py`, written by `session_fit.record_from_params`)
  — the per-driver single-session fit. Lateral A0/A2 here are **m/s² (convention A)**.
- **layer2 `EstimateStore`** (`estimate_store.py`, written by `record_from_estimate`)
  — the five-view cross-session store. Lateral A0/A2 here are **g-units (convention B)**;
  longitudinal stored as raw physical `cda_closed` (m²) / `p_max` (W).

The two **lateral conventions**:
- **Convention A** (m/s²): `a_lat = A0·g_track + A2·ρ·v²`. A0 in m/s², ρ explicit in aero.
- **Convention B** (g-units): `μ_max(v) = A0 + A2·v²` (dimensionless grip coef), then
  `a_lat = μ_max·g·cos θ`. A0 dimensionless (~3.2 g), **no ρ**.

---

## Channel: LATERAL (A0, A2, ceiling, g_track, k_tire)

### Producer P-LAT-A — `LateralEnvelopeFit` (convention A, m/s²) — LIVE on the sim path
- **`src/physics/lateral_envelope.py:fit_envelope` (L21–139)**
- Model fitted: `a_lat = A0 + A2·ρ·v²` (m/s²). ρ baked into the design matrix:
  `x_fit = air_density * v_bins**2` (L88, L94).
- Output units: **A0 in m/s²**, **A2 such that `A2·ρ·v²` is m/s²**. Sets
  `g_track=1.0` (L136), `k_tire=config.grip_decay_prior_k` (L134, =0.01).
- Wrapped into `LateralParameters` at `lateral_envelope.py:131`.
- Driven by `ParameterEstimator` (`parameter_estimator.py:45` `self.lateral_fit = LateralEnvelopeFit`;
  call at L285). On insufficient samples falls back to `default_A0=30.0` / `default_A2=0.001`
  (`parameter_estimator.py:309–333`), which are **already convention-A m/s²**.

### Producer P-LAT-B — `LateralView` (convention B, g-units) — feeds the layer2 EstimateStore
- **`src/physics/layer2/lateral_view.py:LateralView.fit` (L78–161)**
- Model fitted: `μ_max(v) = A0 + A2·v²` (**dimensionless grip coefficient, g-units; NO ρ**).
  De-conflation: `μ_obs = |a_lat| / (g·cos θ)` flat, or the exact banked inverse (L139).
- Output units: **A0 g-units (dimensionless, ~3.2)**, **A2 in 1/(m/s)² g-units**
  (L50–51 field comments). Physical capability is `a_lat_max(v) = μ_max(v)·g·cos θ`
  (`a_lat_max`, L70–72; `g=9.81` default).
- Result type `LateralViewResult` (NOT a `LateralParameters`).

### Store write — layer2 `EstimateStore` (g-units passthrough)
- **`src/physics/layer2/estimate_store.py:record_from_estimate` (L261, L265)**:
  `A0=float(lat.A0)`, `A2=float(lat.A2)` where `lat` is the `LateralViewResult`.
  **Store columns `A0`/`A2` are g-units (convention B).** Per-session `rho` stored (L234).

### Conversion boundary — `car_prior._assemble_lateral` (B g-units → A m/s²)
- **`src/physics/utilization/car_prior.py:_assemble_lateral` (L423–521)**, the #522 patch.
- `s0 = G_MS2` (=9.81), `s2 = G_MS2 / air_density` (L483–484). `A0_param = A0_g·s0`,
  `A2_param = A2_g·s2` (L495–496). Covariance via Jacobian `J = diag(G, G/ρ)` (L485, L505).
- **ρ-cancellation is structural:** the producer's aero grip is ρ-independent (g-coef),
  but the consumer's formula hard-codes `A2·ρ·v²`, so the boundary divides ρ *back out*
  (`A2_param·ρ·v² = A2_g·G·v²` exactly, since the same `air_density` flows downstream, L455).
- **Defaults are NOT converted** (L511–514): `cfg.default_A0=30.0` / `default_A2=0.001`
  are already convention-A m/s² and pass through.
- Output: `LateralParameters(A0=A0_param, A2=A2_param, k_tire=0.0, g_track=1.0, ceiling=None)`
  (L519). Carries the explicit `# TODO(#525)` marker (L470–473).

### Shared consumer — `LateralParameters.lateral_capability` (convention A, m/s²)
- **`src/physics/physics_data_models.py:lateral_capability` (L237–249)**:
  `mechanical = A0·tire_factor·g_track`, `aero = A2·ρ·v²`, returns
  `min(mechanical+aero, ceiling)` (m/s²). `tire_factor = exp(-k_tire·tire_laps)` (L243).
  **ρ explicit. Expects A0 in m/s².**
- `ceiling` field (L211): tyre-saturation cap in **m/s²**; `None` when not saturating.

### Consumer — `PhysicsSimulator` (convention A, m/s²)
- **`_compute_speed_caps` (`physics_simulator.py:489–520`)**: `A0 = lateral.A0·g_track`
  (L497), `A2 = lateral.A2` (L498). Corner cap from `min(A0 + A2·ρ·v², ceiling)`;
  `denom = κ − A2·ρ` (L514). **ρ explicit.**
- **`_gsat_ceiling` (L465–487)**: fallback ceiling `car_lat = A0·g_track + A2·ρ·v_ref²`
  (L482). Population clamp `gsat_population_max_g·9.81` (L484, inline g).

### Consumer — `CapabilityEnvelope` (convention A, m/s²)
- **`capability_envelope.py:lateral_capability` (L97–99)**: delegates to
  `params.lateral.lateral_capability(speed, air_density)`.
- **`from_parameters` (L80–82)**: ceiling-trust test uses `lat.ceiling − lat.A0·lat.g_track`
  (m/s²). Built from a `PhysicsParameterSet`, so it inherits whatever convention fed the set.

### Consumers — apex / friction
- **`apex_extract._on_limit` (`apex_extract.py:161`)**: `lateral_envelope.lateral_capability(speed, air_density)`
  (convention A m/s²). `a_lat` documented m/s² (L11, L105).
- **`friction_coupling.py:36,57`**: `params.lateral.lateral_capability(speed, air_density)` (m/s²).
  (Legacy; superseded by `CapabilityEnvelope` per the module docstring L5–6.)

### Sampling — `physics_simulator._sample_parameters`
- **`physics_simulator.py:378`** perturbs an existing `LateralParameters` (A0/A2 jointly
  from covariance); **preserves whatever convention was on the input** (no conversion).

**LATERAL VERDICT:** Two producers in two conventions feed one m/s² consumer. The B→A
conversion is localized at `car_prior` (C1 path only). The legacy/sim path (P-LAT-A) is
natively convention A and needs no conversion.

---

## Channel: LONGITUDINAL / POWER (theta_D, theta_R, theta_P, p_max, CdA)

### Producer — `LongitudinalFit.fit_drag_throttle` (Layer-1)
- **`src/physics/longitudinal_fit.py:fit_drag_throttle` (L170–291)**
- Fits `a = P/(m·v) − 0.5·ρ·CdA_state·v²/m` (L188, design L254–260, `m=MASS_KG`).
- Converts to engine units: **`theta_D = CdA_closed / (2·MASS_KG)`** (L277–278) →
  unit **m⁻¹**. `theta_D_std = sqrt(var(CdA))·scale`. `power` is **total watts (W)**.
- `MASS_KG = 808.0` defined here (L44) — the canonical mass constant.

### Producer — `LongitudinalFit.fit_drag_rolling` (coast diagnostic, theta_R)
- **`longitudinal_fit.py:fit_drag_rolling` (L90–142)**: `−a_long = theta_R + theta_D·ρ·v²`.
  `theta_R` in **m/s²** (decel intercept). (theta_D from coast is NOT trusted; L9–13.)

### Producer — `LongitudinalFit.fit_power_trajectory` (theta_P)
- **`longitudinal_fit.py:fit_power_trajectory` (L293–341)**:
  `power_est = (a_long + theta_R + drag)·(v+eps)/throttle` (L316). Units (m/s²)·(m/s) =
  **W/kg (specific power, m²/s³)**. → `theta_P_values` is **specific power W/kg**.

### Producer — layer2 `PowerDragView` (feeds the EstimateStore)
- **`src/physics/layer2/power_drag_view.py:PowerDragView.fit` (L82–...)**
- Frontier `y = P_max/(m·v) − CdA·ρ·v²/(2m)` (L5, `wot_drive` L64–68; ρ explicit).
- Output: **`p_max` = engine power in total watts (W)** (L42), **`cda_closed`/`cda_open` =
  drag area m²** (L43–44).

### Store writes
- **layer2 EstimateStore** (`estimate_store.py`): `cda_closed=pd_.cda_closed` (m², L239),
  `p_max=pd_.p_max` (**W**, L253), `coast_theta_R=co.theta_R` (m/s², L267). NO theta_D —
  it stores raw `cda_closed`. So the store is in **physical units (m², W)**, not engine units.
- **Layer-1 FitStore** (`session_fit.record_from_params:88`): `cda = 2·MASS_KG·theta_D` (m²),
  plus `theta_D`/`theta_R` directly (engine units). Uses a **second `MASS_KG=808.0`**
  defined at `session_fit.py:57`.

### Conversion boundary — `car_prior._build_longitudinal` (#518 patch)
- **`car_prior.py:_build_longitudinal` (L325–353)**:
  `theta_D = cda_closed/(2·MASS_KG)` (m⁻¹, L346); `theta_R` passthrough (m/s², L348);
  **`theta_P = p_max/MASS_KG`** (W → W/kg, L344/L351). Covariance `/MASS_KG²` and
  `/(2·MASS_KG)²`. Bridge table at L30–47.

### Consumer — `LongitudinalParameters.drag_acceleration`
- **`physics_data_models.py:drag_acceleration` (L180–191)**: `theta·ρ·v²` (m/s²). **ρ explicit.**
  Uses `theta_D_open` when `drs_open` and set (L186–190); `theta_D_open` doc =
  `CdA_open/(2·MASS_KG)` (L144).
- `interpolate_power` (L174–178) and `max_power` (L193–198) read `theta_P_values` as W/kg.

### Consumer — `PhysicsSimulator` / `CapabilityEnvelope`
- **`physics_simulator._compute_drive_accel` (L452–463)**: `accel = power_scale/(v+eps) − drag − rolling`,
  `power_scale = mean(theta_P_values)` (L65). **theta_P consumed as W/kg.** `rolling = theta_R` (m/s²).
- **`capability_envelope._power_accel` (L102–107)**: `power/(v+eps) − drag − rolling`,
  `power = longitudinal.max_power` (W/kg).

**LONGITUDINAL VERDICT:** Convention-consistent *within each path*, but the EstimateStore
keeps RAW PHYSICAL units (m², W) while the consumer wants ENGINE units (m⁻¹, W/kg); the
two conversions (`/(2·MASS_KG)`, `/MASS_KG`) live at `car_prior`. The #518 watts→W/kg bug
was a missing `/MASS_KG`. `MASS_KG` is **defined twice** (`longitudinal_fit:44`, `session_fit:57`).

---

## Channel: BRAKING (a_b, b_b)

### Producer — `braking_fit.fit_braking_frontier` (Layer-1)
- **`src/physics/braking_fit.py:fit_braking_frontier` (L74–174)**: `decel = A_b + B_b·v²` (m/s²)
  on `−a_long` magnitudes (L89, L150–152). **a_b in m/s²**, **b_b in 1/m** (L47–49).
  `G_MS2=9.81` defined here (L36) but **unused in this file's math** (braking is pure m/s²).

### Producer — layer2 `BrakingView` (feeds the EstimateStore)
- **`src/physics/layer2/braking_view.py:BrakingView` (L31–...)**: `a_brake(v) = a_b + b_b·v²`
  (**m/s²**, L3). `to_braking_parameters()` (L53–54) emits a `BrakingParameters` **directly** —
  same units as the Layer-1 producer.

### Store writes
- EstimateStore: `a_b`/`b_b` from `BrakingView` (m/s², `estimate_store.py:243,245`).
- FitStore: `a_b`/`b_b` from `BrakingParameters` (m/s², `session_fit.py:93–94`).

### Consumer — `BrakingParameters.a_brake` / `CapabilityEnvelope.braking_capability`
- **`physics_data_models.py:a_brake` (L289–291)**: `max(0, a_b + b_b·v²)` (m/s²).
- **`capability_envelope.py:braking_capability` (L123–134)**: measured `a_brake(v)` when
  `b_b≥0`, else `braking_grip_ratio·lateral` (m/s²); clamped to `[0, max_braking_ms2]`.

**BRAKING VERDICT:** **Convention-consistent** — both producers and the consumer are m/s²
(a_b) / 1/m (b_b). No overload. (`G_MS2` is mis-homed here but unused locally.)

---

## Channel: TRACTION (a_t, b_t)

### Producer — `traction_fit.fit_traction_frontier` (Layer-1)
- **`src/physics/traction_fit.py:fit_traction_frontier` (L71–149)**: `a = A_t + B_t·v²` (m/s²),
  `b_t` clamped ≥0 (L123–129). **a_t in m/s²**, **b_t in 1/m** (L46–47). No ρ, no g.

### Producer — layer2 `TractionView` (feeds the EstimateStore)
- **`src/physics/layer2/traction_view.py:TractionView` (L39–...)**: `a_traction(v) = a_t + b_t·v²`
  (**m/s²**, L3, L41–42). De-conflation adds drag/rolling/gravity back:
  `a_drive_obs = a_long + CdA·ρ·v²/2m + theta_R + g·sin θ` (L16; ρ explicit in the *obs*, not the output param).

### Store writes
- EstimateStore: `a_t`/`b_t` from `TractionView` (m/s², `estimate_store.py:249,251`).
- FitStore: `a_t`/`b_t` from `TractionParameters` (m/s², `session_fit.py:95–96`).

### Consumer — `TractionParameters.a_trac` / `CapabilityEnvelope.traction_capability`
- **`physics_data_models.py:a_trac` (L329–331)**: `max(0, a_t + b_t·v²)` (m/s²).
- **`capability_envelope.py:_traction_grip` (L109–116) / `traction_capability` (L118–120)**:
  measured `a_trac(v)` ∩ power limit (m/s²), else `traction_grip_ratio·lateral`.

**TRACTION VERDICT:** **Convention-consistent** — both producers and consumer m/s² (a_t) /
1/m (b_t). No overload.

---

## Channel: COAST (rolling-resistance + coast-drag)

### Producer — layer2 `CoastView`
- **`src/physics/layer2/coast_view.py:CoastView.fit` (L75–...)**: from
  `decel_obs = −a_long − g·sin θ = θ_R + CdA·ρ·v²/(2m)` (L6–7). Output: **`theta_R` in m/s²**
  (L37), **`cda` (coast drag area) in m²** (L38). `coast_decel(v, ρ, m)` (L48–49) ρ explicit.

### Store write / consumer
- EstimateStore: `coast_theta_R` (m/s², `estimate_store.py:267`). The coast `cda` is a
  diagnostic cross-check vs `PowerDragView` CdA — **not** stored as a separate consumed param.
- `coast_theta_R` → `car_prior._build_longitudinal` `theta_R` (passthrough m/s²) → simulator
  `rolling` (m/s²). **No conversion.**

**COAST VERDICT:** Convention-consistent (m/s² / m²). Coast `cda` is diagnostic-only
(modern coast is regen-dominated, L9, L20). No overload introduced.

---

## Channel: TERRAIN (theta, z, banking)

### Producer — `terrain.build_terrain_profile` and the `*_at_positions` helpers
- **`src/physics/terrain.py:build_terrain_profile` (L21–124)**: emits `altitude_m` (**meters**),
  `grade` (**dimensionless dz/ds**), `theta_rad = atan(grade)` (**radians**, L119),
  `bank_rad` (cross-slope **radians**, NaN where unavailable, L120).
- `gradient_at_positions` (L372–390) returns θ in **radians**; `altitude_at_positions`
  (L415–437) returns z in **meters**; `banking_at_positions` (L393–412) returns φ in **radians**.

### Consumers
- `lateral_view`: `cos θ` and banked-inverse with `sin φ`/`cos φ` (radians) (L117, L136–141).
- `traction_view`/`coast_view`/`session_*`/`decoupled_longitudinal`: `g·sin θ` (m/s²),
  e.g. `session_estimator.py:95`, `session_traction.py:165`. z used as `mgz` potential energy
  in `decoupled_longitudinal` (`E_total = ½mv² + mgz`).

**TERRAIN VERDICT:** Convention-consistent — radians for angles, meters for altitude,
dimensionless grade. No overload. (Open known-limit: `decoupled_braking_input` passes
`theta=0` to BrakingView by design, Variant A — gravity counted once inside the estimator;
this is a documented modelling choice, not a unit ambiguity.)

---

## Shared constants (cross-cutting)

| Constant | Definitions found | Unit | Note |
|---|---|---|---|
| `MASS_KG` = 808.0 | `longitudinal_fit.py:44` (canonical), **`session_fit.py:57` (duplicate)** | kg | Two independent definitions; all layer2 imports the longitudinal_fit one. |
| `G_MS2` = 9.81 | `braking_fit.py:36` | m/s² per g | Defined in braking module, **unused there**, imported by `car_prior` (L82) for the *lateral* g→m/s² conversion. Mis-homed. |
| `g` = 9.81 (inline/local) | `lateral_view:70,86`, `braking_view:135`, `traction_view:80`, `power_drag_view:96`, `coast_view:88`, `decoupled_longitudinal:81 (_G)`, `physics_simulator:484 (inline)`, plus `_G` module consts in `lateral_report:21`, `session_lateral:18`, `session_braking:24`, `session_traction:27,165`, `session_estimator:95` | m/s² | ≥8 independent definitions of gravitational acceleration. |
| `DEFAULT_RHO` | `session_fit.py:58` (=1.20), config `reference_density_kg_m3` (=1.225) | kg/m³ | Two different fallback densities. |

---

## Producer/consumer matrix (one-line summary)

| Param | Producer(s) + unit | Store (unit) | Consumer + unit | Conversion seam |
|---|---|---|---|---|
| **A0/A2** | `lateral_envelope` (m/s², conv-A); `lateral_view` (g-units, conv-B) | FitStore: m/s²; EstimateStore: **g-units** | `lateral_capability`/`_compute_speed_caps`/`CapabilityEnvelope` (m/s², conv-A) | `car_prior._assemble_lateral` (B→A, #522) |
| **ceiling** | `lateral_envelope._detect_ceiling` (m/s²) | both: m/s² | `lateral_capability`/`from_parameters` (m/s²) | none (car_prior sets `None`) |
| **g_track** | `=1.0` everywhere | — | multiplies A0 (m/s²) | none |
| **k_tire** | `config.grip_decay_prior_k`=0.01 (Layer-1); `=0.0` (car_prior) | — | `exp(−k_tire·tire_laps)` | none |
| **theta_D** | `longitudinal_fit` `CdA/(2·MASS_KG)` (m⁻¹) | FitStore: m⁻¹; EstimateStore: stores **`cda` m²** | `drag_acceleration` `θ·ρ·v²` (m/s²) | `car_prior._build_longitudinal` `cda/(2·MASS_KG)` |
| **theta_R** | `fit_drag_rolling`/`CoastView` (m/s²) | both: m/s² | `_compute_drive_accel` rolling (m/s²) | none |
| **theta_P / p_max** | `fit_power_trajectory` (**W/kg**); `PowerDragView` `p_max` (**W**) | EstimateStore: **W** | `power_scale/(v+eps)` (W/kg) | `car_prior` `p_max/MASS_KG` (#518) |
| **CdA** | `fit_drag_throttle`/`PowerDragView` (m²) | EstimateStore: m² | (via theta_D) | `/(2·MASS_KG)` |
| **a_b/b_b** | `braking_fit`; `braking_view` (m/s² / 1/m) | both | `a_brake`/`braking_capability` (m/s²) | none (consistent) |
| **a_t/b_t** | `traction_fit`; `traction_view` (m/s² / 1/m) | both | `a_trac`/`traction_capability` (m/s²) | none (consistent) |
| **theta/z/bank** | `terrain` (rad / m / rad) | n/a (per-sample) | `g·sin θ`, `cos θ`, `mgz` | none (consistent) |

**Independently confirmed (the #522-blocking fact):** the live `sim_evaluator` /
`fit_batch` path does **NOT** route through `car_prior` and does **NOT** read the g-unit
EstimateStore. `fit_batch.run_batch → fit_driver → session_fit.fit_session_full`
(`session_fit.py:239` `ParameterEstimator.estimate_parameters` → `LateralEnvelopeFit`)
builds `LateralParameters` natively in **convention A m/s²**; `sim_evaluator.evaluate_session`
(`sim_evaluator.py:194–243`) calls `fit_session_full(...)` then
`PhysicsSimulator.simulate_lap(track_df, full.params)`. Only the **C1 utilization path**
(`characterize → car_prior.build_car_ceiling → CapabilityEnvelope → simulate_lap`,
`regime_utilization.py:508,579`) carries g-unit→m/s² conversion.
