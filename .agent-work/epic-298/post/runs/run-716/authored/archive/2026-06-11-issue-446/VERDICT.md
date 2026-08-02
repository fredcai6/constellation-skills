# Phase 0a Verdict — Trajectory Grading Harness Discrimination Test

**Date:** 2026-06-11
**Gate:** g3 — Multi-session strawman run
**Run:** `scripts/run_trajectory_grading_strawman.py` (3 sessions, 5 drivers each, tol_sector_s=0.050 s)
**Reports:** `.agent-work/issue-446/evidence/*_grading.json` (3 files, schema v1.0)

---

## Per-Session Key Numbers

All numbers are traced directly to the JSON reports in `.agent-work/issue-446/evidence/`.

### Session 1: 2023 Belgium Q (Qualifying, Spa-Francorchamps)
**Report:** `2023_belgium_Q_grading.json`
**Drivers:** VER(1), LEC(16), HAM(44), SAI(55), PIA(81) — 5 laps each = 25 lap-sector triplets

#### Gate (a): Sector-Anchor Gate at 50 ms
| Metric | Value |
|--------|-------|
| `anchor_gate.passed` | **False** |
| `max_residual_s` | **1.5049 s** |
| `tol_s` | 0.050 s |
| `n_laps` | 25 |
| RMS residual (all sector residuals) | 0.3001 s |
| Median absolute residual | 0.0854 s |
| n residuals | 75 |

**Verdict at 50 ms: FAIL** — max residual 1.505 s exceeds the 50 ms threshold by 30x. The sector-anchor gate rejects the strawman clearly.

Fitted anchors: s1=2240.3 m, s2=5029.6 m, s3=7004.0 m (uncertainty: ±2.9, ±3.8, ±5.0 m).

#### Gate (b): Covariance Consistency
| Metric | Value |
|--------|-------|
| `covariance_gate.passed` | **True** |
| `reduced_chi_sq` | **11.14** |
| `band` | [0.01, 100.0] |
| `n_samples` | 75 |

**Verdict: PASS** (within the permissive 0.01–100 band). However, reduced chi-square of 11.14 is strongly elevated — the naive 25 m² flat variance significantly underestimates the actual residual variance (which would correspond to ~sqrt(11.14) × 5 m ≈ 16.7 m 1-sigma actual). The strawman's covariance is detectably dishonest at this chi-square, but the gate band is too wide to reject it at this threshold.

#### Diagnostic (c): Cross-Residual (per-lap offset_s between position_arc and speed_arc)
| Metric | Value |
|--------|-------|
| `n_laps` | 25 |
| offset range | [-0.197 s, +0.406 s] |
| offset mean | +0.060 s |
| offset std | 0.133 s |
| arc residual range | [2.5 m, 13.3 m] |
| arc residual mean | 5.8 m |
| lap closure range | [12.5 m, 119.7 m] |
| lap closure mean | 48.6 m |

The inter-stream time offsets span ~0.6 s across laps — large variation and non-zero mean. Lap closure errors range up to 120 m (1.7% of the 7004 m lap). These are characteristic of the strawman's sawtooth position artifact from interpolating 10 Hz GPS onto a 240 Hz timeline.

---

### Session 2: 2023 Belgium R (Race, Spa-Francorchamps)
**Report:** `2023_belgium_R_grading.json`
**Drivers:** VER(1), LEC(16), HAM(44), SAI(55) — 8 laps each = 32 lap-sector triplets
(PIA had no DB truth for the race and was skipped)

#### Gate (a): Sector-Anchor Gate at 50 ms
| Metric | Value |
|--------|-------|
| `anchor_gate.passed` | **False** |
| `max_residual_s` | **1.0670 s** |
| `tol_s` | 0.050 s |
| `n_laps` | 32 |
| RMS residual | 0.1576 s |
| Median absolute residual | 0.0481 s |
| n residuals | 96 |

**Verdict at 50 ms: FAIL** — max residual 1.067 s exceeds threshold by 21x. Note: median absolute residual is 0.048 s, which is *just* below 50 ms. This means the majority of laps are near the threshold but a tail of outlier laps drives the max. The gate correctly rejects the strawman because the worst laps matter for the pass/fail verdict.

Fitted anchors: s1=2233.7 m, s2=5026.8 m, s3=6996.9 m (uncertainty: ±8.4, ±5.4, ±7.6 m).
Note: anchor uncertainty is higher than in quali (3–8× larger), reflecting greater spread in race lap time profiles.

