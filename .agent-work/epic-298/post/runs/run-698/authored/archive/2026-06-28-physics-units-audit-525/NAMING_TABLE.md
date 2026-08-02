# #525 — Physics Parameter Naming Spec (user-approved 2026-06-27)

The binding rename target for the G2 rework. Supersedes the "unit-suffix only" labelling.
**Goal:** kill the cryptic baked-in names (`A0`, `A2`, `theta_*`, `a_b`, `b_b`, `a_t`, `b_t`)
— every parameter gets a name that says **what it is** AND **what unit space it lives in**.

## Convention: `<what_it_is>_<unit_space>`

Unit-space tokens (the exact token per field = the **verified unit from `AUDIT_MAP.md`** — do
not guess; where a token below is marked `[verify]`, read the source/audit and use the real one):
- `_ms2` — m/s² · `_g` — g-unit grip coefficient (dimensionless) · `_w` — watts · `_w_kg` —
  W/kg · `_m2` — m² · `_per_m` — per metre · `_rad` — radians · `_m` — metres · dimensionless
  multiplier → `_mult` · per-lap → `_per_lap`.

### Why producer `_g` and consumer `_ms2` (NOT an inconsistency to erase)
The five-view producer (`lateral_view`) measures the grip **coefficient** `mu = a_lat/(g·cosθ)`
— mass- and density-**agnostic**, which is exactly what makes it **poolable across sessions**
(the layer2 store keeps the g-unit coefficient + the per-session ρ separately). The m/s²
physical acceleration is *derived* per-session at the one `car_prior` boundary (combining the
g-coefficient with that session's ρ). So `_g` (fit/store space) and `_ms2` (apply/sim space)
are two real spaces with one conversion seam — the names make that visible. (Convention B chose
where the canonical *consumer* lives = m/s²; it did NOT mandate one unit everywhere.)

## Name table (current → proposed general name)

| Channel | Current | Proposed general | Unit token(s) |
|---|---|---|---|
| lateral | `A0` | `lateral_mech_grip` | `_g` (producer/store) · `_ms2` (consumer/FitStore) |
| lateral | `A2` | `lateral_aero_grip` | `_g` (producer/store) · `_ms2` (consumer/FitStore) |
| lateral | `ceiling` | `lateral_grip_ceiling` | `_ms2` |
| lateral | `g_track` | `track_grip` | `_mult` (dimensionless) |
| lateral | `k_tire` | `tyre_grip_decay` | `_per_lap` |
| long | `theta_D` / `theta_D_open` | `spec_drag` / `spec_drag_open` | `[verify]` (CdA/2m; per AUDIT_MAP) |
| long | `theta_R` | `rolling_decel` | `_ms2` |
| long | `theta_P_values` | `specific_power` | `_w_kg` |
| long | `p_max` | `max_power` | `_w` |
| long | `cda_closed` / `cda_open` | `drag_area_closed` / `drag_area_open` | `_m2` |
| braking | `a_b` | `brake_decel` | `_ms2` |
| braking | `b_b` | `brake_aero_decel` | `_per_m` |
| traction | `a_t` | `traction_accel` | `_ms2` |
| traction | `b_t` | `traction_aero_accel` | `_per_m` |
| coast | `coast_theta_R` (store) | `coast_rolling_decel` | `_ms2` |
| coast | coast `cda` | `coast_drag_area` | `_m2` |
| terrain | `theta` | `slope` | `_rad` |
| terrain | `z` | `altitude` | `_m` |
| terrain | `bank` | `bank` | `_rad` |

Notes:
- **`_sigma` companions rename in lockstep:** `A0_sigma` → `lateral_mech_grip_g_sigma`,
  `p_max_sigma` → `max_power_w_sigma`, etc. Every `*_sigma`/`*_std` field/column follows its base.
- **Fit-local variable names** (`a`, `b`, `A`, `B` inside the fit functions) should also become
  readable (`intercept`/`v2_coef` or the channel name) — the user explicitly dislikes the
  single-letter locals. Behaviour-preserving.
- Channel-qualifier prefixes already present (`coast_`, `pd_`, `_open`/`_closed`) stay as
  qualifiers; append the unit token.
- The unit token must be the **source-verified** unit (especially `spec_drag`/`theta_D` —
  AUDIT_MAP cites it; reconcile any audit-vs-derived discrepancy and use the correct one,
  noting it in the header).

## Store migration (the persistence consequence)
The SQLite store **column names are auto-derived from the dataclass field names**
(`EstimateRecord` → `session_estimates`; `FitRecord` → `fit_store`). Existing populated stores
on disk — `data/physics_estimates.db` (the costly 2023-Q store the C1 path reads),
`data/physics_estimates_g3wired.db`, `data/physics_fits.db` — will stop being readable when the
fields/columns rename.

**Approach (user-approved):** ship a one-shot **idempotent migration** that renames the columns
in the existing DBs in place (`ALTER TABLE <t> RENAME COLUMN <old> TO <new>` — SQLite ≥3.25; our
Python 3.14 sqlite3 supports it). No recompute; data preserved; C1 keeps working. A fresh
rebuild stays the fallback (the stores are regenerable artifacts, not canonical data). The
migration must: cover every renamed column incl. `_sigma` companions, be safe to re-run (skip
already-migrated columns), and live at a discoverable path (e.g. `scripts/migrate_physics_store_columns_525.py`)
with a short docstring. Verify post-migration that `pool_driver`/`car_prior` read the renamed
columns and the C1 dashboard path still loads.

## Out of scope (unchanged)
No fit/model changes, no ρ removal, no banking re-application (that's the new #509 follow-up),
no `k_tire` value change (#511), no units library, no per-param band-test matrix.
