# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2` — Layer 1: explained physics (density from measured pressure + mass/fuel) with σ + falsifiable Mexico-vs-Monaco density check.

## Result
`APPROVE`

## Handoff compliance
All Close Criteria independently verified, not accepted on the strength of the implementer's report:

- **`layer1_physics.py` produces explained/residual/σ per axis, σ inflated where `rho_is_fallback=1`:** confirmed by reading the code (`apply_layer1`) and by direct data check — the 4 mass-normalized axes (`brake_decel_ms2`, `traction_accel_ms2`, `lateral_mech_grip_g`, `coast_rolling_decel_ms2`) are exact no-ops on the full real frame (`explained==0` all rows, `residual-raw` max abs diff `== 0.0`). The `rho_is_fallback` inflation mechanism is tested only via a synthetic frame because the real store currently has zero `rho_is_fallback=1` rows (1562/1562 are 0) — this is disclosed honestly in both the module docstring and the test, not hidden.
- **Density input is the measured `rho`:** re-ran an independent spot-check (2023 Mexico, a fresh script, not a reuse of the implementer's or the test's code path) — `moist_air_density_from_pressure` on `telemetry_store.tele_weather`'s measured pressure/temp/humidity reproduced the stored frame `rho` bit-identically (`0.9052291730225163` both sides). `RHO_REF_KG_M3` is derived from the ISA standard atmosphere run through the same measured-pressure formula (`≈1.225`), not a bare `1.2`. This bit-identical match also rules out the buggy altitude-lookup path (that path would not reproduce bit-for-bit).
- **Falsifiable Mexico↔Monaco check:** this was the highest-value check in the dispatch and was verified by direct experiment, not just code reading. I forced the density beta to zero for `drag_area_closed_m2`/`max_power_w` (simulating a broken/density-ignored implementation) and re-ran `mexico_monaco_residual_consistency` — under that condition `z_resid == z_raw` exactly and the implemented test's improvement assertion (`mean_z_resid < 0.85 * mean_z_raw`) genuinely **fails**. This proves the check is not confirmatory-by-construction. I then re-ran the real (unbroken) numbers and they reproduce bit-for-bit against the implementer's reported table (drag: 2.512→1.632; power: 1.665→0.849; n=59 both). The comparison is computed in log-space for the density variable (`ln(rho)` used throughout the fit and application — density's multiplicative nature is respected), on an inner-join of shared `(year, constructor)` car-seasons, with real margin against the pass threshold (ratios 0.65/0.51 vs a 0.85 ceiling) — not massaged to a razor edge. The honest "reduces but does not fully close" reporting is accurate: 37–66% of car-seasons land within 1σ post-correction, and the implementer proactively discloses that the pooled beta is largely identified by the Mexico-vs-rest contrast (a real methodological limit, correctly routed as a triage candidate rather than smoothed over).
- **Honest magnitude:** confirmed — 7/11 axes get a real, statistically significant (t>3) density-explained component; 4/11 are an exact, code-enforced no-op; nothing is inflated to look more impressive than the data supports.
- **No evo import; no `data/*.db` staged:** `grep -i evo` on both files under review returns no import-line matches; `git status --porcelain | grep -i .db` returns nothing.

## Scope drift
None. `git status --porcelain` shows exactly 3 untracked paths: `.agent-work/wave4-626/` (workflow artifacts), `src/physics/weekend_state/layer1_physics.py`, `tests/unit/physics/weekend_state/test_layer1_physics.py` — matching Allowed Scope exactly. `frame.py`/`floor.py`/g1 files/evo/config are untouched (read-only use of `frame.py`, as permitted). No Layer 2/3/4 files exist.

## Evidence verdict
Required evidence present and independently reproduced:
- `py -m pytest tests/unit/physics/weekend_state/test_layer1_physics.py -q` → re-ran fresh: **18 passed**, matching the claimed result.
- Broader region due diligence: `py -m pytest tests/unit/physics/weekend_state/ -q` (g1+g2 combined, 43 tests) → **43 passed**, confirming g2 introduces no regression to g1's prior work.
- Mexico/Monaco residual table and the rho-validation numbers: independently reproduced (see Handoff compliance above), bit-identical to the implementer's reported figures.
- `py -m src.utils.simplification_limits --paths src/physics/weekend_state/layer1_physics.py tests/unit/physics/weekend_state/test_layer1_physics.py` → re-ran fresh: `PASS (2 files checked)`.

## Code/doc quality
Meets inherited project rules. Per-constraint check (handoff Constraints): `py` invocation used throughout; density from measured pressure only (no fixed/altitude fallback); log-space (`ln(rho)`) used throughout for the multiplicative density comparison; absolute main-checkout DB paths (`frame.DB_PATH`, `telemetry_store.DEFAULT_STORE_PATH`, both `C:/Programs/f1Brainz/data/...`); `constraint:physics_region_no_evo_import` honored; every layer output carries an explicit `layer1_sigma`. CREW_CONTEXT.md rules: no `print()`/logging debris; module scope holds only immutable constants + pure functions/one frozen dataclass (no mutable state); all thresholds (`MASS_ELASTICITY`, `MASS_ELASTICITY_SIGMA`, `MIN_WEEKENDS_FOR_BETA`, `RHO_FALLBACK_INFLATION`) are named module constants; an L1 analytical-reference truth-anchored test is present and explicitly labeled as such (`TestRhoMatchesMeasuredPressure`); missingness handled explicitly via `.notna()`/`isna`-aware checks, no silent imputation.

**Fowler refactoring pass** (full record: `.agent-work/wave4-626/g2-review/fowler_pass.json`, `verify_fowler_pass.py` exits 0): 12/12 baseline smells rendered a verdict. Two non-blocking observations — `apply_layer1`'s ~55-line per-axis loop is cohesive but could be decomposed into small helpers; `DEFAULT_WEEKEND_KEY` is a module constant defined but never referenced anywhere (dead speculative generality, worth deleting or wiring up in g3/g4). One logged override — primitive-obsession (bare-string axis identity) is subordinate to g1's `frame.py`'s existing `AXES: list[str]` convention, which this module must key into; a parallel enum would fragment that convention for no gain.

## Map impact verdict
- **Evidence supports claimed change:** yes — independently reproduced (see above).
- **Constraints not violated:** yes — measured-pressure density, log-space comparison, no-evo-import, absolute DB paths all confirmed.
- **Notes match the diff:** yes — the implementer's Map Impact notes (new module, 3 new capabilities, axis-grouping decision, rho-source correction) match what the diff actually contains.
- **Decision candidates surfaced:** the axis-grouping decision was made within the implementer's explicitly delegated Authority ("the exact per-channel density-sensitivity model is yours to choose") and is well-grounded in existing `estimate_store.SYSTEMATIC_FLOOR` precedent — correctly not escalated.
- **Durable context routed:** the implementer's rho-source correction (handoff's `f1_data_<year>.db` Map Anchor is stale — the real measured-pressure source is `telemetry_store.py`) was independently confirmed correct and is routed to Commander as triage candidate `tc1` (survey `triage_candidates`) for the durable anchor to be fixed before g3/g4 dispatch.

