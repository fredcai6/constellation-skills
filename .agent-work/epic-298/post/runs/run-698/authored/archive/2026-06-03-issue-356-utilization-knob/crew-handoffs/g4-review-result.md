# REVIEW_RESULT — g4 (sampled-backtest per-race refactor + parallelize)

Verdict: **APPROVE**

## Independent verification
- _score_one_race line-by-line equivalent to original loop body (verified vs HEAD:sampled_backtest.py 474-618):
  base_diag, actual/quali/race_start lookups, target_lap, oracle_state, runtime.predict, entrant restriction,
  sampled_order_metrics, per-stage metrics, SampledBacktestRaceResult — all identical.
- All 6 skip reasons + diagnostics keys preserved.
- Ordering: per_race/skipped partitioned in calendar (input) order on BOTH paths; independently verified
  run_jobs reassembles results[index] by submission index; n_workers<=1 short-circuits sequential.
- Default path uses LIVE objects in-process (existing callers unaffected); parallel path rebuilds
  runtime/db/normalizer in module-level worker; n_workers>1 without paths -> clear ValueError (no silent fallback).
- target_lap derived from rebuilt runtime (not carried), identical to in-process.
- New module hygiene: only G4-authored code; _oracle_state_for_mode/_runtime_race_start_target_lap byte-identical
  in sampled_backtest.py; no import cycle (lazy import); _ScoreOneRaceJob + worker pickle round-trip; no shared RNG;
  no module-level mutable cache.
- `py -m pytest test_sampled_backtest.py test_sampled_backtest_cli.py -q` -> 47 passed.
- Simplification: --paths on all 3 files PASS; sampled_backtest NOT in simplification_baseline.json (real gate);
  backtest_sampled_runtime now under limits (was CC=32/225); files 778/388 lines.
- Scope clean; exclusions untouched (training loops, scripts, report schema, numerics).

## Blockers
None.

## Out-of-scope observations
- New module sampled_backtest_scoring.py (and G3's parallel_jobs.py) must be added to
  docs/architecture/packets/evo_predictor.md and satisfy the architecture-map drift CI check (#352/#355).
  -> RECONCILE step (cartographer) handles this; carry both new modules in.
- Worker-local runtime/db cache intentionally not built (would be module-level mutable state) -> possible future perf follow-up.
