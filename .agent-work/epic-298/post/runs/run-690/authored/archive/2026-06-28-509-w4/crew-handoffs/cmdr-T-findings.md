# G1 Characterization Table: Decoupled vs Incumbent

Generated: 2026-06-28T10:08:49.293587+00:00 UTC

Circuits: Belgium (Spa), Monaco, Bahrain — 2023 Q RBR (VER, PER)

**Shift** = decoupled - incumbent. **Shift/sigma** = shift / sigma_incumbent.
Shift/sigma |< 0.5| = negligible; |0.5-1.0| = notable; |> 1.0| = significant.

## TractionView: `traction_accel_ms2` and `traction_aero_accel_per_m`

| Circuit | Path | `traction_accel_ms2` | sigma | `traction_aero_accel_per_m` | sigma | n |
|---------|------|----------------------|-------|------------------------------|-------|---|
| Belgium | incumbent | 7.5854 | 1.4775 | 0.007895 | 0.001946 | 1960 |
| Belgium | decoupled | 8.6685 | 1.3915 | 0.007310 | 0.001767 | 2001 |
| Belgium | parity | 8.1315 | 1.3836 | 0.008188 | 0.001818 | 2001 |
| Monaco | incumbent | 7.1204 | 0.8725 | 0.011701 | 0.001385 | 1839 |
| Monaco | decoupled | 16.1079 | 0.3685 | 0.000000 | 0.000438 | 1860 |
| Monaco | parity | 10.6092 | 1.0122 | 0.007903 | 0.001674 | 1860 |
| Bahrain | incumbent | 15.0114 | 1.2920 | 0.001208 | 0.001056 | 2004 |
| Bahrain | decoupled | 5.7871 | 1.6383 | 0.013327 | 0.002429 | 1992 |
| Bahrain | parity | 7.0161 | 1.7955 | 0.011102 | 0.002418 | 1992 |

**Shift table (Traction) — Config B = confounded (smoothed v); Config C = parity (raw v + decoupled a_long)**

| Circuit | Config | delta `traction_accel_ms2` | d/sigma | delta `traction_aero_accel_per_m` | d/sigma |
|---------|--------|---------------------------|---------|-----------------------------------|---------|
| Belgium | B (confounded) | +1.0831 | +0.7331 | -0.000585 | -0.3006 |
| Belgium | C (parity) | +0.5462 | +0.3697 | +0.000294 | +0.1509 |
| Monaco | B (confounded) | +8.9875 | +10.3006 | -0.011701 | -8.4484 |
| Monaco | C (parity) | +3.4888 | +3.9986 | -0.003799 | -2.7428 |
| Bahrain | B (confounded) | -9.2243 | -7.1395 | +0.012119 | +11.4814 |
| Bahrain | C (parity) | -7.9952 | -6.1882 | +0.009895 | +9.3741 |

## PowerDragView: `max_power_w` and `drag_area_closed_m2`

| Circuit | Path | `max_power_w` (MW) | sigma (MW) | `drag_area_closed_m2` | sigma | n_closed | degen |
|---------|------|---------------------|------------|----------------------|-------|----------|-------|
| Belgium | incumbent | 0.5975 | 0.0095 | 1.0642 | 0.0640 | 1572 | False |
| Belgium | decoupled | 0.5878 | 0.0080 | 1.1683 | 0.0554 | 1613 | False |
| Belgium | parity | 0.5881 | 0.0083 | 1.1677 | 0.0576 | 1615 | False |
| Monaco | incumbent | 0.6688 | 0.0077 | 1.4493 | 0.0617 | 1021 | False |
| Monaco | decoupled | 0.5079 | 0.0762 | 0.0000 | 1.3528 | 1651 | True |
| Monaco | parity | 0.5651 | 0.0096 | 0.9277 | 0.0909 | 1182 | False |
| Bahrain | incumbent | 0.6395 | 0.0027 | 1.3996 | 0.0173 | 1065 | False |
| Bahrain | decoupled | 0.5919 | 0.0134 | 1.2626 | 0.1144 | 1265 | False |
| Bahrain | parity | 0.6091 | 0.0129 | 1.3086 | 0.1062 | 1259 | False |

**Shift table (PowerDrag) — Config B = confounded; Config C = parity**

| Circuit | Config | delta `max_power_w` (W) | d/sigma | delta `drag_area_closed_m2` | d/sigma |
|---------|--------|-------------------------|---------|------------------------------|---------|
| Belgium | B (confounded) | -9664.2 | -1.0210 | +0.1041 | +1.6258 |
| Belgium | C (parity) | -9307.8 | -0.9834 | +0.1035 | +1.6166 |
| Monaco | B (confounded) | -160871.4 | -20.8218 | -1.4493 | -23.4729 |
| Monaco | C (parity) | -103697.1 | -13.4217 | -0.5216 | -8.4478 |
| Bahrain | B (confounded) | -47604.0 | -17.7145 | -0.1370 | -7.9363 |
| Bahrain | C (parity) | -30427.0 | -11.3225 | -0.0910 | -5.2735 |

