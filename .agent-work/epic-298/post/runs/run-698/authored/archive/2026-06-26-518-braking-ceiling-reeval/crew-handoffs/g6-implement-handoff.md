# Implementer Handoff

## Gate
g6 (RE-PLANNED) — Re-run C1 on the FIXED simulator + updated verdict. The G5 units fix made the
ideal lap physical; this is the real test of #518's premise (does a physical ideal lap + the
recalibrated ceiling un-clip braking/fast-corner?). **This is the run's HEADLINE deliverable; the
user wants to evaluate it.**

## Task
1. **Re-run the C1 dashboard on the fixed simulator** for the 4 RBR cases on BOTH stores (the G5 fix
   is in `car_prior`, so BOTH OLD and WIRED now produce a physical ideal lap):
   `py scripts/driver_utilization_dashboard.py --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42 --db data/physics_estimates.db`
   and `--db data/physics_estimates_g3wired.db`. Same seed/mc as G4 for comparability.
2. **Build the three-way comparison** per regime per case: **G4 PRE-FIX** (aphysical sim — u_braking/
   u_fast pinned at 2.0; from the G4 VERDICT.md / CSVs) → **G6 POST-FIX OLD** → **G6 POST-FIX WIRED**.
   The key questions: (a) does u_braking / u_fast_corner now UN-CLIP from 2.0 on the fixed sim? (b) are
   the regimes now physical (≤1) and do they separate? (c) does the WIRED (recalibrated braking) ceiling
   differ from OLD on the fixed sim — i.e. does the #518 braking recalibration now matter?
3. **Updated VERDICT.md** (overwrite/supersede the G4 one, but PRESERVE the G4 numbers as the
   pre-fix reference): per-regime GO/CONTEXTUAL/NO-GO on the FIXED sim, with the deciding
   pre-fix→post-fix→OLD-vs-WIRED numbers and honest caveats (RBR-only scope; impure split; the
   lap-sampling σ already first-class from G4).
4. This is **verdict-producing, honest** — if regimes STILL don't separate / clip even on the physical
   ideal lap, report that plainly (it would mean the U-metric or the regime comparison has a further
   issue beyond the sim top-speed). Do not force a GO.

## Protected Intent
The verdict must follow honestly from the re-run numbers. The G5 fix is in place (don't re-fix it).
Single canonical ideal-lap path, `split_is_impure=True`, same seed/mc as G4 for apples-to-apples.

## Test Mode
Inspection + re-run (no new production code expected — the dashboard `--db`/`--cases` + lap-sampling σ
already landed in G4). If you DO touch code, test-after. Keep `py -m pytest tests/unit/physics/ tests/unit/test_utilization.py -q` green.

## Close Criteria
- Both stores re-run on the fixed sim for the 4 RBR cases (4/4 ok each, or honest per-case errors).
- The pre-fix→post-fix comparison table + an explicit statement: did u_braking/u_fast_corner un-clip?
- Updated VERDICT.md with per-regime GO/CONTEXTUAL/NO-GO on the fixed sim + the deciding numbers +
  the G4 pre-fix numbers preserved as reference.
- `py -m pytest tests/unit/physics/ tests/unit/test_utilization.py -q` green; simplification clean if any code touched.

## Allowed Scope
- `scripts/driver_utilization_dashboard.py` ONLY if a small fix is needed to run both stores cleanly
  (prefer not to). `reports/physics/` (gitignored CSVs). `.agent-work/518-braking-ceiling-reeval/VERDICT.md`.
- `src/physics/utilization/` ONLY if a genuine bug blocks the re-run (surface it first).

## Specific Exclusions
- Do NOT re-fix the simulator (G5 done) or change `car_prior` / the capability fits / the store.
- Do NOT change `regime_utilization` thresholds / `U_CLIP_MAX` / the lap-sampling σ (G4 done).
- Do NOT edit `docs/architecture/**` (reconcile owns the map).
- Do NOT repopulate the store (other-4 constructors remain the documented continuation).

## Constraints
- `py` not `python`; offline cache; single canonical ideal-lap path; `split_is_impure=True`.
- `constraint:physics_region_no_evo_import`. Verdict honest, not forced.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `driver_utilization_dashboard.py`, `regime_utilization.py`, `car_prior.py` (read-only, fixed in G5).
- **Decision anchors:** `decision:c1_driver_utilization_design` (Review Trigger), `decision:ideal_lap_sim_two_sided_evaluator` (the ideal-lap-as-ceiling contract — now finally a PHYSICAL ceiling; the G5 fix is the material change).
- **Evidence:** u_braking/u_fast_corner un-clip (or honest report); dashboard regenerates on the fixed sim.

## Exact seams (verified)
- Dashboard: `--cases "GP:DRV,..."`, `--db <store>`, `--mc-samples`, `--seed` (all added in G4).
  `characterize_cases(cases, store_df=EstimateStore(db).load(year=2023,status="ok"), cache=_CACHE, n_mc_samples=50, seed=42)`.
- G4 pre-fix numbers (the reference): VERDICT.md / `reports/physics/driver_util_subset_2023.csv` (OLD pre-fix)
  + `..._g3wired.csv` (WIRED pre-fix) — but NOTE those CSVs were generated PRE-G5-fix; regenerate fresh now.
  The G4 VERDICT.md table (u_braking/u_fast = 2.000 everywhere; u_straight Italy 0.578→0.712) is the pre-fix baseline.
- Stores: WIRED `data/physics_estimates_g3wired.db` (RBR wired), OLD `data/physics_estimates.db`. Only RBR wired — run RBR cases only.

## Data Locations (absolute; main checkout)
- Stores under `C:/Programs/f1Brainz/data/`; cache `C:/Programs/f1Brainz/data/telemetry` (offline). Reports → `reports/physics/` (gitignored).

## Required Evidence
- Both-store dashboard runs on the fixed sim (4/4 ok); the pre-fix→post-fix per-regime table.
- VERDICT.md updated with the per-regime verdict + deciding numbers.
- `py -m pytest tests/unit/physics/ tests/unit/test_utilization.py -q` green.

## Suggested Model Tier
Stronger (Opus) — the headline verdict's interpretation (un-clip? physical? does the braking
recalibration now matter?) is a judgment that must be honest and right.

## Authority
- The verdict is verdict-producing (user-accepted). Call it honestly.
- If the regimes still clip on the physical sim, that's a real finding — report it (do not force GO).
- RBR-only scope stands; the other 4 constructors are the documented continuation.

## Stop Conditions
Stop and return if: the dashboard cannot run on the fixed sim; a genuine bug blocks the re-run; the
verdict cannot be supported by the numbers; scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g6-implement-result.md`:
the pre-fix→post-fix→OLD-vs-WIRED U table, the explicit un-clip statement, the updated per-regime
verdict, whether the #518 braking recalibration now matters on the fixed sim, test output, assumptions,
stop conditions, and **Workflow Feedback**.
