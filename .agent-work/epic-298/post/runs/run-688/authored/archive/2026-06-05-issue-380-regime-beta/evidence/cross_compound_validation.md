# Cross-compound-subset validation (#380, G2)

Harness: `scripts/validate_qs_compound_beta_regime.py` (model-free; uses the DB +
`compute_practice_features` under race-beta vs push-beta; no torch).

Metric: pairwise sign accuracy of the qs_* compound-adjusted best-lap feature
(`NormalizedPracticeFeatures.qs_best_adj`) against the actual Q classification
order, split into the cross-compound subset vs the overall pair population.

## Result (2022-2025)

```
cross-compound pairs: 6212 | overall pairs: 15738
  OVERALL  race-beta=0.6937  push-beta=0.6966  delta=+0.0029
  CROSS    race-beta=0.7072  push-beta=0.7127  delta=+0.0055
```

## Result (2024 only)

```
cross-compound pairs: 2026 | overall pairs: 4323
  OVERALL  race-beta=0.7097  push-beta=0.7133  delta=+0.0036
  CROSS    race-beta=0.7300  push-beta=0.7358  delta=+0.0058
```

## Reading (matches the issue's expectation)

- The push-regime beta **narrows the qs_* feature's gap to actual-Q on the
  cross-compound subset specifically**: +0.55pp (4-season) / +0.58pp (2024).
- Overall movement is **small** (+0.29pp / +0.36pp) — roughly half the cross
  effect, exactly because ~the majority of pairs are same-compound, where any
  per-compound offset cancels in a pairwise comparison. This muted overall
  movement is the honest, expected outcome (issue: "expect ~no overall movement").
- Direction is consistent across both windows; the cross delta is ~1.9x the
  overall delta. The correction is a real but minority-slice improvement (the
  issue's ≤13% sizing), not the quali solution.

Caveat: the same/cross pair classification uses each driver's *dominant* practice
compound as a proxy for the quali-sim stint compound, so the "overall" population
still contains the cross pairs (hence overall is lifted slightly, not flat to
zero). The qualitative conclusion — push helps cross-compound pairs more than the
population average — holds regardless of the proxy.
