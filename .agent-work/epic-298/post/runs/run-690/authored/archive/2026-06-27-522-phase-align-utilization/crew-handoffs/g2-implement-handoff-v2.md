# Implementer Handoff — G2 Lateral Units Fix v2 / REWORK (#522, Option A)

## Gate
g2-implement (REWORK after BLOCK). The first attempt fixed the SHARED consumer for g-units, which broke the legacy convention-A path (`sim_evaluator`, `fit_batch`) that the consumer is *correctly* written for. **New approach (user-decided): Option A — convert the g-unit store → the consumer's m/s² convention at the `car_prior` boundary, exactly mirroring the #518 G5 `p_max` fix; leave the shared consumer UNTOUCHED.**

## Why the first attempt was wrong (read before starting)
The shared `LateralParameters.lateral_capability` / `physics_simulator._compute_speed_caps` are fed by TWO live producers: (A) the legacy single-session `LateralEnvelopeFit`/`fit_session_full` in **m/s²** (`default_A0=30`), still used by the **current** `sim_evaluator` and `build_physics_fit_store`; and (B) the five-view `lateral_view`→`session_estimates` store in **g-units**, used by the C1 utilization path via `car_prior`. The consumer was originally written for convention A (m/s²), so it is CORRECT for the legacy path. The bug is only that convention B (the store) carries g-units into car_prior WITHOUT converting them — identical in shape to the #518 G5 `p_max` watts→W/kg bug, which was fixed at the **car_prior boundary**, not in the consumer.

## Step 1 — discard the entire first-attempt diff
The first attempt's changes are UNCOMMITTED on `feat/522-phase-align-utilization`. Discard them ALL (consumer edits + the 9 re-baselined test files) to return to the pre-g2 baseline:
```bash
git -C C:/Programs/f1Brainz status        # confirm the only modified paths are first-attempt files
git -C C:/Programs/f1Brainz checkout -- src/physics tests/unit/physics tests/known_answer tests/property
git -C C:/Programs/f1Brainz status        # clean of src/test edits; .agent-work artifacts preserved
```
After this, `physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py` and all those tests are back to their convention-A (m/s²) baseline. **Do NOT re-touch them.**

## Step 2 — implement Option A in `car_prior` only
In `src/physics/utilization/car_prior.py`, convert the g-unit store A0/A2 → the consumer's m/s² convention at the lateral assembly boundary (`_assemble_lateral`), mirroring the existing `_build_longitudinal` G5 conversion (`p_max/MASS_KG`, watts→W/kg, with a clear docstring).

**The conversion (exact — uses the same `air_density` that flows to the consumer):**
`build_car_ceiling` already computes `air_density = mean of causal rows' rho` (~line 510) and passes it to `CapabilityEnvelope.from_parameters(params, air_density, cfg)` and the sim. Thread that `air_density` into `_assemble_lateral` and convert:
- `A0_param = A0_mu * G`   (g-unit mechanical coefficient → m/s²; the dominant fix)
- `A2_param = A2_mu * G / air_density`   (so the consumer's `A2_param·ρ·v²` reproduces convention B's physical aero `A2_mu·G·v²` when `ρ = air_density` — and it IS the same `air_density`, so this is exact, not an approximation)
- Covariance transforms by the Jacobian `J = diag(G, G/air_density)`: `cov' = J · cov · Jᵀ` (i.e. `[0,0]×G²`, `[1,1]×(G/air_density)²`, off-diagonal `×G·(G/air_density)`). Apply to whichever covariance path `_assemble_lateral` uses (the diagonal `A0_sigma²/A2_sigma²` form AND the `_pick_representative_blob` 2×2 path).
- Use a single NAMED gravity constant. `src/physics/braking_fit.py` already defines `G_MS2 = 9.81` — import it (do not add a second). Leave a one-line comment + a `# TODO(#525)` noting this car_prior conversion is the localized Option-A patch that #525 will generalize to the producer or retire.

