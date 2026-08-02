# Implementer Handoff — G4 period compound prior = cross-season (match real gold cycle)

## Gate
`g4` (run-enabling) — make the per-period gold cycle's compound-prior handling match the real gold cycle so
training loads succeed. The current period config sets `allow_same_season_compound_prior=true`, which forces
loading each train year's OWN prior; 2018's committed gold prior declares accepted_compounds=[C1..C5] but
only fitted beta_C3/C4/C5, so the strict loader raises "parameter_means lacks 'beta_C1'" and the gold cycle
aborts at module 0.

## Confirmed diagnosis (already verified by Commander — implement directly)
`load_time_safe_compound_prior(<period root>, target_year=2018, allow_same_season_research=False)` → OK
(resolves the complete 2024 prior, all C1-C5 betas) — exactly what the real gold cycle does.
With `=True` it strict-loads 2018's incomplete prior → fails. For target 2025, `False` → cross-season 2024
(zero 2025 data). So: set the period to `allow_same_season_compound_prior=false` and DO NOT build/place a
2025 same-season prior. Compound priors are then cross-season throughout — leakage-safe (zero 2025 compound
data) and identical to the promoted gold's compound handling. The model still trains on 2025 R1..N (the
core experiment is unaffected).

## Task
1. `pipeline.py::render_period_config`: change `allow_same_season_compound_prior = true` → `false`
   (update the surrounding comment to explain: cross-season prior, leakage-safe, matches gold; same-season
   as-of-N is set aside because the committed train-year priors (e.g. 2018) omit betas for unused compounds
   and the strict loader requires them).
2. `pipeline.py::_build_prior_root`: STOP attempting the as-of-N 2025 build. Always assemble the isolated
   period prior root with ONLY the copied 2018-2024 train-year priors (NO 2025 dir — so there is no
   possibility of consuming 2025 compound data). Return `PriorBuildResult(prior_mode="cross_season",
   prior_through_round=0)`. Remove the now-dead as-of-N build helper / its imports if unused. Keep the
   hard-fail if a gold train-year prior is missing.
3. Provenance: per-period `prior_mode` is now `"cross_season"` (P1-P3) and `"promoted_gold"` (P0); effective
   `prior_through_round=0` for cutoff periods. Ensure attestation still passes (0 < every race round) and the
   summary/MD reflect `cross_season`. (The earlier `as_of_n`/`cross_season_fallback` modes are no longer
   produced — drop or keep the constants as appropriate, but the runtime value is `cross_season`.)

## Protected Intent
Leakage-free (zero 2025 compound data), robust, and HONEST provenance. The gold cycle must load training
priors exactly as the real gold cycle does.

## Test Mode
`test-after allowed`. Adjust the prior-build tests to the new always-cross-season behavior; keep a test that
`_build_prior_root` produces no 2025 dir and records `cross_season`/0, and that a missing train-year prior
still hard-fails.

## Close Criteria
- Period config renders `allow_same_season_compound_prior = false`.
- `_build_prior_root` assembles 2018-2024 only (no 2025), records `cross_season`/0.
- Attestation passes; summary/MD show `cross_season`.
- `py -m pytest tests/unit/evo_predictor/walkforward -q` green; `simplification_limits` passes on touched paths.
- REAL validation: drive the gold cycle far enough to prove the 2018 load now SUCCEEDS — either run a single
  module train for `constructor_quali_power_from_race_weekend` with a period-style config
  (`allow_same_season_compound_prior=false`, eval_year_train_through_round=6, eval_round_range=[7,12],
  compound_prior_root=<period root with 2018-2024 only>) at a research micro setting (epochs=1) and show it
  passes the compound-prior load (no "lacks beta_C1"); OR run the real `load_time_safe_compound_prior` for
  2018/2024/2025 at `False` and show all resolve. Paste the result.

## Allowed Scope
`src/evo_predictor/walkforward/pipeline.py`, `orchestrator.py` (only if the provenance value needs updating),
their tests. Read-only elsewhere.

## Specific Exclusions
- Do NOT modify the compound-prior loader/solver, gold config, gold defaults, scoring, or G1/G2.
- Do NOT run the full multi-hour backtest (Commander reruns).

## Constraints
- DB-only; `py`; repo-root; period-isolated outputs; explicit provenance (no silent behavior).

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/walkforward -q` green; the new/updated prior tests.
- `py -m src.utils.simplification_limits` on touched paths.
- The REAL validation output proving the 2018 compound-prior load succeeds under the new config.

## Suggested Model Tier
`simple bounded` — the fix is small and the diagnosis is confirmed; main care is updating tests + the real check.

## Authority
Decided (Commander): cross-season compound priors throughout for the periods (allow_same_season=false,
2018-2024-only isolated root, no 2025). You implement exactly this; do not reintroduce same-season priors.

## Stop Conditions
Stop and return if: the gold cycle still fails to load a train-year prior under `false` (paste the error);
or removing the as-of-N path breaks an unrelated contract.

## Return Format
Return IMPLEMENTER_RESULT: fix, files changed, test mode satisfied, evidence (tests + the real 2018-load
validation), assumptions, stop conditions, out-of-scope observations.
