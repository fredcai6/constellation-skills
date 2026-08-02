# #525 G1 — Overloaded-Term Dispositions + Recommendations

**Gate:** G1 evidence-only. **I recommend; I do not decide.** The canonical-convention
call and the in-scope-vs-routed split are ruled by the human at the decide-fix checkpoint.
North star (`PROBLEM_STATEMENT.md`): **de-overload / disambiguate — NOT unitless-as-dogma.**
Labelling the variables (unit-suffixed names + co-located headers) is the primary fix;
mechanical unit-philosophy is secondary.

Disposition values: **fix-local** (do it in this run's G2) · **route-out** (separate issue)
· **decide-at-checkpoint** (depends on the canonical-convention ruling).

---

## Overloaded / ambiguous term inventory

### OT-1 — Two lateral conventions for `A0` / `A2` (the headline overload)
- **Where overloaded:** the same field names `A0`/`A2` mean two different things.
  - `lateral_view.py` (`LateralViewResult`) and the **EstimateStore `A0`/`A2` columns**:
    dimensionless **grip coefficients, g-units** (`μ_max = A0 + A2·v²`, no ρ).
  - `LateralParameters.A0`/`A2`, `lateral_envelope.py`, `physics_simulator`,
    `CapabilityEnvelope`, the **FitStore `A0`/`A2` columns**: **m/s²** (`a_lat = A0·g_track + A2·ρ·v²`).
- **Evidence:** `lateral_view.py:50–51,66–72` (g-units) vs `physics_data_models.py:237–249` +
  `physics_simulator.py:497–498,514` (m/s², ρ-explicit). The store split is visible in the
  tests: `test_lateral_view.py:44–50` recovers g-unit coefficients; `test_car_prior.py:50–56,233–234`
  treats the same columns as g-units and asserts the `·G` / `·G/ρ` conversion.
- **De-overloading options:**
  1. Rename the columns/fields so the unit is in the name: store side
     `A0_grip_g` / `A2_grip_per_v2_g`; consumer side `A0_ms2` / `A2_aero_ms2_per_rho_v2`.
  2. Adopt ONE canonical lateral convention (the A-vs-B recommendation below) so only
     one meaning of `A0`/`A2` survives, with a single documented conversion (if any) at
     a labelled seam.
  3. Co-located unit header on `LateralParameters` and on `LateralViewResult` / the
     EstimateStore schema stating the formula + unit each carries.
- **Proposed disposition:** **fix-local** the *labelling* (options 1 + 3 — unit-suffixed
  names + headers) AND **decide-at-checkpoint** the canonical convention (option 2). The
  labelling de-overloads immediately and is low-risk; the convention unification is the
  governing fork the human owns (see recommendation below).

### OT-2 — `ρ`-in-aero: present in one form, absent in the other
- **Where overloaded:** the lateral aero grip term carries ρ in convention A
  (`A2·ρ·v²`, `physics_data_models.py:245`; `physics_simulator.py:514`) but **not** in
  convention B (`A2·v²`, `lateral_view.py:68 grip_coef`). The longitudinal/drag,
  traction-obs, and coast formulas keep ρ explicit consistently
  (`drag_acceleration` L191; `power_drag_view.wot_drive` L68; `coast_view.coast_decel` L49).
  So ρ-in-aero is overloaded **only in lateral**.
- **Why it bites:** because convention B's grip is genuinely ρ-independent (downforce
  grip-coef is normalized), the B→A boundary must *divide ρ back out*:
  `A2_param = A2_g·G/air_density` so that `A2_param·ρ·v²` reproduces the ρ-free physical
  grip (`car_prior.py:484,496`, exact because the same `air_density` flows downstream, L455).
  This is a **round-trip artifact**: ρ is injected by the consumer's formula and immediately
  cancelled by the boundary.