The producer (`lateral_view.py`), the store schema, the shared consumer, and `regime_utilization.py` stay UNTOUCHED.

## Close Criteria
- Only `src/physics/utilization/car_prior.py` (+ its test) changed in `src/`; the consumer files are byte-identical to baseline (`git diff` shows no change there).
- **Truth anchor (NEW location — the C1 path):** a test in `tests/unit/physics/test_car_prior.py` builds a ceiling from a g-unit store row (real range, e.g. A0≈3.2) and asserts the resulting lateral capability / corner cap at the Monaco tunnel (κ≈0.011) is ~63–66 m/s (vs VER's 63.3). RED before the car_prior conversion, GREEN after.
- **Convention A unbroken:** the reverted consumer tests (`test_physics_data_models`, `test_physics_simulator`, `test_capability_envelope`, etc.) pass UNCHANGED (convention A, m/s²) with NO re-baselining — proving the legacy/`sim_evaluator` path is intact.
- The FULL physics region is green (see Verification — do NOT use a narrow command; the first attempt's narrow g2 list hid a red region).

## Allowed Scope
`src/physics/utilization/car_prior.py` and `tests/unit/physics/test_car_prior.py`. Import (not redefine) `G_MS2` from `braking_fit`.

## Specific Exclusions
- NO changes to `physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py`, `lateral_view.py`, the store schema, `regime_utilization.py`, or any convention-A producer. (Those are #525 / out of scope.)
- No evo-region files. No store writes.

## Constraints
- `py` launcher; run from repo root. Physics-model change → truth-anchored evidence, units explicit.
- Store/cache read-only via absolute main-checkout paths (`C:/Programs/f1Brainz/data/physics_estimates.db`, cache `C:/Programs/f1Brainz/data/telemetry`) for the truth anchor.
- One canonical conversion location (car_prior `_assemble_lateral`), documented like the G5 `_build_longitudinal` docstring.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `car_prior._assemble_lateral`/`build_car_ceiling` (the conversion boundary; sibling of `_build_longitudinal` G5).
- **Capability:** lateral capability ceiling for the C1 ideal-lap path.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (G5 `p_max` boundary-conversion precedent recorded here; this is its lateral sibling), `decision:c1_driver_utilization_design`.
- **Evidence:** corrected C1-path tunnel cap ~63–66 m/s; convention-A consumer tests unchanged & green; #525 filed for the producer unification.

## Required Evidence
- `git diff` showing ONLY `car_prior.py` + `test_car_prior.py` changed in tracked code.
- The truth-anchor test RED→GREEN.
- Full physics-region command green, explicitly noting the consumer tests passed with NO re-baselining (convention A intact).

## Verification Commands
```bash
py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q
py -m src.utils.simplification_limits --paths src/physics/utilization/car_prior.py
```

## Suggested Model Tier
Stronger (opus) — covariance transform + the exact ρ-consistent conversion + breadth of verification (must prove convention A is unbroken).

## Authority
Option A (car_prior boundary conversion, consumer untouched) is DECIDED by the user. You own the exact covariance transform, the `air_density` threading, and the truth-anchor test. Do NOT touch the consumer or any producer; do not re-introduce the first attempt's approach.

## Stop Conditions
Stop and return if: `air_density` cannot be threaded into `_assemble_lateral` cleanly; the truth anchor cannot reach ~63–66 m/s with the consumer untouched (would mean the diagnosis is incomplete — surface it); or the conversion would require editing the consumer.

## Return Format
IMPLEMENTER_RESULT to exactly `.agent-work/522-phase-align-utilization/crew-handoffs/g2-implement-result.md` (OVERWRITE the v1 result): completed slice, files changed (should be just car_prior.py + test), the conversion + covariance math, truth-anchor RED→GREEN, the convention-A-unbroken evidence, full-region test result, assumptions, stop conditions, out-of-scope observations, workflow feedback.
