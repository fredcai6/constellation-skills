# Held-out-weekend diagnostic — g4 (#670, epic #659)

_Generated 2026-07-27T11:39:12.391396+00:00 — slice `C:\Programs\f1brainz-wt\epic659-670\.agent-work\670-season-run\artifacts\scratch\refutil_season_2023.db`_

## What this sizes

arm1 vs arm2 sizes the value of COMPOSITION-WEIGHTING; arms 1/2 vs golf null sizes the value of the WHOLE DRIVER TERM. This is NOT the full hierarchical pool vs an independent aggregate.

> **⚠ Sigma interpretation — read first.** READ THE POINT METRIC FIRST. Arms 1 & 2 carry the LANDED #666 fit's predictive sigma, which folds in the channel-independent one-sided grip term g_sigma_onesided. On this slice that term is pathological: p90 ~ 8e9 and max ~ 9.6e9 (vs a utilization time_deficit scale of ~0.1s), so ~20% of severity rows inflate the fingerprint/baseline cell sigma to ~1e9. That makes arms 1/2's predictive intervals VACUOUSLY WIDE (coverage ~1.0) and their mean log-score catastrophically negative — NOT because their point prediction is bad, but because their variance is grip-dominated. The golf null uses an honest empirical field dispersion, so its sigma is well-scaled and its log-score is not comparable to arms 1/2's on equal footing. CONCLUSION: the mean-|resid| POINT metric is the sigma-robust skill comparison here; the log-score primarily diagnoses the landed fit's sigma mis-calibration (a #666 property, out of scope for this diagnostic to change — surfaced as a finding).

> **Composition caveat.** PROMINENT CAVEAT: W's composition is the FIELD-REFERENCE (__field__) row's time_shares — the field-median-across-constructors track geometry — read IDENTICALLY for all three arms. It is track-geometry derived from W's OWN reference lap (NOT strictly-prior on a 2023-only slice; a 2023-only slice has no prior-year same-circuit composition, so the strictly-prior-composition sensitivity readout is ABSENT). It carries NO driver-specific leakage — the fingerprint CELLS are strictly-pre (as_of=R-1) and the golf-null pool is strictly < R. Being shared across arms, it cannot advantage the fingerprint arm over the baseline, so the comparison stays fair — which is exactly what this diagnostic measures.

**Leakage guards.** Fingerprint fit runs at as_of_round=R-1 (fit_driver_fingerprints filters round_idx<=as_of INCLUSIVE, excluding R); golf-null field pool pools rounds < R only. Both are asserted in code and covered by dedicated leakage-guard tests.

**One documented baseline.** Arm 2 (driver-overall-only) is the join's T7-1 uniform-composition form: the SAME code path (join_weekend_prior) and the SAME strictly-pre cells as arm 1, with the composition flattened to equal shares so the resolved-weighted mean reduces to the unweighted driver mean. It is the ONE documented baseline (per #667 TC-1) — no second, separately-built model exists in this diagnostic.

**Thin/early rounds.** Round 3 (as_of=2) has no covered strictly-prior severity round -> UNRESOLVABLE (not forced). Early rounds with < 3 prior severity rounds are reported THIN (honest thin-cell fingerprints), not suppressed. A small/thin signal is a complete result.

**Scoring.** Per scored (round R, driver d, channel ch): weights w_i = comp_i / sum_present(comp) over the field composition's severity classes present for d at R; truth = sum_i w_i * actual_value(d, class_i, R) (utilization=time_deficit_s, energy=deployment_share). Each arm yields a Student-t PredictiveT (loc=m, scale=s, df=nu). PRIMARY metric = mean predictive log-score L = mean over scored triples of scipy.stats.t.logpdf(truth; df=nu, loc=m, scale=s) (higher is better; no normal approximation). SECONDARY: mean |resid| = mean|truth - m|; coverage = fraction of truths inside each arm's two-sided 90% predictive interval.

