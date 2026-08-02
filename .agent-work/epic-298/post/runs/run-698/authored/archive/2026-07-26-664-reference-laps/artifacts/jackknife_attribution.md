# g4 attribution-robustness jackknife (issue #664, epic #659)

- Slice: 2023 Q round 10 (Great Britain); scoring VER (Red Bull Racing).
- Jackknife: delete-d / **driver**-block boundary-jitter, B=30 (30 replicates re-derived cleanly).
- Boundary-set drift: mean=0.7363 m, max=1.155 m (anchor MAP_STABILITY_DRIFT_M=10.0 m; within_anchor=True).
- INSTRUMENT reading, not a hard gate: the numbers are reported; no new literal band is minted.

## Per-class deficit stability (across replicates)

| class | time-deficit median (s) | time-deficit IQR (s) | speed-deficit IQR (m/s) |
|---|---|---|---|
| straight | 1.248 | 0.01236 | 0.009274 |
| braking_zone | 0.2615 | 0.004207 | 0.03246 |
| severity:2023:v1:c0 | 3.491 | 0.0168 | 0.05282 |
| severity:2023:v1:c1 | 0.01924 | 0.001506 | 0.05723 |
| severity:2023:v1:c2 | 0.4618 | 0.007578 | 0.03073 |
| severity:2023:v1:c3 | 0.1473 | 0.003702 | 0.03113 |

## Positive control (REQUIRED)

- Injected: a corner-class deficit shifted into a straight class.
- Statistic: leaked straight-class deficit spread WITH injection (0.1589) vs clean baseline (0).
- **FIRED = True** (injected straight-class deficit spread exceeds clean-baseline spread under boundary jitter (corner deficit leaks across the corner/straight edge)).

## Notes

- G soft-degrade: The #663 grip_estimates store is UNPOPULATED on disk, so the one-sided grip band sigma+ is 0 (band omitted). The POINT deficit is byte-identical with or without G; consume-not-refit -- grip_batch was NOT run (out of scope).
- Anti-circularity: Scoring ceiling is strictly_pre=True (target round excluded from the causal car history); the FIELD reference lap only PLACES class boundaries, it does not score. The jackknife perturbs attribution (boundaries), never the ceiling.
- deficits-sum-to-lap is a CONSTRUCTION check (labelled construction, not validation).