- **Disposition:** see the dedicated **ρ-in-aero disposition** section below (it is a *pure
  representation* call, not a refit). **decide-at-checkpoint**, bundled with the canonical
  convention — if B is canonical, the consumer's `A2·ρ·v²` should drop ρ (it is physically
  ρ-independent for a grip coefficient); if A is canonical, the `/ρ` boundary divide is retired.

### OT-3 — `G_MS2` mis-homed (the issue-cited "duplicated G_MS2")
- **Where overloaded:** `G_MS2 = 9.81` is **defined in `braking_fit.py:36`** ("m/s² per g")
  but is **unused inside braking_fit's own math** (braking fits natively in m/s²). Its only
  consumer is `car_prior.py:82` → the **lateral** g→m/s² Jacobian (L483–484). So a
  gravity constant lives in a braking module and is used by a lateral conversion.
  Meanwhile gravitational `g=9.81` is independently re-declared in ≥8 other places
  (`lateral_view`, `traction_view`, `power_drag_view`, `coast_view` defaults;
  `_G` module consts in `lateral_report`, `session_lateral`, `session_braking`,
  `session_traction`; inline in `physics_simulator.py:484`, `session_estimator.py:95`;
  `_G` in `decoupled_longitudinal.py:81`).
- **NB on issue framing:** the issue calls this "the duplicated `G_MS2`." Source shows
  `G_MS2` itself is defined **once** (`braking_fit.py:36`); the real duplication is the
  *value 9.81* scattered as ad-hoc `g`/`_G` across the views, and `G_MS2`'s **wrong home**
  (braking module, lateral use). Flagging this distinction (the from-memory framing was
  slightly off) is part of the audit.
- **De-overloading options:** (1) a single `physics/constants.py` `GRAVITY_MS2 = 9.81`
  imported everywhere; (2) at minimum move `G_MS2` out of `braking_fit` to a neutral home
  and have `car_prior` import it from there.
- **Proposed disposition:** **fix-local** (nominal cleanup is in-scope per the latitude
  ruling). Single gravity constant; retire the braking-module home. Pure rename/move, no
  numeric change, no behavior change. Low blast radius (the value is identical everywhere).

### OT-4 — `MASS_KG` defined twice
- **Where overloaded:** `MASS_KG = 808.0` in **`longitudinal_fit.py:44`** (canonical; all of
  layer2 imports this) AND independently in **`session_fit.py:57`** (`MASS_KG = 808.0`,
  used for `cda = 2·MASS_KG·theta_D` at L88). Same value today, but two sources of truth:
  a future change to one silently diverges the FitStore `cda` from every other mass user.
- **De-overloading options:** make `session_fit` import `MASS_KG` from `longitudinal_fit`
  (or a shared constants module).
- **Proposed disposition:** **fix-local** (nominal cleanup). Single definition, imported.
  No numeric change. Low risk.

### OT-5 — Longitudinal store keeps RAW PHYSICAL units; consumer wants ENGINE units
- **Where overloaded:** the EstimateStore stores `cda_closed` (m²) and `p_max` (**total W**),
  but the consumer (`LongitudinalParameters`) wants `theta_D` (m⁻¹) and `theta_P` (**W/kg**).
  The two `/(2·MASS_KG)` and `/MASS_KG` conversions live at `car_prior._build_longitudinal`
  (L343–352). The missing `/MASS_KG` was the **#518 bug** (745 km/h ideal lap). The
  FitStore, by contrast, stores `theta_D` in engine units AND `cda` in physical units (both).
- **Note:** this is a *store-schema-vs-consumer* unit gap (physical vs engine), not a
  same-name overload like OT-1. It is silent because nothing labels the store column unit
  at the consumer seam.
- **De-overloading options:** (1) unit-suffix the store columns (`p_max_watts`, `cda_m2`)
  and the consumer fields (`theta_P_w_per_kg`); (2) co-located header on
  `LongitudinalParameters` and the EstimateStore schema; (3) optionally normalize the store
  to engine units at the write boundary (`estimate_store`) instead of the read boundary
  (`car_prior`) — a representation choice analogous to the lateral A-vs-B fork.
