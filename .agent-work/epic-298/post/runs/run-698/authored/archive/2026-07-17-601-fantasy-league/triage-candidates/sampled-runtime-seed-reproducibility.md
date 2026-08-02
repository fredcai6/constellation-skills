# Triage Recommendation: Make sampled-runtime seed reproducible end to end

## Classification
`bug, missing test, research hardening`

## Source checklist/artifact
- Issue #606 historical reconstruction evidence and `.agent-work/cmdr-606/model-reconstruction/`

## Structural anchor
`struct:evo_predictor`

## Cartographer mismatch class
`none`

## Problem
The sampled runtime accepts and records a seed, but repeated executions with the same code, manifest, data, sample count, and seed produce different position distributions, ranked top tens, and fantasy scores.

## Current truth
The issue-606 2022 round-1 pilot and full reconstruction both used the same assembled manifest, `n_samples=1000`, and `seed=0`, yet their distribution hashes differ (`995415…` versus `12c22a…`), their top-ten orders differ, and their fantasy scores are 57 versus 55. Full fresh season totals also diverged from the original hash-frozen payloads: 832 versus 873, 841 versus 850, and 811 versus 859. Race-classification row hashes were unchanged.

## Desired/future concern
One frozen seed must control every stochastic source used by sampled prediction/backtest, or the interface must fail rather than claim reproducibility it does not provide.

## Evidence
- `.agent-work/cmdr-606/model-reconstruction/heldout_2022.pilot.json`
- `.agent-work/cmdr-606/model-reconstruction/heldout_2022.full.partial.json`
- `.agent-work/cmdr-606/model-reconstruction/heldout_{2022,2023,2024}.failed.json`
- `src/evo_predictor` sampled-runtime and backtest paths

## Impact
Historical reports cannot be regenerated from their declared seed, race-week submissions can reshuffle between identical runs, and A/B decisions on fantasy points can measure RNG drift instead of model changes.

## Suggested scope
Trace every Python, NumPy, model-framework, and sampling RNG used by sampled prediction/backtest; establish a single explicit seed derivation contract; add repeat-run tests at runtime and CLI boundaries; document determinism guarantees and any platform limits.

## Non-goals
Do not retune models, change sampling semantics, or bless one newly generated historical total as canonical.

## Acceptance criteria
- [ ] Two same-process and two fresh-process executions with identical inputs and seed produce byte-stable canonical position-distribution facts and identical ranked outputs.
- [ ] Changing the seed changes at least one sampled fact in a controlled test.
- [ ] The seed is threaded through every RNG source with no implicit global-state fallback.
- [ ] `race-week`, sampled-predict, and sampled-backtest expose and record the same seed contract.
- [ ] A regression fixture covers the issue-606 repeated-round failure shape.

## Recommended priority
`urgent`

**Reason:** It invalidates reproducible evaluation and single-submission output across the fantasy epic.

## Related artifacts
- Epic #601
- Issue #606
- `reports/walkforward/multiseason_fantasy.json`

## Disposition
`filed`

**Detail:** filed as #616

## Issue creation authority
`create issue directly`
