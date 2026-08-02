# Re-validation on the NEW median-relative encoding (#380 resume)

Harness: `scripts/validate_qs_compound_beta_regime.py` (unchanged; no adaptation needed —
the new encoding kept `qs_best_adj` lower-is-better, and the harness uses within-event
pairwise sign accuracy which is invariant to a monotone normalization).

Run: `PYTHONPATH=. py scripts/validate_qs_compound_beta_regime.py --years 2022 2023 2024 2025`

## Why β units did NOT need adjustment
`CompoundNormalizer.normalize_lap_time` adjusts RAW lap times (seconds) to "equivalent C3
at age 0" — this happens UPSTREAM of feature normalization. PR #400 changed feature
normalization from minmax `[0,1]` to median-relative `(t − median)/median`. Median-relative
is a STRICTLY MONOTONE transform of the adjusted lap time (median > 0), so the within-event
ORDER of `qs_best_adj` is identical under either encoding. The harness scores pairwise sign
accuracy within each event => the β-effect on cross-compound ordering is preserved. β values
(normalized_fractional effect space, applied to lap-time adjustments) remain valid as-is.

## Fresh numbers (NEW encoding) vs stale (OLD minmax)

### 2022–2025 (headline)
```
cross-compound pairs: 6284 | overall pairs: 15872
  OVERALL  race-beta=0.7014  push-beta=0.7040  delta=+0.0026
  CROSS    race-beta=0.7131  push-beta=0.7191  delta=+0.0060
```
| Metric        | Stale (minmax)        | Fresh (median-relative) |
|---------------|-----------------------|-------------------------|
| CROSS delta   | +0.55pp (.7072→.7127) | +0.60pp (.7131→.7191)   |
| OVERALL delta | +0.29pp (.6937→.6966) | +0.26pp (.7014→.7040)   |
| CROSS/OVERALL | ~1.9×                 | ~2.3×                   |
| cross/overall | 6212 / 15738          | 6284 / 15872            |

### 2024 only
```
cross-compound pairs: 2039 | overall pairs: 4362
  OVERALL  race-beta=0.6884  push-beta=0.6926  delta=+0.0041
  CROSS    race-beta=0.7155  push-beta=0.7244  delta=+0.0088
```
(stale 2024: CROSS +0.58pp .7300→.7358; OVERALL +0.36pp .7097→.7133)

## Verdict
CROSS-COMPOUND improvement SURVIVES the new encoding — directionally positive, and CROSS
delta is ~2.3× the OVERALL delta (the §7.5 minority-slice signature). Marginally stronger
than the stale measurement. STOP condition NOT triggered. No β-unit adjustment made.

Pair-count drift (6212→6284 overall; 4323→4362 for 2024) is consistent with PR #400's
sprint FP1+SQ short-run bucket changes altering which laps land in the quali-sim bucket.
