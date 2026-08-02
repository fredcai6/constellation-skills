# Crew Handoff

## Role
reviewer

## Assigned Gate
G2 — surface |r/σ| percentile instrumentation (issue #304, phase 1)

## Suggested Model Tier
stronger broad — verify eval-path instrumentation, ADR 0001 boundary, schema surfacing, and test quality

## Test Mode
inspection + independent command verification

## Task
Independently verify G2: full-eval |r/σ| percentiles persisted in module diagnostics + gold report, schema v5 fields registered, no training-math change, latent_power F1-agnostic.

## Close Criteria (APPROVE requires all)
1. `py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py -q` → exit 0.
2. `uncertainty_diagnostics` with {p50,p90,p95,p99,sigma_mean} in training diagnostics dict AND gold report per-module entry.
3. Unit tests prove: monotonic percentiles, full-eval (not last-batch) for persisted values, None/empty target_mu → nulls not raise.
4. `REPORT_SCHEMA_VERSION` still 5 (no second bump); schema markdown regenerated from source (byte-match generator if feasible).
5. No F1 phase/scope strings added to `latent_power`; no loss/training-math change.
6. `evidence/g2-rsigma-baseline.md` exists with per-module table.

## Authority
User-approved plan, gate G2.

## Allowed Scope
Read-only review + verification commands. Do not edit source.

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py -q
git diff --stat
```

## Return Format
REVIEW_RESULT: APPROVE|BLOCK, per-check findings, command outputs.
