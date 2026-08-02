# Implementer Handoff

## Gate
g4 — Re-run the C1 driver-utilization characterization on the recalibrated (wired) ceiling, add
the deferred lap-sampling σ term to the utilization covariance, and produce an updated
GO/CONTEXTUAL/NO-GO readiness verdict per regime. **This is the run's HEADLINE deliverable.**

## Task
1. **Re-run C1** (`scripts/driver_utilization_dashboard.py` → `characterize.characterize_cases`) on
   the WIRED estimate store `data/physics_estimates_g3wired.db` (the G3 output — full causal history,
   wired braking) for the 10-case C1 subset, and compare against the OLD store
   `data/physics_estimates.db` (the #510 CONTEXTUAL baseline). The dashboard currently HARD-CODES
   `_DB = data/physics_estimates.db`; add a `--db` CLI arg (default = OLD for back-compat) so it can
   target either store, and run BOTH for the before/after comparison.
2. **Add the lap-sampling σ term** to `regime_utilization.py` (the deferred #510 G2 hook, documented
   in the `estimate_driver_utilization` Notes + the module "Honest covariance" docstring). The
   realised lap is a SINGLE best lap; its sampling noise is currently unmodelled. Add a per-regime
   lap-sampling σ = the standard error of the regime-mean ratio, `std(ratio[mask]) / sqrt(n_points)`,
   and combine it IN QUADRATURE with the existing envelope σ:
   `sigma_u_total = sqrt(sigma_u_envelope**2 + sigma_u_lapsampling**2)`. Keep the envelope σ
   separately reportable; the combined σ is the honest total. Update the dataclass + docstring; do
   NOT silently replace the envelope σ.
3. **Confirm the headline:** does `U_braking` / `U_fast_corner` still clip at the `U_CLIP_MAX = 2.0`
   ceiling (the #510 NO-GO), or do they now produce a physical (`≤ 1`, ideally separating) signal on
   the recalibrated ceiling? Report the per-regime OLD→NEW U shift for every case.
4. **Produce the verdict** — `VERDICT.md` in the work area with a per-regime GO / CONTEXTUAL / NO-GO
   readiness call and the deciding numbers. **Verdict-producing, NOT GO-guaranteed** (user-accepted):
   report honestly where it lands. The #509 done-done bar: full coverage · honest covariance ·
   single canonical path · traceable data→dashboard.

## Protected Intent
The re-eval must be apples-to-apples with #510 (same cases, same causal scope, single canonical
ideal-lap path `EstimateStore → car_prior → CapabilityEnvelope → PhysicsSimulator`). The verdict
must follow honestly from the numbers — a deeper ceiling should push `U` down off the 2.0 clip, but
whether it lands `≤ 1` and whether team/driver separate is the empirical question this gate answers.

## Test Mode
Test-after. Add a unit test for the lap-sampling σ term (synthetic: known ratio spread → known SEM →
known quadrature combination) and that the envelope σ is still reported separately. Keep the existing
`tests/unit/physics/test_regime_utilization.py` + `test_driver_utilization_dashboard.py` green.

## Close Criteria
- `--db` arg added to the dashboard; the wired store runs cleanly through `characterize_cases` for the
  10 cases (or honest per-case errors reported).
- Lap-sampling σ term added to `regime_utilization` (SEM-of-regime-mean), combined in quadrature with
  the envelope σ; envelope σ still separately reportable; dataclass + docstring updated; the "future
  lap-sampling hook" TODO is now resolved.
- A per-regime OLD→NEW U comparison table (all 10 cases) + a clear statement of whether
  `u_braking` / `u_fast_corner` un-clip from 2.0.
- `VERDICT.md` with per-regime GO/CONTEXTUAL/NO-GO + deciding numbers + honest caveats (incl. the
  impure split, the per-constructor scope if not all 5 wired).
- `py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py tests/unit/test_utilization.py -q` green; `py -m src.utils.simplification_limits` clean on touched paths.

## Allowed Scope
- `src/physics/utilization/regime_utilization.py` (lap-sampling σ term + dataclass field + docstring).
- `scripts/driver_utilization_dashboard.py` (`--db` arg; optional OLD-vs-NEW comparison helper).
- `src/physics/utilization/characterize.py` ONLY if needed to thread the σ (prefer not to).
- `tests/unit/physics/` (regime_utilization + dashboard tests), `reports/physics/` (gitignored),
  `.agent-work/518-braking-ceiling-reeval/VERDICT.md`.

## Specific Exclusions
- Do NOT modify `car_prior.py` (the causal ceiling builder), the braking wiring (G3, done), the
  EstimateStore schema, or any layer2 view. Do NOT re-populate the store (G3 owns that; if a
  constructor is unwired, report it — see Scope note).
- Do NOT edit `docs/architecture/**` (reconcile owns the map).
- Do NOT weaken `split_is_impure` (always True) or the single-canonical-ideal-lap-path invariant.

## Store scope note (IMPORTANT)
The G3 wired store may have all 5 C1 constructors wired (RBR + Ferrari/McLaren/Williams/Mercedes) OR
only RBR (the primary) if the continuation repop did not finish. **Check before running:** a
constructor's rows are "wired" if `fitted_at >= '2026-06-25'` for that constructor's r1-15. Run the
cases for the WIRED constructors and clearly mark any case whose constructor is still OLD-braking
(those would not reflect the recalibration). RBR (4 cases: Monaco/Italy/Great Britain/Singapore) is
the primary and is wired; the verdict's headline rests on RBR with the others as generality. State
the wired scope explicitly in VERDICT.md.

## Constraints
- `py` not `python`; offline cache only (`data/telemetry`); DB-only is not relevant here (physics
  telemetry path), but do not add live FastF1/Jolpica calls.
- Honest covariance first-class (lap-sampling σ is additive, not a replacement).
- Single canonical ideal-lap path; `split_is_impure=True` preserved.
- `constraint:physics_region_no_evo_import`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — `regime_utilization.py`, `car_prior.py` (read-only),
  `characterize.py`; `scripts/driver_utilization_dashboard.py`.
- **Capability:** per-regime driver utilization — the C1 re-eval consumer.
- **Decision anchors:** `decision:c1_driver_utilization_design` (its Review Trigger fires — ceiling
  recalibration changes which U are trustworthy); `decision:ideal_lap_sim_two_sided_evaluator`.
- **Evidence:** `u_braking`/`u_fast_corner` un-clip from 2.0 (or honest report they don't); dashboard
  regenerates from the wired store; lap-sampling σ in the covariance.

## Exact seams (verified from source)
- `scripts/driver_utilization_dashboard.py`: `_DB` (hard-coded, add `--db`); `_DEFAULT_CASES` (the 10
  cases: Monaco VER/LEC, Italy VER/NOR/ALB, Great Britain VER/NOR/HAM/ALB, Singapore VER);
  `store_df = EstimateStore(_DB).load(year=2023, status="ok")`;
  `characterize_cases(cases, store_df=, cache=_CACHE, n_mc_samples=50, seed=42)`; `rows_to_dataframe`.
- `src/physics/utilization/regime_utilization.py`: pure core `regime_utilization(distance, curvature,
  v_real, v_ideal, *, mc_speed_profiles=...)`; the `ratio = v_real / safe_ideal`; `_u_and_consistency`
  computes `U_r = mean(ratio[mask])` clipped to `[0, U_CLIP_MAX=2.0]`; `_sigma_u_from_mc_speeds` is the
  envelope σ. Add the lap-sampling σ alongside (it needs `ratio[mask]` + `n`). `RegimeUtilization` is a
  frozen dataclass — add the new field(s). `estimate_driver_utilization` Notes documents the hook.
- `src/physics/utilization/car_prior.py`: `build_car_ceiling(store_df, year, constructor, target_round,
  strictly_pre, config)` — the causal ceiling (do not modify).
- Stores: NEW `data/physics_estimates_g3wired.db`, OLD `data/physics_estimates.db`; table `session_estimates`.
- #510 baseline: the prior dashboard CSV (`reports/physics/driver_util_subset_2023.csv` if present) records the OLD U values; otherwise re-run on OLD via `--db`.

## Data Locations (absolute; main checkout)
- Wired store `C:/Programs/f1Brainz/data/physics_estimates_g3wired.db`; OLD `C:/Programs/f1Brainz/data/physics_estimates.db`.
- FastF1 cache `C:/Programs/f1Brainz/data/telemetry` (offline). Reports → `reports/physics/` (gitignored).

## Required Evidence
- `py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py tests/unit/test_utilization.py -q` (green) + simplification clean.
- The per-regime OLD→NEW U comparison table (10 cases) + the un-clip statement.
- `VERDICT.md` with per-regime GO/CONTEXTUAL/NO-GO + deciding numbers.
- The lap-sampling σ unit test output.

## Suggested Model Tier
Stronger (Opus) — the headline verdict needs an honest, well-reasoned GO/CONTEXTUAL/NO-GO judgment
from the numbers, plus a correct covariance addition.

## Authority
- The verdict is verdict-producing (user-accepted) — call it honestly; do NOT force GO.
- You decide the lap-sampling σ mechanics within scope. If the wired store is RBR-only, run RBR (the
  primary) and clearly scope the verdict; do NOT repopulate the store yourself.
- If a regime's U is still pathological (clips at 2.0) on the recalibrated ceiling, that is a real
  CONTEXTUAL/NO-GO finding — report it, don't paper over it.

## Stop Conditions
Stop and return if: the wired store cannot be read; the dashboard cannot run the cases; the lap-sampling
σ cannot be combined without breaking the envelope σ; allowed scope must be exceeded; the verdict
cannot be supported by the numbers.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g4-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence (the OLD→NEW U table with the KEY numbers:
did u_braking/u_fast_corner un-clip? per-regime σ incl. the new lap-sampling term), the per-regime
verdict, the wired-scope statement, assumptions, stop conditions hit, out-of-scope observations, and
**Workflow Feedback**.
