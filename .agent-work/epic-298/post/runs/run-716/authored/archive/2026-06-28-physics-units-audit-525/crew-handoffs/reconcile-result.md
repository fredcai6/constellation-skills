# Cartographer Reconcile Result — #525 (physics units-convention unify + rename)

**Date:** 2026-06-27
**Branch:** feat/physics-units-audit-525
**Commits reconciled:** ca4abcfc (code) + df192e2a (docs)
**Map compliance:** check_arch_map.py green throughout (39 catalog nodes, 18 packets, 12 overlay nodes)

---

## Checklist Status

- **context (c1):** SATISFIED — map-model, ORCHESTRATOR_CONTEXT, and all touched architecture files loaded; current code verified by grep and direct module-import test.
- **packets (c1):** SATISFIED — `packets/physics.md` reconciled against current code (verified field names via grep on car_prior.py; verified constants.py import; verified friction_coupling.py deletion via Glob).
- **index-overlays (c1):** SATISFIED — `index.md` reconcile entry added; `overlays/constraints.yml` claim updated; `decision:ideal_lap_sim_two_sided_evaluator` trigger fired; `docs/DOCUMENTATION.md` updated.
- **map-compliance (c1):** SATISFIED — check_arch_map.py green; open items recorded; future work cross-referenced.

---

## Edits Made

### 1. `docs/architecture/packets/physics.md`

**Node removed:** `friction_coupling.py` / `FrictionCoupling` entry deleted from the Per-lap force-channel fitting section (Layer 1 Key Modules). Evidence: `Glob src/physics/friction_coupling.py` returns no result; file is deleted on this branch.

**Node added:** `constants.py` entry added after `physics_config.py` in the Layer 1 Key Modules section. Documents `GRAVITY_MS2 = 9.81` as the canonical constant home, the deprecated `braking_fit.G_MS2` alias, and the location of `MASS_KG` in `longitudinal_fit.py`. Evidence: `src/physics/constants.py` verified; `py -c "from src.physics.constants import GRAVITY_MS2"` returns 9.81.

**car_prior.py entry updated** (utilization section): replaced all pre-#525 parameter names:
- `p_max` → `max_power_w` (store field); `theta_P_values` → `specific_power_w_kg` (consumer field)
- `A0`/`A2` → `lateral_mech_grip_g`/`lateral_aero_grip_g` (store) and `lateral_mech_grip_ms2`/`lateral_aero_grip_ms2` (consumer)
- Updated two-producer split language: removed "unification tracked in #525" (done); added "sanctioned, documented boundary as of #525"; referenced `claim:lateral_car_prior_boundary_conversion` and `docs/architecture/reference/physics-unit-conventions.md`.

**Characterization finding updated:** replaced "g-unit store A0/A2" with "g-unit store `lateral_mech_grip_g`/`lateral_aero_grip_g`".

**`accel_obs.py` entry updated:** replaced "NOT the de-conflated capability `a_b/b_b`" with the post-#525 names `brake_decel_ms2`/`brake_aero_decel_per_m`.

**Decision anchors summary updated** (in-packet prose for `decision:ideal_lap_sim_two_sided_evaluator`):
- Replaced "G5 p_max watts→W/kg" → "G5 `max_power_w` watts→W/kg via `_build_longitudinal`"
- Replaced "G2 lateral g-unit→m/s²" → "G2 lateral g-unit `lateral_mech_grip_g`/`lateral_aero_grip_g`→m/s² via `_assemble_lateral`"
- Added "#525 rename + seam sanctioned" note (TODO retired; all parameters now carry unit suffixes).

