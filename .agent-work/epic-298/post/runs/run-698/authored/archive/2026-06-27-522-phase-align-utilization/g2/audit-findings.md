# G2 Consumer Audit Findings (#522 lateral units fix)

## Two runtime-disjoint lateral conventions (the key discovery)

| Path | Producer | A0 units | rho on aero? | Store | Feeds #522? |
|---|---|---|---|---|---|
| **B (live)** | `layer2/lateral_view.py` | g-unit coeff (A0≈1.6-5.0) | NO | `session_estimates` → `car_prior` | **YES** (sim corner caps, truth anchor) |
| A (legacy) | `lateral_envelope.LateralEnvelopeFit` | m/s² (A0≈30, `default_A0=30`) | YES (correct in its own m/s² fit) | `session_fits` (FitStore) | No (in-memory diagnostic via `session_fit.fit_driver`) |

The shared `LateralParameters.lateral_capability` was written for convention A
(m/s²) but the LIVE store carries convention B (g-units). The fix unifies on the
**producer-of-truth convention (g-units)**: `lateral_capability` and all sim
consumers now apply `× G_MS2` and drop the spurious `ρ`. This is correct for the
live path; it intentionally makes the legacy convention-A in-memory inputs
(A0=30) non-physical — those only ever appeared in tests, now re-baselined.

## Site-by-site

1. **`physics_data_models.LateralParameters.lateral_capability`** — ROOT. Fixed:
   `mechanical = A0·tire·g_track·G_MS2`, `aero = A2·v²·G_MS2` (dropped `ρ`).
   Canonical `G_MS2 = 9.81` added here as the single source.

2. **`physics_simulator._compute_speed_caps`** — Fixed: `A0` term `× G_MS2`;
   `denom = κ − A2·G_MS2` (dropped `air_density`). Ceiling stays m/s² (consistent).

3. **`physics_simulator._gsat_ceiling`** — Fixed: `car_lat = (A0·g_track + A2·v_ref²)·G_MS2`
   (dropped `air_density`). `pop_max` now uses `G_MS2`. NOTE: pre-fix the
   `min(car_lat, pop_max)` compared g-units (~2.6) to m/s² (~49) and always
   picked the tiny `car_lat`; post-fix `car_lat`≈26 m/s² so the clamp can bite.

4. **`capability_envelope.py` L84 headroom check** — Fixed: `(ceiling − A0·g_track·G_MS2)`
   (was `(ceiling − A0·g_track)`, mixing m/s² ceiling with g-unit floor).
   `lateral_capability` (L101) DELEGATES to the data model → auto-corrected.

5. **`friction_coupling.py`** — DELEGATES to `lateral_capability` (L36, L57). No
   inline mis-scaling, no pre-existing ×g compensation. `compute_friction_utilization`
   is a dimensionless ratio (`a/a_max`) → INVARIANT to the scaling. No change.

6. **`apex_extract.py` `_on_limit` (L161)** — DELEGATES to `lateral_capability`.
   Compares observed `a_lat` (m/s²) to `fraction × capability`; rides the
   corrected (now physical) ceiling as intended. No inline scaling. No change.

7. **Braking/traction grip-ratio fallbacks** (`capability_envelope` L118, L135)
   `braking_grip_ratio × lateral_capability`, `traction_grip_ratio × lateral_capability`
   — ride the corrected lateral magnitude. INTENDED (ratios of physical lateral).
   Mostly inert for RBR 2023-Q (measured frontiers present). No double-correction.

8. **`physics_simulator` MC sampler (L285-305)** — perturbs raw g-unit A0/A2 by
   covariance and clips, then rebuilds `LateralParameters` fed to the fixed
   `_compute_speed_caps`. Convention-agnostic; scaling applied downstream. No change.

## No double-correction found
Every consumer either delegates to `lateral_capability` (root fix propagates) or
does its own inline scaling which was fixed in lockstep. Nothing already
multiplied by g — so nothing to remove.

## Producer-side (NOT consumers, out of scope, left unchanged — correct as-is)
- `lateral_envelope.py` L217 (`A0 + A2·ρ·v²`) and `fit_utils.py` L261 — these are
  the convention-A FIT residuals/ceiling-detection, internally consistent in m/s².
- `lateral_view.py` — the g-unit producer (source of truth).

## Triage candidates (out of scope)
- `braking_fit.py::G_MS2 = 9.81` duplicates the new canonical constant; consolidate
  to import `physics_data_models.G_MS2` (braking_fit not in g2 scope).
- `A0_max_plausible=60` / `A2_max_plausible=0.01` plausibility clips were sized for
  convention-A m/s² A0; harmless for g-unit A0 (never bite) but semantically stale.
- Convention-A `LateralEnvelopeFit`/`FitStore` path is now non-physical against the
  shared data model; if it is dead it should be removed (#491 cleanup already slates
  `FrictionCoupling`); if live for diagnostics, it needs its own g-unit reconciliation.
