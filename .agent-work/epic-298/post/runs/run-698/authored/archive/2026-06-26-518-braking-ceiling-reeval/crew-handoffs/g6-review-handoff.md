# Reviewer Handoff

## Gate
g6 (RE-PLANNED) — Re-run C1 on the fixed simulator + updated verdict (review). The headline:
braking/fast-corner did NOT un-clip even on the physical ideal lap; the binding constraint is a
longitudinal phase misalignment. Verify the re-run + the verdict are sound.

## What Was Implemented
No production code changed. The C1 dashboard was re-run on BOTH stores on the G5-fixed simulator for
the 4 RBR cases. Result: u_braking = u_fast_corner = 2.000 in 4/4 cases on BOTH stores (Δ vs G4 pre-fix
= 0.000). The G5 top-speed fix is confirmed live (ideal-lap top speed now ~333 km/h physical) but only
fixed the straight channel; the braking/fast clip persists due to a ~3.3–3.8× longitudinal phase
misalignment (v_ideal 17–25 m/s at apex vs v_real 63–66 m/s at the same grid index). #518's braking
recalibration (OLD vs WIRED) makes ≤0.04 difference. New finding: the now-physical (lower) ideal lap
mildly UNDER-calls straight speed → straight U crossed <1→>1 (Italy 0.71→1.07, GB 0.83→1.23). Updated
VERDICT.md (supersedes G4; VERDICT_G4_prefix.md preserves the G4 baseline).

## How to Inspect
```bash
cd /c/Programs/f1Brainz
git log --oneline -1           # G5 fix df46d840 live
git status --short             # expect NO src changes (re-run only); VERDICT.md + CSVs + result
```
VERDICT.md (updated) + VERDICT_G4_prefix.md + `crew-handoffs/g6-implement-result.md` + the two CSVs in `reports/physics/`.

## Close Criteria (each a review check)
- **Re-run reproduces:** independently run `py scripts/driver_utilization_dashboard.py --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42 --db data/physics_estimates_g3wired.db` (and OLD). Confirm u_braking/u_fast = 2.000 (still clipped) and the straight-U crossing (Italy ~1.07, GB ~1.23). Same seed/mc → deterministic.
- **G5 fix is live in the run:** confirm the ideal-lap top speed is now physical (~95 m/s) in this re-run (not the G4 aphysical 207) — the clip persists DESPITE the physical top speed (that's the key point).
- **Phase-misalignment finding is sound:** confirm (from the per-point data / the result) that v_ideal at the braking/corner grid indices is at-apex (~17–25) while v_real is ~63–66, giving the ~3.3–3.8× ratio → clip. (This corroborates the G4 reviewer's independent phase-misalignment finding.)
- **#518 braking recalibration irrelevance:** OLD vs WIRED Δ ≤0.04 everywhere, 0.000 on the clipped regimes — confirm.
- **Verdict honesty:** per-regime braking/fast/slow NO-GO, straight CONTEXTUAL→trending-NO-GO follows from the numbers; not forced; G4 pre-fix preserved as reference; RBR-only scope + impure split stated.
- **No exclusions touched:** no sim/car_prior/fits/store/threshold/docs changes (re-run only). `py -m pytest tests/unit/physics/ tests/unit/test_utilization.py -q` green (~629). Re-run inline.

## Allowed Scope / Exclusions
Re-run + VERDICT.md only. Flag if any src/sim/car_prior/store/threshold/docs/architecture changed.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — dashboard, regime_utilization, car_prior (read-only).
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — the ideal-lap-as-ceiling contract; the point-aligned v_real/v_ideal comparison is the binding flaw (note for reconcile/triage); `decision:c1_driver_utilization_design`.

## Suggested Model Tier
Bounded (Sonnet) — re-run reproduction + verdict-honesty check; the phase-misalignment was already
independently confirmed at G4. Escalate only if the re-run numbers don't reproduce.

## Stop Conditions
BLOCK if: the re-run numbers don't reproduce; the G5 fix is NOT live in the run (top speed still aphysical);
the verdict is forced/unsupported; production code was changed; tests don't reproduce.

## Return Format
Return REVIEW_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g6-review-result.md` with a
clear `verdict: APPROVE` or `verdict: BLOCK`, per-check findings incl. YOUR reproduced U numbers + the
ideal-lap top speed you measured, blockers, out-of-scope observations, and Workflow Feedback. (APPROVE =
the re-run + the honest NO-GO-persists verdict are sound.)
