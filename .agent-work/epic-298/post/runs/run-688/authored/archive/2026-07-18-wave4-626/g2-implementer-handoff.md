# Implementer Handoff

## Gate
`g2` — Layer 1: explained physics (density from measured pressure + mass/fuel) with σ + falsifiable Mexico-vs-Monaco density check.

## Task
Build `src/physics/weekend_state/layer1_physics.py`: the deterministic-ish explained-physics layer of the four-layer weekend-state model. It takes the g1 frame (11 axis estimates per car-weekend + `_sigma`, plus `rho`, `rho_is_fallback`, `mass_kg_assumed`) and produces, per car-weekend and per axis: an **explained-physics component**, a **residual** (`axis − explained`), and an **honest σ** for the residual (propagate the axis `_sigma` + the density/mass model uncertainty; inflate σ where `rho_is_fallback=1`).

## Key data facts (verified this run — use them)
- The store's `rho` column IS the measured-pressure air density, per weekend (constant across the ~10 constructors in a weekend), `rho_is_fallback=0` = measured/trusted. Mexico ρ≈0.90–0.92, Monaco ρ≈1.16–1.20 (~24% difference). So the layer's density input is the store's measured `rho` — that IS "density from measured pressure," NOT fixed RHO=1.2, NOT the buggy altitude lookup.
- VALIDATE that `rho` equals `src.utils.environment.moist_air_density_from_pressure(pressure_pa, air_temp_c, humidity_pct)` on 2–3 sessions using measured weather from `C:/Programs/f1Brainz/data/f1_data_<year>.db` (FastF1 `Pressure` is mbar → ×100 for Pa; the fn raises if you pass mbar). This proves the store's rho is the measured-pressure density and grounds the layer.
- `mass_kg_assumed` is the fuel/mass assumption used per row — the mass/fuel input.

## Modeling note (be honest about magnitude)
The 11 axes are already-fit CAPABILITY estimates (e.g. `drag_area_closed_m2` is a CdA in m², `max_power_w` in W) and the estimator ALREADY used measured ρ when fitting them. So Layer 1's explained-physics component is NOT "drag ∝ ρ" on a raw force — it is the RESIDUAL density/mass leakage that survives into the capability estimates (the `SYSTEMATIC_FLOOR` in `estimate_store.py` floors CdA/P_max at 4% precisely for this shared ρ/altitude systematic). Model each channel's residual density-sensitivity (drag/power channels carry it most; braking-aero-slope least — see x4's per-axis ratios) and the mass/fuel sensitivity, remove them, carry σ. If for well-ρ-normalized axes this layer is near-a-no-op, that is an HONEST finding to report (it feeds the g5 per-layer ablation on whether Layer 1 earns its keep) — do NOT manufacture a large explained component that isn't physically there.

## Protected Intent
Density is modelable PHYSICS, not noise (Pre-Ruling 3). The layer must EXPLAIN cross-track density differences physically (Mexico≠Monaco is known truth), not subtract them as a nuisance. Honest σ per layer feeds Phase-3 σ-honesty.

## Test Mode
Test-after allowed; the load-bearing test is the falsifiable density check.

## Close Criteria
- `layer1_physics.py` produces, per car-weekend×axis: explained component + residual + honest σ; σ inflated where `rho_is_fallback=1`.
- Density input is the measured `rho` (validated ≈ `moist_air_density_from_pressure` on 2–3 sessions) — NOT fixed/altitude. A test asserts the validation holds within a small tolerance.
- **Falsifiable density secondary check (cold-critic F6):** implement it as a RESIDUAL-CONSISTENCY test with a numeric tolerance — after density handling, the SAME constructor's drag/power residual at Mexico vs Monaco AGREES within its propagated σ (a real pass/fail: if density were mishandled/ignored, the raw ~24% ρ gap would blow the residual apart → the test would FAIL). Acknowledge in a comment + the result that Mexico differs from Monaco in aero trim + track too (setup confound), so a residual gap is not naively blamed on density; pick constructors present in both.
- `test_layer1_physics.py` passes: σ propagation, measured-rho validation, Mexico↔Monaco residual consistency.
- No evo import; no `data/*.db` staged.

## Allowed Scope
`src/physics/weekend_state/layer1_physics.py`; `tests/unit/physics/weekend_state/test_layer1_physics.py`. You MAY read (not modify) `frame.py`/`floor.py` from g1 and `src/utils/environment.py`.

## Specific Exclusions
Do NOT build Layers 2/3/4 (g3/g4). Do NOT modify g1 files, the estimator, evo, or config. Do NOT commit/modify `data/*.db`.

## Constraints
- Python `py`. Density from measured pressure only (`environment.moist_air_density_from_pressure`) — cite its signature `(pressure_pa, air_temp_c, humidity_pct) -> kg/m³` (raises ValueError if pressure_pa < 10000, i.e. mbar passed).
- Density is MULTIPLICATIVE — compare/normalize in LOG-space where you compare cross-track (density memory).
- Absolute paths into `C:/Programs/f1Brainz/data/*` for DBs.
- `constraint:physics_region_no_evo_import`. Every layer carries explicit σ.

## Map Anchors (inbound)
- Structural: `src/physics/weekend_state/layer1_physics.py` (NEW); `src/utils/environment.moist_air_density_from_pressure`.
- Capability: explained-physics removal (density+mass) with σ.
- Constraints: measured-pressure density not fixed/altitude; no evo import.
- Decision: density is modelable physics (Pre-Ruling 3) — EXPLAIN Mexico≠Monaco.
- Evidence: density layer explains Mexico(low-ρ) vs Monaco(sea-level) via a falsifiable residual-consistency test.

## Deliverable Path Check
- Committed: `src/physics/weekend_state/layer1_physics.py`, `tests/unit/physics/weekend_state/test_layer1_physics.py` (not gitignored). New files untracked until staged.

## Required Evidence
- `py -m pytest tests/unit/physics/weekend_state/test_layer1_physics.py -q` → pass.
- Printout of the Mexico vs Monaco residual + σ for 2-3 shared constructors, showing agreement within σ (and the raw pre-density gap for contrast).
- The measured-rho ≈ moist_air_density_from_pressure validation numbers.

## Verification Commands
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_layer1_physics.py -q
```

## Suggested Model Tier
Stronger — the density modeling + falsifiable check need real physical reasoning, not a divide-by-rho reflex.

## Authority
Density = measured pressure (frozen). The exact per-channel density-sensitivity model is yours to choose but must be physical + carry σ + honest about magnitude.

## Stop Conditions
Stop/return if: measured `rho` cannot be validated against the environment fn (report the discrepancy — may be a data-quality float), or the Mexico/Monaco residual gap cannot be brought within σ even with correct density handling (that is a real finding — report it; it may mean the density leakage is entangled with setup, a float candidate).

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/wave4-626/g2-implementer-result.md`: completed slice, files changed, test output, the Mexico↔Monaco residual numbers, the rho validation, honest note on the layer's magnitude, assumptions, stop conditions, out-of-scope observations, workflow feedback.