- **Proposed disposition:** **fix-local** the labelling (1 + 2). The *where-to-convert*
  choice (3) is **decide-at-checkpoint** — it is the longitudinal sibling of the lateral
  fork and should be ruled consistently with it. No refit either way (pure scaling by a
  fixed mass).

### OT-6 — `theta_R` / `g_track` / `k_tire` (low-risk, noted for completeness)
- `theta_R` is m/s² consistently across `fit_drag_rolling`, `CoastView`, `car_prior`, and
  the simulator (no overload). `g_track` is `1.0` everywhere (a latent track-evolution
  multiplier never exercised). `k_tire` is `config.grip_decay_prior_k=0.01` on the Layer-1
  path but `0.0` from `car_prior` (`car_prior.py:519`) — a behavioral default difference,
  not a unit overload. **Disposition:** **route-out** (note in G2 docs; no action needed
  for units). The `k_tire` default mismatch is a separate modelling question.

### OT-7 — `DEFAULT_RHO` vs `reference_density_kg_m3`
- Two fallback air densities: `session_fit.DEFAULT_RHO = 1.20` (L58) and config
  `reference_density_kg_m3 = 1.225` (`physics_config.py:91`). Same concept, two values,
  two homes. **Disposition:** **route-out** (minor; flag in G2 if touched). Not a unit
  overload — a default-value inconsistency.

---

## RECOMMENDATION 1 — Canonical lateral convention (A vs B)

**The two options (verbatim from the locked scope):**
- **A** = unitless/g-coefficient canonical **everywhere**: the consumer moves to g-units,
  both producers feed g-units. Bigger blast radius (the live `sim_evaluator`/`fit_batch`
  path is touched).
- **B** = m/s² canonical **at the consumer**: producers normalize up to it (the legacy
  producer already is m/s²; the five-view producer converts up). Smaller blast radius
  (consumer untouched). This is the **status-quo** shape — `car_prior` already does B.

### Independently-confirmed blast-radius fact (the #522-blocking fact)

**Confirmed from source, not memory:** the live `sim_evaluator` / `fit_batch` path does
**NOT** consume the g-unit store and does **NOT** route through `car_prior`:
- `fit_batch.run_batch` → `fit_driver` → `session_fit.fit_session_full`
  (`session_fit.py:239` builds params via `ParameterEstimator.estimate_parameters` →
  `LateralEnvelopeFit`, convention **A m/s²**) → `record_from_params` writes the **FitStore**
  in m/s² (`session_fit.py:89`).
- `sim_evaluator.evaluate_session` (`sim_evaluator.py:194–243`) calls
  `fit_session_full(...)` then `PhysicsSimulator.simulate_lap(track_df, full.params)` —
  native convention A; **no g-units anywhere on this path**.
- Only the **C1 utilization path** carries the g→m/s² conversion:
  `characterize.characterize_case` → `car_prior.build_car_ceiling` (`_assemble_lateral`,
  g→m/s²) → `CapabilityEnvelope.from_parameters` → `regime_utilization` →
  `PhysicsSimulator.simulate_lap` (`regime_utilization.py:508,579`).

**Implication:** choosing **A (g-units canonical)** forces the *legacy/live* producer
(`lateral_envelope.py`), the m/s² consumer (`physics_data_models`, `physics_simulator`,
`capability_envelope`), the FitStore schema, AND every test that hard-codes m/s² A0/A2
to move to g-units — i.e. it touches the proven-working `sim_evaluator`/`fit_batch` path.
Choosing **B (m/s² canonical)** leaves all of that untouched and only formalizes the
single conversion that already exists at `car_prior`.

### Honest blast-radius enumeration