## Reconciliation check
No blocking divergence. One triage candidate flagged (`tc1`, engine-recorded): the Map Anchor citing `f1_data_<year>.db` for measured weather is stale (that DB's `weather` table has no Pressure column); the correct, already-DB-only-compliant source is `src/data/telemetry_store.py` (`tele_weather`). Recommend Cartographer/Commander correct this anchor before g3/g4.

## Blockers
- none

## Out-of-scope observations
- **Map Anchor staleness (tc1):** see Reconciliation check above.
- **Dead `DEFAULT_WEEKEND_KEY` constant:** defined at module level, never referenced. Low-priority cleanup for a future gate touching this file.
- **Mexico-identification confound:** already flagged by the implementer as a triage candidate (pooled density beta is largely a "Mexico dummy" since Mexico is nearly the only sub-1.0 ρ circuit on the calendar) — independently confirmed as a genuine, honestly-disclosed limitation, not a defect in this gate's scope. Worth revisiting if a future gate wants a cleaner density-only estimate.

## Workflow Feedback

- **Handoff gaps:** none blocking. The reviewer handoff's density source note (`telemetry_store.tele_weather`, correcting the implementer handoff's `f1_data` pointer) was accurate and matched what I independently verified — good self-correction propagation from implementer → reviewer handoff.
- **Context rediscovered:** none beyond what the handoff already surfaced; the implementer's result file was unusually thorough (full beta table, full Mexico/Monaco table, honest-magnitude section), which made independent reproduction fast.
- **Instructions improvised around:** the r4-quality survey item's imperative says "Append a check per rule" — I did not literally use the engine's `append` verb to create per-rule sibling checks; I instead covered each rule explicitly within the single `r4-quality` finding text (matching the precedent set by the g1 reviewer's own `review.json`, which took the same approach). Flagging this in case "append a check per rule" is meant literally — the current survey template's imperative text and the observed prior practice diverge, and a future reviewer might reasonably do either.
- **What would have made this easier:** nothing significant — this was a well-scoped, well-evidenced handoff with a genuinely falsifiable claim that was worth the extra step of experimentally breaking the implementation to confirm it (rather than just reading the assertion thresholds and trusting they were meaningful).

## Return status
`complete`