#### Gate (b): Covariance Consistency
| Metric | Value |
|--------|-------|
| `covariance_gate.passed` | **True** |
| `reduced_chi_sq` | **3.07** |
| `band` | [0.01, 100.0] |
| `n_samples` | 96 |

**Verdict: PASS** (within band). Reduced chi-square 3.07 is elevated but less so than in quali (11.14), because race laps have lower speed variation so the naive flat variance is less wrong on average. Still detectably dishonest (actual ~ sqrt(3.07) × 5 m ≈ 8.8 m 1-sigma).

#### Diagnostic (c): Cross-Residual
| Metric | Value |
|--------|-------|
| `n_laps` | 32 |
| offset range | [-0.227 s, +0.028 s] |
| offset mean | -0.126 s |
| offset std | 0.077 s |
| arc residual range | [2.7 m, 9.5 m] |
| arc residual mean | 5.8 m |
| lap closure range | [32.1 m, 123.8 m] |
| lap closure mean | 70.4 m |

Offsets are predominantly negative in the race (mean -0.126 s) vs. mixed in quali (mean +0.060 s), consistent with formation lap / SC lap contaminating the position arc integration. Lap closure mean 70 m (1% of track) is similar to quali.

---

### Session 3: 2022 Spain R (Race, Circuit de Barcelona-Catalunya)
**Report:** `2022_spain_R_grading.json`
**Drivers:** VER(1), PER(11), RUS(63), SAI(55), HAM(44) — 8 laps each = 40 lap-sector triplets

#### Gate (a): Sector-Anchor Gate at 50 ms
| Metric | Value |
|--------|-------|
| `anchor_gate.passed` | **False** |
| `max_residual_s` | **0.2955 s** |
| `tol_s` | 0.050 s |
| `n_laps` | 40 |
| RMS residual | 0.0696 s |
| Median absolute residual | 0.0374 s |
| n residuals | 120 |

**Verdict at 50 ms: FAIL** — max residual 0.296 s exceeds threshold by 6x. This is notably smaller than the Belgium sessions (0.30 vs 0.16–1.50 s range). Median residual is 0.037 s — below the 50 ms threshold, meaning the majority of observations pass, but the tail is long enough to fail the gate.

Fitted anchors: s1=1599.3 m, s2=3347.1 m, s3=4599.0 m (uncertainty: ±1.3, ±1.9, ±1.9 m).
Anchor uncertainty is smallest here — tightest co-estimation in the race at Barcelona.

#### Gate (b): Covariance Consistency
| Metric | Value |
|--------|-------|
| `covariance_gate.passed` | **True** |
| `reduced_chi_sq` | **0.5989** |
| `band` | [0.01, 100.0] |
| `n_samples` | 120 |

**Verdict: PASS** (within band). Reduced chi-square 0.60 is *below* 1 — the naive 25 m² variance is actually *overestimating* the actual residual variance for this session. This is also "dishonest" (covariance is miscalibrated, just in the other direction: too conservative here vs. too optimistic for Spa), but the current gate band passes it.

#### Diagnostic (c): Cross-Residual
| Metric | Value |
|--------|-------|
| `n_laps` | 40 |
| offset range | [-0.075 s, +0.356 s] |
| offset mean | +0.124 s |
| offset std | 0.099 s |
| arc residual range | [2.9 m, 13.9 m] |
| arc residual mean | 7.0 m |
| lap closure range | [35.2 m, 78.3 m] |
| lap closure mean | 62.4 m |

Closure errors 35–78 m on a 4675 m track = 0.8–1.7%, consistent in magnitude with Spa despite the shorter track. The position arc and speed arc disagree by 3–14 m/lap consistently — another fingerprint of the strawman's interpolation artifact.

---

## Cross-Session Summary Table

| Session | n_laps | max_res_s | RMS_res_s | med_abs_res_s | anchor PASS? | red_chi_sq | cov PASS? | offset_range_s | closure_mean_m |
|---------|--------|-----------|-----------|---------------|--------------|------------|-----------|----------------|----------------|
| 2023 Belgium Q | 25 | 1.505 | 0.300 | 0.085 | **FAIL** | 11.14 | PASS | [-0.20, +0.41] | 48.6 |
| 2023 Belgium R | 32 | 1.067 | 0.158 | 0.048 | **FAIL** | 3.07 | PASS | [-0.23, +0.03] | 70.4 |
| 2022 Spain R | 40 | 0.296 | 0.070 | 0.037 | **FAIL** | 0.60 | PASS | [-0.08, +0.36] | 62.4 |

---

