# Reviewer Handoff — G1 Diagnose review (#522)

## Gate
g1-review (verify a DIAGNOSIS, not code — verdict = is the diagnosis SOUND and well-evidenced)

## What Was Implemented
A diagnosis (no production code) determining the root cause of the C1 braking/fast-corner utilization clip (`U` pinned at 2.0). The implementer concluded **(b) under-called ideal-lap lateral caps** and **rejected (a) misregistration**. Artifacts (all under `.agent-work/522-phase-align-utilization/`): `DIAGNOSIS.md`, `diag_alignment.py`, `fig_alignment_monaco_ver.png`, `crew-handoffs/g1-implement-result.md`.

## How to Inspect the Diff
No src/ diff. Read `DIAGNOSIS.md` and `crew-handoffs/g1-implement-result.md`; regenerate the numbers with `py .agent-work/522-phase-align-utilization/diag_alignment.py` from repo root `C:/Programs/f1Brainz`.

## Task Statement
Discriminate (a) corner misregistration (real lap registered by progress-fraction vs ideal+curvature on true distance) vs (b) genuinely under-called ideal corner-speed caps, on RBR 2023-Q corners, with a true-distance-registration re-computation as the decisive test. Recommend a fix approach.

## Close Criteria (each a review check)
- The traces in the figure/table are REAL and regenerable from `diag_alignment.py` (run it; numbers match `DIAGNOSIS.md`).
- The **(a) rejection** is justified: true-distance registration (`np.interp(grid_dist, driver_distance, driver_speed)`) genuinely does NOT lower the braking/fast-corner ratios (the table shows U_truedist ≈ U_progress). Confirm this is real, not an artifact of how the implementer recomputed it.
- The **(b) confirmation** is justified: the ideal-lap lateral cap really is far below VER's actual corner speeds (tunnel cap ~16 m/s vs VER ~63 m/s), and the canonical ideal-lap path (`PhysicsSimulator.simulate_lap` from `car_prior` ceiling, NOT a reinvented sim) was used.
- The recommended fix follows from the finding.

## SCOPE-DETERMINING PROBE (the key review value-add — do this carefully)
The implementer attributed the A0≈2.64 m/s² lateral under-call to "cross-session pooling dilution" but did NOT verify it. This distinction governs whether #522 is a small fix or a capability rebuild, so resolve it as far as you can:

1. **Raw per-session A0.** `g_track=1.0`, `k_tire=0.0` (neutral) in `car_prior._assemble_lateral`, so the consumed lateral grip is exactly the stored `A0`. Open `C:/Programs/f1Brainz/data/physics_estimates.db` (table `session_estimates`) READ-ONLY (`sqlite3` `file:...?mode=ro`) and pull `A0, A2, A0_sigma` for Red Bull Racing across its 2023-Q rows (especially Monaco, round_idx≈6, and 2-3 other rounds). **Are all per-session A0 ≈ 2.6, or does Monaco's own session show a higher A0 that the causal pool dilutes?** (Pool = causal mean over round_idx ≤ target via `_assemble_lateral`/`_causal_pool`.)
2. **Physical-scale sanity.** The grip model is `G(v) = A0 + A2·ρ·v²` (m/s²). A 2023 F1 car sustains ~30–50 m/s² (3–5g) peak lateral. Does the stored A0/A2 reproduce ANY plausible peak (e.g. at v=60 m/s), or is it uniformly ~5–10× too low across BOTH terms? A clean ~constant multiplicative gap on both terms points at a **units/assembly bug** (cf. #518 G5: store `p_max` watts injected into a W/kg slot); a single-term or track-varying bias points at **measurement/pooling**.
3. **Cross-check the measured frontier.** If feasible, run the per-session lateral fit directly on VER's Monaco 2023-Q lap (`src/physics/layer2/session_lateral.py` / `lateral_view.py` — `LateralView.fit`) and compare its apex-grip to the stored A0. If the direct measured frontier is physical (~15–40 m/s²) but the stored/pooled A0 is 2.6 → store-mapping or pooling problem; if the direct fit is ALSO ~2.6 → the lateral measurement itself under-calls.
4. **Conclude** in the REVIEW_RESULT: units/assembly bug | measurement under-call | pooling dilution | undetermined — with the evidence. This feeds the human decide-fix checkpoint.

## Allowed Scope
Read-only inspection of `src/physics/`, the store, the FastF1 cache (`C:/Programs/f1Brainz/data/telemetry`), and the work-area artifacts. You MAY write a throwaway probe script under `.agent-work/522-phase-align-utilization/` to pull store values / run a lateral fit. No src/ or committed scripts/ edits.

## Specific Exclusions
No production code change. No store writes. Do not implement the fix.

## Constraints the Implementation Must Respect
- Canonical ideal-lap path only (no reinvented sim).
- `py` launcher; store/cache read-only via absolute main-checkout paths.
- Physics rigor: units explicit.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` (regime_utilization, car_prior `_assemble_lateral`), `struct:physics` (physics_simulator `_compute_speed_caps`), `struct:physics.layer2` (lateral_view/session_lateral — the measured frontier).
- **Capability:** per-regime driver utilization; the lateral capability ceiling feeding it.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (Gsat fallback owns `lateral.ceiling=None`); `decision:c1_driver_utilization_design`. A units bug here would be a **decision candidate** (parallels the #518 G5 fix recorded on the ideal-lap anchor).
- **Evidence expectations:** (a) rejected ⇔ true-dist ratio ≈ progress ratio; (b) confirmed ⇔ caps physically below real corner speeds.

## Evidence Produced
`DIAGNOSIS.md` table (per-corner v_ideal/v_real/curvature/ratio both registrations), regime means (braking U 1.884→1.870, fast_corner 1.994→1.994), the A0/A2 cap analysis. Regenerate via the script.

## Suggested Model Tier
Stronger (opus) — this gate re-scopes the issue and overturns the prior (#518) narrative; the units-vs-dilution probe needs careful, independent physics reasoning.

## Stop Conditions
Return BLOCK if: the numbers don't regenerate, the (a)/(b) call is not supported by the regenerated evidence, or the canonical path was not used. (Being unable to fully resolve probe #3 is NOT a block — report it as "undetermined" with what you found.)

## Return Format
REVIEW_RESULT: verdict (APPROVE = diagnosis sound / BLOCK), per-check findings, the **units-vs-dilution conclusion** with evidence, blockers, out-of-scope observations, workflow feedback. Write it to `.agent-work/522-phase-align-utilization/crew-handoffs/g1-review-result.md`.
