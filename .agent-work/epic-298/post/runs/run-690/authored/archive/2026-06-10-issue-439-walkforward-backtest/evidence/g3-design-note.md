# g3 Design Note — Walk-Forward 2025 (for the G4 run)

## Per-period config / prior layout (isolated; never touches params/gold)

Everything for a cutoff period lives under `--work-root` (default
`outputs/walkforward_2025/`), one subdir per period (`p1/`, `p2/`, `p3/`):

```
outputs/walkforward_2025/<pN>/
  compound_prior/                 # the period's compound_prior_root
    2018/ ... 2024/               #   train-year priors COPIED from params/gold/compound_prior
    2025/compound_prior_summary.json   #   as-of-N 2025 same-season prior (built DB-only)
  alignment/                      # run_season_alignment scratch (as-of-N build)
  gold_cycle_<pN>.toml            # generated research-mode config (cutoff + eval range)
  gold_cycle/                     # gold-cycle output_dir (bundles, db_work) — gitignored
  uncertainty_calibration/        # calibration artifact dir (NOT params/gold)
  reports/                        # report_dir: gold_cycle_<slug>.*, fusion_<slug>.*, comparison
  params/gold/fusion/fusion_<slug>.json   # fusion config (under --output-dir=<pN> root)
```

The loader resolves a prior by `<root>/<year>/compound_prior_summary.json`, so the period
`compound_prior_root` holds BOTH the (unchanged) train-year gold priors and the as-of-N
2025 prior. The as-of-N prior is built by
`run_season_alignment.run_year(2025, through_round=N, skip_collection=True, db_path=...)`
(rounds > N are physically absent), then its summary is copied to `compound_prior/2025/`.

The generated TOML is `mode="research"` (so the cutoff overrides are allowed),
`data.eval_year_train_through_round=N`, `data.eval_round_range=[N+1, N+6]`,
`data.compound_prior_root=<period>/compound_prior`,
`runtime.allow_same_season_compound_prior=true`, anchor on + `quali_pace_gap` to match
promoted gold, isolated `outputs`/`report_dir`/`uncertainty_calibration_dir`, and
`runtime.utilization` from the `--utilization` passthrough. It validates through the real
`load_gold_cycle_config` (test: `test_rendered_config_loads_via_real_loader`).

Periods (`build_periods()`): P0 cutoff=None reuse R1-6; P1 N=6 → R7-12; P2 N=12 → R13-18;
P3 N=18 → R19-24. `train_max_round` and `prior_through_round` both equal the cutoff (0 for
P0); these feed the leakage attestation.

## How eval-round predictions are collected

- **P0 (reuse):** read `params/gold/per_race_predictions/round0{1..6}_*.json`, pick top-10
  via the existing G1 `extract_top10_picks` (the file's `predictions[].rank`/`driver_id`).
- **P1–P3 (cutoff pipeline):** after gold cycle → fusion → materialize → comparison, read
  the trained `reports/.../sampled_runtime_backtests/*.trained.json`. Each `per_race[]`
  carries `prediction.position_distribution` (`{driver_id: {pos: prob}}`). Predicted
  top-10 = drivers sorted by **ascending mean finishing position**
  (`predicted_top10_from_position_distribution`). This rule reproduces the promoted-gold
  file ordering exactly (verified: `test_matches_promoted_gold_round01_ordering`), so P0
  and P1–P3 collect predictions on one consistent rule.

## Pipeline step wiring (SubprocessPipeline, the real G4 path)

`run_walkforward_backtest.py` (no `--dry-run`) injects `SubprocessPipeline` into the
orchestrator. For each cutoff period it runs, in order (slugs discovered from the period's
ISOLATED `reports/` dir, exactly one of each kind):

1. `run_season_alignment.run_year(through_round=N)` + copy train-year priors → period root.
2. `py -m src.evo_predictor.run gold-cycle --config <pN>.toml --utilization <u>`.
3. `run_static_hierarchical_fusion_training.py --output-dir <pN>` (discovers `gold_cycle_<slug>.*`).
4. `materialize_runtime_bundles.py --run-slug <gold_slug>`.
5. `assemble_trained_sampled_runtime_manifest.py --fusion-config <fusion_slug> --race-start-target-lap 3`.
6. `run_sampled_runtime_comparison.py --compound-prior-root <pN>/compound_prior
   --race-name <each period GP> --utilization <u> --race-start-target-lap 3`.
7. Read the `.trained.json`; extract per-round `position_distribution` for rounds N+1..N+6.

The orchestrator then aggregates all 24 races (P0 reuse + P1-3) via the G1
`SeasonAggregator` against DB actuals (`get_session_classification(2025, R, "R")`), runs
the ENFORCED `attest_no_leakage` (aborts on any `train_max_round >= R` or
`prior_through_round >= R`), and writes `reports/walkforward/walkforward_2025.summary.json`
(+ `.md`). `verify_walkforward_run.py` gates it (exit 0 iff 24 rounds, all four periods,
every `leakage_ok`, `attestation_all_pass`).

## Caveat for G4 (out of scope to verify here — no real cycle was run)

Step 5 (`materialize_runtime_bundles.py`) auto-discovers the trained manifest by swapping
`gold_cycle_`→`fusion_` on the gold slug; it only finds it when gold and fusion share a
timestamp (per the runbook gotcha). Because each period runs gold then fusion back-to-back
into one isolated `reports/` dir this normally holds, but if the slugs diverge the trained
manifest must be repointed manually. The `SubprocessPipeline` downstream chain has not been
executed end-to-end (that is the multi-hour G4 step); its step ORDER, CLI flags, slug
discovery, and prediction extraction are all unit-validated on the pure parts, but the live
slug handoff between steps 3–6 should be watched on the first real run.
