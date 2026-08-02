# Triage Recommendation: Regenerate rt_comparison with live backtests

## Classification
`bug`, `research hardening`

## Source checklist/artifact
- reconcile.json tc1 / reconcile-summary.md T1
- g4 pilot residual note

## Structural anchor
`struct:evo` — sampled runtime comparison path

## Problem
Committed `rt_comparison_*` artifacts pass compact validation but metrics may reuse a prior May-17 comparison run. Live `run_sampled_runtime_comparison.py` fails with `torch.linalg.solve: singular matrix` on current gold runtime bundles.

## Current truth
- Manifests and train_years aligned to 2018–2024 in g4
- Compact validation passes with materialized rt_comparison artifacts
- Live backtest regen blocked by singular matrix in gold runtime bundles

## Desired/future concern
Sampled-runtime parity gates should be backed by metrics computed from the same gold bundles/manifests they reference.

## Evidence
- g4 pilot: singular matrix during live regen
- `scripts/run_sampled_runtime_comparison.py` mode/slug fixes in issue-292
- reconcile-summary.md T1

## Impact
Observability gates may pass structurally while parity metrics are stale relative to current gold bundles.

## Suggested scope
1. Diagnose singular matrix in gold runtime bundle linear algebra path
2. Regenerate `rt_comparison_*` from current `fusion_*` / gold manifests
3. Confirm compact validation still passes with fresh metrics

## Non-goals
- Changing issue-292 validation gate definitions
- Full gold retrain (separate candidate)

## Acceptance criteria
- [ ] Live `run_sampled_runtime_comparison.py` completes without singular matrix on current gold bundles
- [ ] New `rt_comparison_*` artifacts committed with metrics from that run
- [ ] `py scripts/run_pipeline_validation.py --profile compact` exits 0

## Recommended priority
`medium`

**Reason:** Validation passes today but metric freshness undermines sampled-runtime parity trust.

## Issue creation authority
`ask user`