**Option B (m/s² canonical at consumer) — RECOMMENDED. Files/tests touched:**
- *src (labelling/representation only):*
  - `physics_data_models.py` — unit header + suffix on `LateralParameters` (no formula change).
  - `layer2/lateral_view.py` + `layer2/estimate_store.py` — label `A0`/`A2` columns/fields
    as g-units; optionally rename to `*_g`.
  - `utilization/car_prior.py:_assemble_lateral` — keep the conversion but make it the
    single sanctioned, documented seam (retire the `# TODO(#525)`); source `G_MS2` from a
    neutral constants home (OT-3).
- *tests (NO re-baseline of numbers):* `test_car_prior.py` (conversion asserts already
  encode B — they stay green), `test_lateral_view.py` (g-unit recovery — stays green),
  `test_lateral_envelope.py` / `test_physics_simulator.py` / `test_capability_envelope.py`
  / `test_published_f1_data.py` (m/s² magnitudes — unchanged because the consumer is
  unchanged). Net: **only renames/headers + one new known-answer guard; zero numeric
  re-baseline.**

**Option A (g-units canonical everywhere) — larger. Files/tests touched:**
- *src (behavioral representation change):* `lateral_envelope.py` (emit g-units — divide its
  m/s² fit by g, drop ρ from aero), `physics_data_models.lateral_capability` (rewrite to
  `(A0 + A2·v²)·g·...`), `physics_simulator._compute_speed_caps`/`_gsat_ceiling`
  (rewrite the corner-cap algebra in g-units), `capability_envelope` (ceiling-trust + all
  lateral reads), `apex_extract`, `friction_coupling`, both store schemas, `parameter_estimator`
  defaults (`default_A0=30.0`→~3.06 g; `default_A2`), `physics_config` default values.
- *tests (RE-BASELINE):* every test that hard-codes m/s² A0/A2 magnitudes —
  `test_lateral_envelope.py`, `test_physics_simulator.py`, `test_capability_envelope.py`,
  `test_car_prior.py` (conversion deleted), `test_published_f1_data.py`,
  `test_density_consistency.py`, `test_numerical_stability.py`, `test_parameter_uncertainty.py`,
  `test_monte_carlo.py`, the regression fixtures (`spain_2024_fp1_ver/blessed_params.json`,
  `monaco_2024_fp1_ver/blessed_params.json`), and the `test_ideal_lap_top_speed_invariant`.
- This path **modifies the live `sim_evaluator`/`fit_batch` path and its blessed fixtures** —
  exactly the risk that got #522's from-memory first fix blocked.

### Recommendation
**Recommend Convention B (m/s² canonical at the consumer)**, paired with **unit-suffixed
field/column names + co-located headers** (OT-1 labelling). Rationale:
1. It is the de-overloading north star with the **smallest, lowest-risk blast radius** —
   the consumer and the proven `sim_evaluator`/`fit_batch` path are untouched.
2. The single conversion already exists, is tested (`test_car_prior.py`), and is exact
   (same ρ both sides). G2 promotes it from a `# TODO(#525)` localized patch to the one
   sanctioned, labelled seam.
3. The user is explicitly **not hard on unitless** — B satisfies "pick whichever best
   de-overloads with acceptable blast radius."
4. **Caveat carried up:** B keeps the ρ-round-trip artifact (OT-2) unless the consumer's
   `A2·ρ·v²` is changed to drop ρ. If the human wants the cleanest physics, the ρ removal
   (below) can ride along with B without touching the convention. This is the human's call.

(Convention A is *defensible* if the goal is a single physical truth with no boundary
conversion at all, but its blast radius reaches the live sim path + blessed fixtures and a
full numeric re-baseline — higher risk for an alignment-only run.)

---

## RECOMMENDATION 2 — ρ-in-aero disposition (representation vs refit?)

**Verdict: PURE REPRESENTATION / CONVERSION change. No refit required.**