## CoastView: `coast_rolling_decel_ms2` and `coast_drag_area_m2`

| Circuit | Path | `coast_rolling_decel_ms2` | sigma | `coast_drag_area_m2` | sigma | n |
|---------|------|--------------------------|-------|----------------------|-------|---|
| Belgium | incumbent | 1.31163 | 0.06824 | 0.9002 | 0.0562 | 1407 |
| Belgium | decoupled | 1.27872 | 0.06805 | 0.9736 | 0.0722 | 1020 |
| Monaco | incumbent | 1.55805 | 0.07363 | 0.8440 | 0.1068 | 1502 |
| Monaco | decoupled | 1.31539 | 0.08837 | 1.2071 | 0.0900 | 1128 |
| Bahrain | incumbent | 1.53122 | 0.07951 | 1.0600 | 0.0547 | 1265 |
| Bahrain | decoupled | 1.39952 | 0.09281 | 1.0883 | 0.0874 | 991 |

**Shift table (Coast)**

| Circuit | delta `coast_rolling_decel_ms2` | d/sigma | delta `coast_drag_area_m2` | d/sigma |
|---------|----------------------------------|---------|---------------------------|---------|
| Belgium | -0.03291 | -0.4823 | +0.0734 | +1.3055 |
| Monaco | -0.24266 | -3.2957 | +0.3631 | +3.3991 |
| Bahrain | -0.13170 | -1.6564 | +0.0283 | +0.5165 |

**Note on CoastView:** Coast uses raw CAN bus speed (`car["Speed"]/3.6`) in BOTH the incumbent and decoupled paths. The decoupled coast comparison is already a parity (Config C) comparison — the v-axis is identical. The observed coast shifts (1.5-3.4σ, 23-33% sample loss) are from `a_long` alone, not the v-source confound.

## Notes
- Incumbent path: `clean_longitudinal_from_raw` (finite-difference of cleaned raw speed)
- Decoupled path: `estimate_longitudinal` (total-energy Kalman-RTS with TV-denoised anchor)
- Coast decoupled: per-contiguous-segment estimation, regime='straight_coast' (LOOSE soft-obs)
- σ values are sqrt(covariance[i,i]) from the respective view's output
- Shift/sigma interpretation: |< 0.5| negligible; |0.5-1.0| notable; |> 1.0| significant
- Config C (parity): decoupled a_long + incumbent's raw v_at from spd_d['V'] (throttle views only)
- Coast path: both configs use raw car_data Speed (parity by construction)

## sig_a_soft_throttle HP Sweep: Config-C Shift Table

Generated: 2026-06-28T10:08:49.293952+00:00 UTC

HP values: 1.0, 2.0, 3.0, 5.0, 30.0

Config-C = parity (raw v + decoupled a_long). Shift = parity - incumbent.
30.0 = incumbent (same as sig_a_soft_other default; should match prior Config-C row exactly).

### TractionView Config-C Shifts per HP

| HP | Circuit | delta `a_t` (m/s²) | d/sigma_a | delta `b_t` (1/m) | d/sigma_b |
|----|---------|---------------------|-----------|-------------------|-----------|
| 1.0 | Belgium | +3.7982 | +2.5706 | -0.003858 | -1.9829 |
| 1.0 | Monaco | +1.6369 | +1.8761 | -0.001937 | -1.3983 |
| 1.0 | Bahrain | -11.6642 | -9.0279 | +0.014699 | +13.9251 |
| 2.0 | Belgium | +2.9185 | +1.9753 | -0.002693 | -1.3839 |
| 2.0 | Monaco | +2.3156 | +2.6539 | -0.002526 | -1.8237 |
| 2.0 | Bahrain | -10.8764 | -8.4182 | +0.013735 | +13.0119 |
| 3.0 | Belgium | +1.9000 | +1.2859 | -0.001460 | -0.7505 |
| 3.0 | Monaco | +3.0346 | +3.4779 | -0.003283 | -2.3704 |
| 3.0 | Bahrain | -10.4022 | -8.0511 | +0.013082 | +12.3940 |
| 5.0 | Belgium | +0.9205 | +0.6230 | -0.000256 | -0.1316 |
| 5.0 | Monaco | +3.1660 | +3.6285 | -0.003307 | -2.3875 |
| 5.0 | Bahrain | -8.8343 | -6.8376 | +0.010934 | +10.3585 |
| 30.0 [incumbent] | Belgium | +0.5462 | +0.3697 | +0.000294 | +0.1509 |
| 30.0 [incumbent] | Monaco | +3.4888 | +3.9986 | -0.003799 | -2.7428 |
| 30.0 [incumbent] | Bahrain | -7.9952 | -6.1882 | +0.009895 | +9.3741 |

### PowerDragView Config-C Shifts per HP