**Known Limits added (3 new bullets):**
- Fit-vs-apply asymmetry — banking (#527): `LateralView.fit` normalizes banking out of the grip coefficient but the apply side does not re-apply `cosθ`; banked tracks have lateral capability overestimated. Cross-reference #527 (FUTURE, not implemented).
- Fit-vs-apply asymmetry — tyre-grip decay and track-grip multiplier (#511): fit assumes steady-state grip; `lateral_capability` applies `exp(-k_tire·laps)` and `track_grip_mult` at apply time; `car_prior` sets both to neutral defaults. Cross-reference #511 (FUTURE, not implemented).
- Parameter naming and unit conventions reference bullet: points to `docs/architecture/reference/physics-unit-conventions.md` and `scripts/migrate_physics_store_columns_525.py`.

### 2. `docs/architecture/overlays/constraints.yml`

**`claim:lateral_car_prior_boundary_conversion` updated:**
- Label broadened: "car_prior._assemble_lateral and _build_longitudinal are the ONE sanctioned unit-conversion seams"
- Summary expanded to cover:
  - Post-#525 field names (`lateral_mech_grip_g`, `lateral_aero_grip_g`, `lateral_mech_grip_ms2`, `lateral_aero_grip_ms2`)
  - `_build_longitudinal` seam for `max_power_w` → `specific_power_w_kg` and `drag_area_closed_m2` → `spec_drag_m2_kg`
  - Two-producer split described as "intentional and documented as of #525" (removed "unification is #525")
  - `_g` vs `_ms2` suffix naming described as making the boundary visible
  - Durable unit table cross-reference: `docs/architecture/reference/physics-unit-conventions.md`
  - Evidence updated: added commits ca4abcfc+df192e2a alongside existing 33c56214

### 3. `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md`

**G5 parameter name updated (Current Structural Consequence):**
- "store's total-watts `p_max`" → "store's total-watts `max_power_w`"
- "`theta_P_values` (= `p_max/MASS_KG`)" → "`specific_power_w_kg` (= `max_power_w/MASS_KG`)"

**Review Trigger: new FIRED item added:**
```
~~`car_prior._assemble_lateral`/`_build_longitudinal` sanctioned as the ONE conversion seams;
parameter rename to `<what>_<unit>` (`lateral_mech_grip_g`, `max_power_w`, `brake_decel_ms2`,
etc.)~~ **FIRED — #525 landed 2026-06-27; TODO(#525) retired; `_g`/`_ms2` suffix naming
makes boundary visible; durable unit table at `docs/architecture/reference/physics-unit-conventions.md`.**
```

### 4. `docs/architecture/index.md`

**Reconcile entry appended** after the 2026-06-26 (#522) entry. Covers all six items from the briefing: full rename; new `constants.py`; `friction_coupling.py` deleted; `car_prior` seams sanctioned; new `reference/physics-unit-conventions.md`; `migrate_physics_store_columns_525.py`. Also records tc6 decision (DOCUMENTATION.md row added — see below). Records check_arch_map.py green.

### 5. `docs/DOCUMENTATION.md`

**New row added** in the Active Domain Reference table:
```
| `docs/architecture/reference/physics-unit-conventions.md` | Durable physics parameter name→unit→producer→store→consumer table;
  `_g` vs `_ms2` rationale; fit-vs-apply asymmetries; single conversion boundary
  (`car_prior._assemble_lateral`/`_build_longitudinal`). Review-and-update mandate:
  any work that adds, renames, or repurposes a physics model parameter must update
  this doc in the same gate. |
```

**Rationale (tc6):** This is a clean current-truth fix. The doc `docs/architecture/reference/physics-unit-conventions.md` exists, is referenced from `docs/AGENT_GUIDE.md` with an active review mandate, and is a durable reference (not a historical writeup). Adding its index row is within Cartographer's authority for current-truth doc-index maintenance. No Triage route needed.

---

## Nodes Added / Removed

| Action | Node | Evidence |
|---|---|---|
| Added (packet prose) | `constants.py` module within `struct:physics` | `src/physics/constants.py` exists; GRAVITY_MS2 import verified |
| Removed (packet prose) | `friction_coupling.FrictionCoupling` within `struct:physics` | `Glob src/physics/friction_coupling.py` returns no result |
| Updated (packet prose) | `scripts/migrate_physics_store_columns_525.py` reference | file exists on branch; idempotent migration run + verified per briefing |
| Updated (overlay) | `claim:lateral_car_prior_boundary_conversion` | post-#525 field names, both seams, sanctioned language |

No new structural nodes, capability nodes, or edges were added or removed. The map node count is unchanged (39 catalog nodes, 18 packets, 12 overlay nodes).

---

## Items Left for Triage

1. **Banking fit/apply asymmetry (#527):** `LateralView.fit` normalizes banking out (`mu = |a_lat|/(g·cosθ)`) but the apply side is flat. Recorded as Known Limit with #527 cross-reference. Remediation = FUTURE work; do not fold as implemented.
2. **Tyre-decay/track-grip apply-only (#511):** `k_tire` and `track_grip_mult` are apply-side-only modulations with no fit equivalent. Recorded as Known Limit with #511 cross-reference. Remediation = FUTURE work.
3. **`PhysicsEstimatorConfig.default_A0`/`default_A2` config field names not renamed:** These are the legacy m/s² fallback defaults in `physics_config.py`. They were NOT renamed by #525 (they're fallback constants in convention-A m/s², not store column names). This is a naming inconsistency that could be confusing — but it is current code truth. The packet correctly notes these "are already convention-A m/s² and pass through unconverted." If a rename is desired, it's a future cleanup issue.

---

## Workflow Feedback

- The briefing was clear and complete; every suggested action had a direct target (file + section) which made each edit mechanical. No ambiguity required an ask.
- tc6 (DOCUMENTATION.md) was correctly framed as a judgment call. The "clean current-truth fix" test passes: the doc is live, referenced from AGENT_GUIDE.md with a mandate, and the `docs/architecture/reference/` directory is new enough that it was never listed. Adding the row is defensible and complete.
- The fit-vs-apply section in `physics-unit-conventions.md` is well-structured. Recording them as Known Limits in the packet (with #527/#511 cross-refs) is the right sparse treatment — they don't need overlay nodes since they don't govern planning boundaries, they just limit trust of the current sim on banked circuits. The known-limits prose serves that purpose.
- One mismatch noted during the edit: `decision:ideal_lap_sim_two_sided_evaluator` already had "A0/A2" in the fired-trigger line (for #522) and "p_max" in the G5 line. These were cleaned up in place. The decision anchor is not a packet but it's part of the structural record — updating parameter names there was the right call.
- check_arch_map.py remained green throughout all edits, confirming no overlay-node or edge consistency issues were introduced.