Evidence:
- The lateral fits do **not** re-estimate any parameter from data when ρ is added/removed —
  ρ appears only as a deterministic multiplier in the consumer formula and is exactly
  cancelled at the boundary. `car_prior.py:455` documents the cancellation is **exact**
  (`A2_param·air_density == A2_g·G`) because the same `air_density` flows from
  `build_car_ceiling` to the consumer. No data is touched; no `lstsq`/bootstrap re-runs.
- Convention B's grip coefficient is, by construction, ρ-independent (`μ_obs = |a_lat|/(g·cos θ)`,
  `lateral_view.py:141` — ρ never enters). Removing `ρ` from the consumer's aero term and
  the matching `/ρ` from the boundary is a **symbolic identity**, not a new estimate.
- Contrast: a refit would be required only if the *fit itself* baked an assumed ρ that we
  wanted to change (e.g. re-deriving `cda` at a different reference density). That is **not**
  the case for lateral — ρ is not in the lateral fit. (For longitudinal/drag, ρ IS in the
  fit via the design matrix `air_density*v²`, but #525 does not propose changing the drag
  fit; the store already carries `cda` in physical m² and the per-session `rho`.)

**Therefore:** unifying ρ-in-aero is **in-scope-eligible** (no stop-and-route trigger).
Recommended bundling: do it **with the canonical-convention ruling** —
- If **B** canonical: drop ρ from `lateral_capability`'s aero term (`A2·v²` in g-derived
  m/s²) and drop the `/air_density` from `_assemble_lateral`. Pure representation.
- If **A** canonical: ρ stays in the consumer (it is the m/s² physical form); the boundary
  conversion is deleted because both producers already feed m/s².
Either way: **no refit, no fit re-derivation.** I flag it as **decide-at-checkpoint** only
because the cleanest form depends on the convention ruling, not because it needs a refit.

---

## Channels beyond the handoff's listed set

The handoff listed lateral, longitudinal/power, braking, traction, coast, terrain. Audit
found **no additional force channel**. Cross-cutting items NOT in the per-channel list but
material to units: the **two stores** (Layer-1 `FitStore` vs layer2 `EstimateStore`) carry
the *same parameter names in different unit conventions* (lateral g-units vs m/s²;
longitudinal physical vs engine) — this is the structural root of OT-1/OT-5 and deserves a
header in each store's schema doc. The **gravity constant** (OT-3) and **mass constant**
(OT-4) are cross-channel constants, not a channel, but are the cited de-overloading targets.

---

## Disposition summary table

| ID | Term | Overload | Disposition |
|---|---|---|---|
| OT-1 | lateral `A0`/`A2` | g-units vs m/s² (same names) | labelling **fix-local**; convention **decide-at-checkpoint** (rec: B) |
| OT-2 | ρ-in-aero (lateral) | present (A) vs absent (B); round-trip cancel | **decide-at-checkpoint** w/ convention; **pure representation, NO refit** |
| OT-3 | `G_MS2` / `g=9.81` | mis-homed + ≥8 ad-hoc copies | **fix-local** (single GRAVITY const) |
| OT-4 | `MASS_KG` | defined twice (808.0) | **fix-local** (single def, imported) |
| OT-5 | longitudinal store | physical (m²,W) vs engine (m⁻¹,W/kg) | labelling **fix-local**; where-to-convert **decide-at-checkpoint** |
| OT-6 | `k_tire` default | 0.01 (L1) vs 0.0 (car_prior) | **route-out** (modelling, not units) |
| OT-7 | `DEFAULT_RHO` vs `reference_density_kg_m3` | 1.20 vs 1.225 | **route-out** (default-value, minor) |

**One-line bottom line for the checkpoint:** recommend **B (m/s² canonical at consumer) +
unit-suffixed labels + co-located headers**, fold the gravity/mass constant dedup in as
nominal cleanup, treat ρ-in-aero as a pure-representation change bundled with the convention
ruling (no refit), and route `k_tire`/`DEFAULT_RHO` out as non-units follow-ups.
