# Cartographer Reconcile Briefing — #525 (physics units-convention unify + rename)

Drive your own `CARTOGRAPHER.template.json` checklist. This briefing lists what changed so you
fold it into the recorded architecture. **Packet-first.** The two commits on
`feat/physics-units-audit-525` are `ca4abcfc` (code) and `df192e2a` (docs);
`git diff main..HEAD` shows everything.

## What changed (current truth to reconcile)

1. **Full physics parameter SEMANTIC RENAME (de-overload).** Convention B (m/s² canonical at the
   consumer; consumer + live sim path math untouched). Every parameter renamed to `<what>_<unit>`:
   `A0`→`lateral_mech_grip_{g,ms2}`, `A2`→`lateral_aero_grip_{g,ms2}`, `p_max`→`max_power_w`,
   `theta_P_values`→`specific_power_w_kg`, `theta_D`→`spec_drag_m2_kg`, `theta_R`→`rolling_decel_ms2`,
   `cda*`→`drag_area_*_m2`, `a_b/b_b`→`brake_decel_ms2`/`brake_aero_decel_per_m`,
   `a_t/b_t`→`traction_accel_ms2`/`traction_aero_accel_per_m`, terrain `theta/z/bank`→
   `slope_rad/altitude_m/bank_rad`, + `_sigma` companions. Across producers, both stores
   (`EstimateRecord`, `FitRecord`), consumers, fit locals, tests. The `_g` (producer/store,
   density-agnostic, poolable) vs `_ms2` (consumer, per-session) split is intentional.
2. **`src/physics/constants.py` (NEW)** — `GRAVITY_MS2 = 9.81` canonical home. `braking_fit.G_MS2`
   retired to a deprecated import alias. Single `MASS_KG` (`longitudinal_fit`; `session_fit` imports).
   Air-density fallback `DEFAULT_RHO` 1.20→1.225 (ISA).
3. **`friction_coupling.py` DELETED** — superseded-but-unused; removed from `parameter_estimator`
   + `__init__` export + its tests. **Drop the `FrictionCoupling` node from `struct:physics`.**
4. **`car_prior._assemble_lateral` / `_build_longitudinal`** are now the **one sanctioned, documented
   conversion seams** (g→m/s² lateral; watts→W/kg longitudinal). The `# TODO(#525)` is retired.
   → **`decision:ideal_lap_sim_two_sided_evaluator` Review Trigger FIRED** (update the annotation:
   the lateral conversion is generalized/sanctioned, not a localized patch). →
   **`claim:lateral_car_prior_boundary_conversion`**: the conversion still lives at `car_prior` but
   is now the canonical labelled boundary with renamed fields; #525 was the unification — update its
   summary (the two-producer split is documented, the legacy producer is convention-A m/s², the
   five-view producer is convention-B g-units, conversion at car_prior; the names now carry units).
5. **`scripts/migrate_physics_store_columns_525.py` (NEW)** — idempotent `ALTER TABLE RENAME COLUMN`
   migration that realigned the on-disk stores (`physics_estimates.db`, `_g3wired.db`,
   `physics_fits.db`) to the renamed columns. Run + verified (C1 read+pool intact).
6. **`docs/architecture/reference/physics-unit-conventions.md` (NEW)** — the durable unit map
   (table + `_g`/`_ms2` rationale + **fit-model vs apply-model split** + the conversion boundary).
   Referenced from `docs/AGENT_GUIDE.md` with a review-and-update mandate. Consider recording this
   as a reference/anchor in the map, and note the **fit-vs-apply asymmetries** as known limits:
   banking normalized at fit but not re-applied at apply (**#527**), tyre-decay/track-grip apply-only
   (**#511**).

## Suggested reconcile actions (you decide/record rationale)
- Update `docs/architecture/packets/physics.md`: the renamed parameters in Key Modules / data
  models; remove `friction_coupling.FrictionCoupling`; add `constants.py` (GRAVITY_MS2/shared
  constants); add the unit-conventions reference doc + the migration script; update the
  Known-Limits two-producer/units notes (the localized-patch language → now unified/renamed);
  note the fit-vs-apply asymmetries (#527/#511) as known limits.
- Update `decision:ideal_lap_sim_two_sided_evaluator` (Review Trigger fired — record the #525
  generalization) and `claim:lateral_car_prior_boundary_conversion` (renamed-fields, sanctioned
  boundary) in `overlays/constraints.yml`.
- **tc6 (triage):** `docs/DOCUMENTATION.md` doesn't list the new reference doc — you may add the
  row if it's a clean current-truth doc-index fix, else leave to Triage.

## Out of scope (do NOT fold as current truth)
- The banking fit/apply fix (#527) and the k_tire value unification (#511) are FUTURE work — record
  them only as known-limits/cross-refs, not as implemented.

Write your reconcile output/findings to `.agent-work/525/crew-handoffs/reconcile-result.md`.