| HP | Circuit | delta P_max (W) | d/sigma_P | delta CdA (m²) | d/sigma_CdA |
|----|---------|-----------------|-----------|----------------|-------------|
| 1.0 | Belgium | -8328.7 | -0.8799 | +0.1119 | +1.7479 |
| 1.0 | Monaco | -72132.3 | -9.3362 | -0.2679 | -4.3396 |
| 1.0 | Bahrain | -26231.7 | -9.7614 | -0.0504 | -2.9173 |
| 2.0 | Belgium | -8777.8 | -0.9274 | +0.1129 | +1.7633 |
| 2.0 | Monaco | -94747.9 | -12.2633 | -0.4548 | -7.3665 |
| 2.0 | Bahrain | -33977.6 | -12.6438 | -0.0966 | -5.5973 |
| 3.0 | Belgium | -9745.6 | -1.0296 | +0.1095 | +1.7104 |
| 3.0 | Monaco | -98359.6 | -12.7308 | -0.4758 | -7.7064 |
| 3.0 | Bahrain | -30898.1 | -11.4979 | -0.0864 | -5.0043 |
| 5.0 | Belgium | -11343.1 | -1.1984 | +0.1012 | +1.5815 |
| 5.0 | Monaco | -98690.4 | -12.7736 | -0.4801 | -7.7760 |
| 5.0 | Bahrain | -30497.8 | -11.3489 | -0.0876 | -5.0750 |
| 30.0 [incumbent] | Belgium | -9307.8 | -0.9834 | +0.1035 | +1.6166 |
| 30.0 [incumbent] | Monaco | -103697.1 | -13.4217 | -0.5216 | -8.4478 |
| 30.0 [incumbent] | Bahrain | -30427.0 | -11.3225 | -0.0910 | -5.2735 |

**HP sweep notes:**
- Only Config-C (parity: raw v + decoupled a_long) is swept.
- Incumbent results are SHARED across HP values (not repeated per-HP).
- 30.0 row should reproduce the Config-C row from the main table above.

---

## G2 Coast Boundary-Lag Fix (2026-06-28)

**Verdict: HONEST-NULL** — acceptance bar not met.

### Root cause clarification

The boundary-lag hypothesis (F_vehicle=0 init + loose coupling) is real but accounts for almost none of the 22-26% sample loss:
- Belgium: 3 samples recovered by post-clamp fix (of ~380 gap vs incumbent)
- Monaco: 11 samples recovered (of ~374 gap)
- Bahrain: 1 sample recovered (of ~274 gap)

**True structural causes of sample loss:**
1. Speed filter (v > 12 m/s) eliminates the majority of off-mask time (pit lane, slow corners, Monaco hairpins)
2. Short coast segments (3-15 samples) + loose coupling (sig_a_soft_other=30 m/s²) → estimate_longitudinal cannot converge F_vehicle to correct coast force for brief coast events
3. Incumbent uses full-session stream smoothing → stable a_long even for brief coast blips; per-segment estimation cannot match this

### Post-clamp fix side effect (value distortion)

`np.minimum(res.a_long, a_long_raw_seg)` also changes the a_long VALUES of interior passing samples where noisy raw FD is more negative than the smooth filter estimate. This biases CdA toward higher drag (clamp samples 1972-5887 values per circuit, not just the 3-11 boundary recoveries).

### Sample count table (after G2 fix)

| Circuit | n_inc | n_dec_G1 | n_dec_G2fix | loss_G1 | loss_G2fix | bar (<10%) |
|---------|-------|----------|-------------|---------|------------|------------|
| Belgium | 1407 | 1020 | 1045 | 27.5% | 25.7% | FAIL |
| Monaco | 1502 | 1128 | 1156 | 24.9% | 23.0% | FAIL |
| Bahrain | 1265 | 991 | 994 | 21.7% | 21.4% | FAIL |

### Shift/sigma table after G2 fix (decoupled vs incumbent)

| Circuit | d_theta_R | d_R/σ | d_CdA | d_CdA/σ | R bar | CdA bar |
|---------|-----------|-------|-------|---------|-------|---------|
| Belgium | +0.18410 | +2.70 | +0.13698 | +2.44 | FAIL | FAIL |
| Monaco | +0.01795 | +0.24 | +0.48106 | +4.50 | PASS | FAIL |
| Bahrain | +0.03046 | +0.38 | +0.15641 | +2.86 | PASS | FAIL |

Note: Monaco and Bahrain theta_R improved vs G1 (from -3.30σ/-1.66σ to +0.24σ/+0.38σ) as a side effect of value distortion. Belgium theta_R worsened (-0.48σ → +2.70σ). All CdA shifts worsened.

### G3 direction

Do NOT wire coast decoupled path. Requires fundamentally different approach:
- Option A: keep incumbent coast path (already uses raw CAN speed — parity by construction)
- Option B: redesign to process per-lap windows (not 3-15 sample bursts) or enforce min_segment_len ≥ 30
- Option C: tighten coast coupling to sig_a_soft_other = 2-5 m/s² to allow filter convergence on short segments
