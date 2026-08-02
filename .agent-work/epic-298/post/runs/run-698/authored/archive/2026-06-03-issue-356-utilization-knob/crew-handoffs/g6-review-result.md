# REVIEW_RESULT — g6 (determinism acceptance test + usage doc)

Verdict: **APPROVE** (judged against the human-approved REFRAMED guarantee)

## Divergence-catch reproduced: YES
- Throwaway probe reversed Run B's job order at n_workers=2 -> headline test's input-order assertion
  (keys_a == keys_b == list(_MODULES)) raised AssertionError. Probe deleted; git clean. Input-order-reassembly
  tier proven non-vacuous. Committed divergence-catch test proves the weight tier (seed perturbation > 1e-2).

## Independent verification
- `py -m pytest -q -k utilization_determinism -v` -> both tests RAN + PASSED (not skipped), 6.21s.
- Structural assertions exact/real (count, input-order keys, normalized manifest JSON, artifacts dict, normalized
  backtest JSON); worker return shape matches parallel_jobs.run_train_backtest; weight tol 1e-2 ~30x over 3e-4 floor;
  metric VALUES intentionally not compared (documented).
- Fixed seeds; threads pinned=1 both runs; skipif guard with reason; bounded ~6s.
- Doc (analysis_refresh.md) matches code: levels = _LEVEL_PLANS, workers*threads<=cores, RAM cap, single-core clamp;
  non-policy hint bypasses apply_cli_overrides (verified) and absent from build_run_config; Last verified 2026-06-03.
- Scope: only the new test + the doc; zero src/scripts/schema/arch-map change. No report-schema drift.
- Production-defect check: NONE. run_jobs adds no systematic divergence (2.8e-4 worker-delta ~= 3.1e-4 rerun, both < 1e-2).

## Blockers
None.

## Out-of-scope observations
- Bit-repro of torch CPU training (~3e-4 drift) -> separate issue (human-approved filing; engine tc3).
