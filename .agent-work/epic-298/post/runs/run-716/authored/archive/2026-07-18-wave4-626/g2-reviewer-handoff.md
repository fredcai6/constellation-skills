# Reviewer Handoff

## Gate
`g2` — Layer 1 explained physics (density from measured pressure + mass/fuel) with σ + falsifiable Mexico↔Monaco density check.

## Survey State Location
`.agent-work/wave4-626/g2-review/review.json`.

## What Was Implemented
`src/physics/weekend_state/layer1_physics.py` + `tests/unit/physics/weekend_state/test_layer1_physics.py` (18 tests). Removes a density(measured store `rho`)+mass component from the 11 axes: 7 density-sensitive axes (3 CdA + max_power + 3 aero-slope companions, grounded in `estimate_store.py` SYSTEMATIC_FLOOR), 4 mass-normalized accel axes as code-enforced no-ops (explained==0, residual==raw). Validated store `rho` bit-identical to `moist_air_density_from_pressure` on the measured pressure from `telemetry_store.tele_weather` (NOT f1_data.weather, which lacks Pressure — implementer corrected this). Mexico↔Monaco: density correction halves the normalized gap (drag |z| 2.51→1.63, power 1.66→0.85, 90-95% car-seasons improved) but doesn't close to <1σ on all — reported as honest setup-confound residual. Result: `.agent-work/wave4-626/g2-implementer-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree; `git status --porcelain` then read `src/physics/weekend_state/layer1_physics.py` and its test directly (untracked).

## Task Statement
Build Layer 1 = explained-physics removal with σ + a FALSIFIABLE density check. Full task: `.agent-work/wave4-626/g2-implementer-handoff.md`.

## Close Criteria (each a review check)
- Density input is the MEASURED `rho` (validate the implementer's claim that store rho ≈ `moist_air_density_from_pressure` — re-run their validation or spot-check one session); NOT fixed RHO=1.2, NOT altitude lookup.
- Residual = axis − explained; σ propagated honestly (axis `_sigma` + model uncertainty; inflated where `rho_is_fallback=1`). The 4 mass-normalized axes are genuine no-ops (explained==0 exactly).
- The Mexico↔Monaco check is FALSIFIABLE (a real pass/fail with a failure mode), computed on shared constructors, in log-space, and the implementer did NOT force it to <1σ — the honest "reduces but setup-confound remains" reporting is acceptable and correct; verify it's not confirmatory-by-construction (density genuinely COULD have failed to reduce the gap).
- Honest magnitude: if Layer 1 is small on well-normalized axes, that is reported, not inflated.
- No evo import; no `data/*.db` staged.

## Allowed Scope
`src/physics/weekend_state/layer1_physics.py`, its test.

## Specific Exclusions
No Layers 2/3/4; g1 files/estimator/evo/config untouched. (The telemetry_store data-source path is outside your worktree DB — Commander-verified, note-not-block.)

## Constraints the Implementation Must Respect
- Density from measured pressure only; log-space cross-track comparison; σ explicit; `constraint:physics_region_no_evo_import`; absolute DB paths; no `data/*.db` commit.

## Map Anchors (inbound)
- Structural: `layer1_physics.py` (NEW); `environment.moist_air_density_from_pressure`.
- Capability: explained-physics removal with σ.
- Constraints: measured-pressure density; no evo import.
- Decision: density is modelable physics (Pre-Ruling 3) — EXPLAIN Mexico≠Monaco.
- Evidence: falsifiable Mexico↔Monaco residual-consistency check.

## Evidence Produced
`py -m pytest tests/unit/physics/weekend_state/test_layer1_physics.py -q` → 18 passed (commander re-ran: 18 passed). Mexico↔Monaco numbers + rho validation in the implementer result.

## Suggested Model Tier
Stronger — physical-reasoning gate; verify the density handling is genuinely physical and the falsifiable check has a real failure mode.

## Stop Conditions
BLOCK if: density is not the measured value, σ is not propagated, the Mexico↔Monaco check is confirmatory-by-construction (no failure mode) or was massaged to pass, or an evo import / data/*.db staged.

## Return Format
Return REVIEW_RESULT to `.agent-work/wave4-626/g2-reviewer-result.md`: verdict (APPROVE/BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
