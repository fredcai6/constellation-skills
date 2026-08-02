# Reviewer Handoff

## Gate
g4 — C1 driver-utilization re-eval on the recalibrated ceiling + lap-sampling σ + the headline
GO/CONTEXTUAL/NO-GO verdict (review). The verdict came back **NO-GO on braking + fast-corner** with
a project-redirecting diagnosis; your job is to independently confirm it is RIGHT.

## What Was Implemented
A `--db` (+`--cases`) arg on `scripts/driver_utilization_dashboard.py`; a lap-sampling σ term in
`regime_utilization.py` (`sigma_u_lapsampling_* = std(ratio[mask])/sqrt(n)`, `sigma_u_total_* =
sqrt(env²+lap²)`, envelope σ unchanged + separately reportable); an OLD-vs-WIRED run on the 4 RBR/VER
dashboard cases; and `VERDICT.md`. Headline: `u_braking` and `u_fast_corner` stay pinned at the
`U_CLIP_MAX=2.0` clip (Δ=0.000 in all 4 cases) on the wired ceiling — they do NOT un-clip. Only
`u_straight` responds (Italy +0.134, physical). Diagnosis: the clip is an ideal-lap shape/alignment
artifact (aphysical 206.9 m/s ideal top speed + longitudinal phase mismatch), NOT braking-frontier depth.

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git diff HEAD -- src/physics/utilization/regime_utilization.py src/physics/utilization/characterize.py scripts/driver_utilization_dashboard.py
git status --short
```
Verdict: `.agent-work/518-braking-ceiling-reeval/VERDICT.md`. Result:
`.agent-work/518-braking-ceiling-reeval/crew-handoffs/g4-implement-result.md`. CSVs (gitignored):
`reports/physics/driver_util_subset_2023.csv` (OLD), `..._g3wired.csv` (WIRED).

## Task Statement
Re-run C1 on the wired store vs OLD for the RBR cases, add the deferred lap-sampling σ, and produce an
honest per-regime GO/CONTEXTUAL/NO-GO verdict on whether the recalibrated ceiling un-clips braking/fast-corner.

## Close Criteria (each a review check)
- **The headline numbers reproduce.** Re-run both stores yourself:
  `py scripts/driver_utilization_dashboard.py --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42 [--db data/physics_estimates.db | --db data/physics_estimates_g3wired.db]`.
  Confirm `u_braking`/`u_fast_corner` = 2.000 on BOTH stores (Δ=0.000) and `u_straight` moves (Italy +0.134).
- **THE CRUX — independently verify the diagnosis (this is the most important check):** confirm the
  ideal lap is genuinely aphysical/mis-aligned, not a probe artifact. Probe the canonical sim for one
  case (e.g. Italy/VER): build the ceiling via `car_prior.build_car_ceiling`, run
  `PhysicsSimulator.simulate_lap`, and check the ideal-lap speed profile max (claim: ≈206.9 m/s ≈ 745
  km/h — aphysical; real lap maxes ≈95 m/s). Confirm that in the braking mask `v_ideal` (~25 m/s, at
  apex) ≪ `v_real` (~66 m/s) at the same grid index → ratio ≥2 → clip. If the ideal lap is aphysical,
  the NO-GO diagnosis (comparison artifact, not ceiling depth) is sound. If the ideal lap is actually
  physical, the diagnosis is wrong — BLOCK and explain.
- **Lap-sampling σ correct:** `std(ratio[mask])/sqrt(n)` per regime, combined in quadrature with the
  UNCHANGED envelope σ; envelope σ still separately reportable; the new unit tests are sound (SEM,
  quadrature, separateness, 1/sqrt(n) shrinkage). Re-run the σ tests.
- **Invariants preserved:** single canonical ideal-lap path (`EstimateStore → car_prior →
  CapabilityEnvelope → PhysicsSimulator`); `split_is_impure=True` on every row; no second inline sim;
  `car_prior` / braking wiring / `estimate_store` / `docs/architecture/**` UNTOUCHED.
- **Verdict honesty:** the per-regime GO/CONTEXTUAL/NO-GO follows from the numbers, not forced; the
  RBR-only scope is stated and does not soften the (method-level) headline.
- **Tests reproduce:** re-run `py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py tests/unit/test_utilization.py -q` + `py -m src.utils.simplification_limits` on touched paths inline; report real output.

## Allowed Scope (what the implementation touched)
`regime_utilization.py` (lap-sampling σ + dataclass fields), `characterize.py` (thread the fields),
`driver_utilization_dashboard.py` (`--db`/`--cases`), the two test files, gitignored reports + VERDICT.md.

## Specific Exclusions (flag if touched)
`car_prior.py`, braking wiring, `estimate_store.py`, any layer2 view, `docs/architecture/**` — must be unchanged.

## Constraints
- Honest covariance additive (lap-sampling σ NOT a replacement for envelope σ).
- Single canonical path; `split_is_impure=True`. `py` not `python`. Offline cache.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `regime_utilization.py`, `car_prior.py` (read-only), `characterize.py`; dashboard.
- **Decision anchors:** `decision:c1_driver_utilization_design` (its Review Trigger fired), `decision:ideal_lap_sim_two_sided_evaluator` (the ideal-lap-as-ceiling contract — note the aphysical-top-speed finding bears directly on it).
- **Decision pressure:** the diagnosis supersedes #510's "ceiling under-call" framing — if you confirm it, that's a significant decision candidate for reconcile/triage.

## Evidence Produced
- 4 RBR cases, both stores, 4/4 ok: u_braking/u_fast 2.000→2.000 (Δ0.000); u_straight Italy 0.578→0.712.
- Diagnosis probe: ideal [7.5, 206.9] m/s vs real [20.8, 95.3]; braking-mask v_ideal 25.1 vs v_real 65.6.
- 60 tests passed; simplification PASS (5 files).

## Suggested Model Tier
Stronger (Opus) — the verdict is the run's headline and its diagnosis redirects the project; the
aphysical-ideal-lap confirmation is a judgment that must be independently right.

## Stop Conditions
BLOCK if: the headline numbers do not reproduce; the aphysical-ideal-lap diagnosis is NOT confirmed
(ideal lap is actually physical/aligned); the lap-sampling σ is wrong or replaces the envelope σ; an
invariant (single path / split_is_impure) is broken; an excluded file was touched; tests don't reproduce.

## Return Format
Return REVIEW_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g4-review-result.md`
with a clear `verdict: APPROVE` or `verdict: BLOCK`, per-check findings, an EXPLICIT confirm/deny of the
aphysical-ideal-lap diagnosis (with your own probe numbers), blockers, out-of-scope observations, and
Workflow Feedback. (APPROVE = the re-eval + the NO-GO verdict + the diagnosis are sound; it does NOT
mean the regimes are GO.)