## Discrimination Conclusion

### Gate (a) — Sector-Anchor at 50 ms: DISCRIMINATES

The sector-anchor gate **discriminates the strawman in all three sessions**. All three reports have `anchor_gate.passed = False` with max residuals ranging from 0.30 s to 1.51 s, all well above the 50 ms threshold. The gate rejects the strawman unambiguously.

**Why it discriminates:** The strawman's `s(t)` is derived from FastF1's merged product — position arc-length computed from 10 Hz GPS interpolated to ~240 Hz. The interpolation introduces systematic lag between the timing-loop crossing times implied by the position trajectory and the official sector split durations. These lags accumulate to 100 ms – 1.5 s in the worst cases, depending on sector length and speed profile. With free (co-estimated) anchors, the least-squares fit absorbs constant biases, but the per-lap variance in sector crossings cannot be absorbed — so the residuals after fitting reflect the lap-to-lap instability of the interpolation artifact.

**This is NOT a free-anchor permissiveness problem.** The key distinguishing point: the 50 ms gate is tighter than the typical residual scatter. Even the median residual (0.037–0.085 s across sessions) exceeds or is near 50 ms in two of three sessions, and the tail reaches 0.30–1.5 s. Free anchors absorb the *mean* bias per session but cannot absorb the *lap-to-lap variance*, which is the strawman's pathology.

### Gate (b) — Covariance Consistency: DOES NOT DISCRIMINATE at current band

All three sessions pass the covariance gate with the current permissive band [0.01, 100.0]. The reduced chi-squares range widely (0.60 → 11.14), which is itself informative: the strawman's covariance is detectably wrong (chi-sq far from 1), but the band is too wide to reject it. Tightening the band to (e.g.) [0.5, 2.0] would correctly reject the Belgium Quali (chi-sq 11.14) and plausibly Spain Race (chi-sq 0.60), but would still pass Belgium Race (chi-sq 3.07). Gate (b) discrimination therefore depends critically on the band design — this is an input to Phase 0b gate-tolerance calibration.

### Gate (c) — Cross-Residual: DIAGNOSTIC, NOT GATED

The cross-residual block reveals consistent strawman pathologies:
- Inter-stream time offsets range [-0.23, +0.41] s across laps (0.1–0.2 s std), with session-level mean shifts (-0.13 s for Belgium Race, +0.06–0.12 s for the others). This is the expected fingerprint of the sawtooth accel / time-base drift from differentiating the interpolated position.
- Lap closure errors are 12–124 m (mean 49–70 m) — not negligible but not gated.
- The arc residual (position arc vs. speed arc disagreement) is 3–14 m per lap, consistent with the GPS interpolation grid.

These diagnostics can become gate (c) in Phase 0b once a pass threshold is calibrated.

### Overall Phase 0a Verdict

**The harness discriminates at gate (a) at 50 ms across all three sessions and two circuits (2022, 2023), one quali + two races.**

This is not an honest null. The strawman is clearly rejected by the sector-anchor gate. The discriminating power is in the per-lap variance of sector crossing times, not in the mean offset (which the free anchor absorbs). The covariance gate at its current permissive band is a non-discriminator and needs tightening for Phase 0b — chi-sq of 11 (Spa Quali) vs. 0.6 (Spain Race) shows the gate is sensitive to session type and would benefit from session-type-specific band calibration.

**Feed to Phase 0b:** 
1. Gate (a) at 50 ms is working. The current tol_sector_s=0.050 s is the right operating point — it rejects the strawman while being analytically grounded in timing-loop precision.
2. Gate (b) needs a tighter band: [0.01, 100.0] is too permissive. A calibrated [0.5, 2.0] band would add independent discrimination power beyond gate (a).
3. Gate (c) cross-residual thresholds for offset_std and lap closure are TBD — the current data gives calibration ranges (offset_std 0.08–0.13 s, closure mean 49–70 m for a bad strawman).
4. Note: the 2023 Belgium Race median anchor residual (0.048 s) is just below 50 ms — a tighter threshold (e.g. 30 ms) would fail even the median, which may be appropriate for a high-quality trajectory.

---

## Offline and DB-Write Confirmation

- All three sessions loaded from `C:/Programs/f1Brainz/outputs/cache` only. `offline_mode(True)` was enforced by the offline_loader. No network calls.
- DB access was strictly read-only (SQLite read-only URI: `file:///...?mode=ro`). No writes to any canonical DB.
- The JSON evidence files are in `.agent-work/issue-446/evidence/` and are NOT committed.
