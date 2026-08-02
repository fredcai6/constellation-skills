# Implementer Handoff — G2 Lateral Units Fix (#522)

## Gate
g2-implement (the FIX — re-planned at decide-fix; user directive: "fix the bugs" = fix at source, correcting the #485 production envelope too)

## Task
Correct a lateral-grip **units bug** (same class as #518 G5). The producer `LateralView` fits A0/A2 as **dimensionless g-unit grip coefficients**; the consumers read them as **m/s²**, missing a **×g (9.81)** and applying a **spurious ×ρ** on the aero term. Apply ×g and drop the spurious ρ consistently across **all** lateral consumers, with a single canonical scaling convention. This corrects every corner-speed cap in the ideal lap and the #485 production `CapabilityEnvelope` (intended; physics-only blast radius — nothing in evo/latent_power/compound_prior consumes it).

## Protected Intent
The lateral capability must be physically scaled (F1 cars sustain ~3–5g lateral). The corrected Monaco/VER tunnel cap must land near VER's actual speed (~63 m/s), not 16 m/s. Do not introduce a dual unit convention or a compatibility shim.

## Test Mode
TDD/test-led + **truth-anchored**. The existing physics unit tests were written against the BUGGY (~10× low) values — re-baseline their expected numbers to PHYSICAL truth (real apex/corner speeds, ~3–5g lateral), not by mechanically multiplying old expectations. A unit-scaling change where every expectation just ×9.81 is acceptable ONLY where you've confirmed the new value is physically right.

## The bug — exact sites (verified from source)
**Producer / source of truth:** `src/physics/layer2/lateral_view.py` (docstring lines 3–5, 50–54):
`mu_max(v) = A0 + A2·v²` is a **grip COEFFICIENT in g-units**; `a_lat_max(v) = mu_max(v)·g·cos(theta)`; `A0` = mechanical grip coefficient (g-units), `A2` = aero grip coefficient `1/(m/s)²` (NO ρ).

**Buggy consumers:**
1. `src/physics/physics_data_models.py` ~L237 `LateralParameters.lateral_capability`:
   `mechanical = A0·tire_factor·g_track` (missing ×g); `aero = A2·rho·speed²` (spurious ×rho, missing ×g). → should be `mechanical = A0·tire_factor·g_track·g` and `aero = A2·speed²·g`.
2. `src/physics/physics_simulator.py` `_compute_speed_caps` (~L489): `A0 = lateral.A0·g_track` used directly as accel; `denom = curvature − A2·air_density`; `v_unbounded = sqrt(A0/denom)`; `ceil_cap = sqrt(eff_ceiling/curvature)`. Same two errors inline. → A0 term ×g; `denom = curvature − A2·g`; eff_ceiling units consistent (see below).
3. `src/physics/physics_simulator.py` `_gsat_ceiling` (~L465): `car_lat = A0·g_track + A2·air_density·v_ref²` — same bug. Note `pop_max = gsat_population_max_g·9.81` is ALREADY m/s², so currently the `min(car_lat, pop_max)` compares g-units (~2.6) to m/s² (~49) and always picks the tiny car_lat. After the fix car_lat becomes ~26 m/s² and the clamp works as intended.

## MUST-RESOLVE audit (do not skip — the reviewer will check these)
- **`lateral.ceiling` (tyre-saturation cap) units.** `lateral_capability` does `min(mechanical+aero, ceiling)` and `capability_envelope.py` ~L82 compares `(lat.ceiling − lat.A0·g_track)` to a `*_ms2` threshold. Determine whether `ceiling` is stored in g-units or m/s² (trace where it is set — lateral_view / session_fit / car_prior sets it `None`), and scale it consistently so the `min` and the headroom check are unit-consistent after the fix. car_prior sets `ceiling=None` (Gsat path), but session-fit direct paths may set it.
- **`src/physics/friction_coupling.py`** and **`src/physics/apex_extract.py`** — both reference lateral capability; audit for the same mis-scaling or any **pre-existing compensation** that already multiplies by g (if found, do NOT double-correct — fix the root and remove the compensation, single source of truth).
- **braking/traction grip-ratio fallbacks** (reviewer flag): anywhere a `braking_grip_ratio`/`traction_grip_ratio × lateral_capability` composes channels — confirm the corrected lateral magnitude doesn't silently rescale those.
- Use the codebase's gravity convention (cf. `lateral_view`'s `g·cos(theta)`; reuse a named `G`/gravity constant if one exists, else 9.81 m/s² as a named module constant — do not scatter magic 9.81s).

## Single canonical convention
Prefer ONE place that converts g-coefficient → m/s² (e.g. make `_compute_speed_caps` and the Gsat fallback reuse `LateralParameters.lateral_capability` / a shared grip helper rather than re-deriving the formula inline). If a full de-duplication is too large for this gate, at minimum make the scaling factor a single named constant applied identically everywhere, and note the inline duplication as a triage candidate.

## Close Criteria
- ×g applied and spurious ρ dropped across all lateral consumers; ceiling + Gsat + fallbacks unit-consistent; no double-correction.
- Truth anchor: `LateralParameters.lateral_capability` / the sim cap at the Monaco/VER tunnel (κ≈0.011, v≈63) yields ~63–66 m/s (a NEW or updated test asserts this against the real apex).
- Re-baselined physics tests assert physical values; the full g2 verification suite is green.
- Single canonical scaling; no dual convention.

## Allowed Scope
`src/physics/physics_data_models.py`, `src/physics/physics_simulator.py`, `src/physics/capability_envelope.py`, `src/physics/friction_coupling.py`, `src/physics/apex_extract.py`, and their tests under `tests/unit/physics/`. A named gravity constant may be added to the appropriate physics module.

## Specific Exclusions
- No change to `LateralView`/`lateral_view.py` (the producer is the correct g-unit source of truth).
- No change to the store schema or the comparison method in `regime_utilization.py` (the comparison is NOT the bug — confirmed at G1). You may add/adjust a regime_utilization test that now expects un-pinned U, but do not change its logic.
- No evo/data-region files. No store writes.

## Constraints
- `py` launcher; run from repo root. Physics-model change → highest-applicable L1–L4 truth evidence, units/bounds explicit.
- `constraint:physics_region_no_evo_import` (verified posture — keep it).
- Store/cache read-only via absolute main-checkout paths if you load a real session for the truth anchor (`C:/Programs/f1Brainz/data/physics_estimates.db`, cache `C:/Programs/f1Brainz/data/telemetry`).

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `physics_data_models.LateralParameters.lateral_capability`, `physics_simulator._compute_speed_caps`/`_gsat_ceiling`, `capability_envelope`, `friction_coupling`, `apex_extract`. `struct:physics.layer2` — `lateral_view` (producer, g-unit truth).
- **Capability:** lateral capability ceiling (feeds the ideal-lap sim corner caps AND the #485 production envelope).
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (this units fix parallels the #518 G5 `p_max` fix recorded there — it will get a sibling note at reconcile); `decision:c1_driver_utilization_design`.
- **Evidence:** corrected Monaco tunnel cap ~63–66 m/s vs VER 63.3; physics suite re-baselined to truth; corner-regime U un-pins from 2.0 (verified next gate).

## Required Evidence
- The diff across the lateral consumers + the named gravity constant.
- A truth-anchored test (Monaco-tunnel cap ~63–66 m/s, or an equivalent ~3–5g lateral assertion) — show it FAILS pre-fix, passes post-fix.
- Full g2 verification command green, with a note on which test expectations were re-baselined and why each new value is physical.
- The audit findings for ceiling/friction_coupling/apex_extract/fallbacks (what you found, what you changed, what was already correct).

## Verification Commands
```bash
py -m pytest tests/unit/physics/test_physics_data_models.py tests/unit/physics/test_capability_envelope.py tests/unit/physics/test_capability.py tests/unit/physics/test_lateral_envelope.py tests/unit/physics/test_physics_simulator.py tests/unit/physics/test_friction_coupling.py tests/unit/physics/test_apex_extract.py tests/unit/physics/test_ideal_lap_top_speed_invariant.py tests/unit/physics/test_regime_utilization.py -q
py -m src.utils.simplification_limits   # on touched src/ paths if applicable
```

## Suggested Model Tier
Stronger (opus) — shared production physics, a re-baselining-to-truth trap, and a multi-site audit (ceiling units, fallbacks, double-correction) that needs careful reasoning.

## Authority
The bug, fix direction (×g + drop ρ), and fix-at-source scope are DECIDED (user "fix the bugs", G1 review). You own: the exact single-canonical-location refactor choice, the ceiling-units resolution, and which test expectations are re-baselined. Do not change the comparison method or the producer; do not expand beyond the lateral consumers without surfacing.

## Stop Conditions
Stop and return if: a consumer turns out to already compensate in a way that makes the "single convention" ambiguous (surface it); the ceiling units cannot be determined from source; or the fix would require touching the producer or a non-physics region.

## Return Format
IMPLEMENTER_RESULT to exactly `.agent-work/522-phase-align-utilization/crew-handoffs/g2-implement-result.md`: completed slice, files changed, the audit findings (ceiling/friction/apex/fallbacks), test mode satisfied + which expectations re-baselined (with the physical justification), the truth-anchor result, evidence/commands, assumptions, stop conditions, out-of-scope observations, workflow feedback.