## Per-arm aggregate (all scored held-out driver-weekends)

| arm | n | mean log-score ↑ | mean \|resid\| ↓ | coverage@90% |
|---|---:|---:|---:|---:|
| fingerprint × composition (arm 1) | 718 | -19.6252 | 0.8541 | 1.000 |
| driver-overall-only / T7-1 (arm 2) | 718 | -19.5294 | 1.1425 | 1.000 |
| golf null — field, no driver (arm 3) | 722 | -0.4594 | 0.8300 | 0.911 |

### Golf-null floor + point reading (sigma-robust)

Two readings. LOG-SCORE (mandated primary) is dominated by the arms' differing sigma constructions (see meta.sigma_interpretation) and is NOT an equal-footing skill comparison for arms 1/2 vs golf null. The mean-|resid| POINT reading is the sigma-robust skill comparison.

- composition-weighting helps the point (arm1 |resid| < arm2 |resid|): **True**
- fingerprint beats golf null on the point (|resid|): **False**
- baseline beats golf null on the point (|resid|): **False**

## Per-channel

| arm | channel | n | mean log-score ↑ | mean \|resid\| ↓ | coverage |
|---|---|---:|---:|---:|---:|
| fingerprint × composition (arm 1) | utilization | 359 | -19.6253 | 1.6623 | 1.000 |
| fingerprint × composition (arm 1) | energy | 359 | -19.6252 | 0.0459 | 1.000 |
| driver-overall-only / T7-1 (arm 2) | utilization | 359 | -19.5297 | 2.2041 | 1.000 |
| driver-overall-only / T7-1 (arm 2) | energy | 359 | -19.5292 | 0.0808 | 1.000 |
| golf null — field, no driver (arm 3) | utilization | 361 | -2.3188 | 1.6147 | 0.900 |
| golf null — field, no driver (arm 3) | energy | 361 | 1.3999 | 0.0454 | 0.922 |

## Per-round

| round | circuit | status | prior rounds | n scored | fp n | base n | golf n |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | Australia | unresolvable | 0 | 0 | 0 | 0 | 0 |
| 4 | Azerbaijan | thin | 1 | 36 | 36 | 36 | 36 |
| 5 | Miami | thin | 2 | 38 | 38 | 38 | 38 |
| 6 | Monaco | resolved | 3 | 40 | 40 | 40 | 40 |
| 7 | Spain | resolved | 4 | 40 | 40 | 40 | 40 |
| 8 | Canada | resolved | 5 | 36 | 36 | 36 | 36 |
| 9 | Austria | resolved | 6 | 40 | 40 | 40 | 40 |
| 10 | Great Britain | resolved | 7 | 40 | 40 | 40 | 40 |
| 11 | Hungary | resolved | 8 | 40 | 38 | 38 | 40 |
| 12 | Belgium | resolved | 9 | 40 | 40 | 40 | 40 |
| 13 | Netherlands | resolved | 10 | 36 | 34 | 34 | 36 |
| 14 | Italy | resolved | 11 | 40 | 40 | 40 | 40 |
| 15 | Singapore | resolved | 12 | 40 | 40 | 40 | 40 |
| 16 | Japan | resolved | 13 | 26 | 26 | 26 | 26 |
| 17 | Qatar | resolved | 14 | 40 | 40 | 40 | 40 |
| 18 | United States | resolved | 15 | 40 | 40 | 40 | 40 |
| 19 | Mexico | resolved | 16 | 36 | 36 | 36 | 36 |
| 20 | Brazil | resolved | 17 | 38 | 38 | 38 | 38 |
| 21 | Las Vegas | resolved | 18 | 38 | 38 | 38 | 38 |
| 22 | Abu Dhabi | resolved | 19 | 38 | 38 | 38 | 38 |

- **resolved rounds:** [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
- **thin rounds:** [4, 5]
- **unresolvable rounds:** [3]
