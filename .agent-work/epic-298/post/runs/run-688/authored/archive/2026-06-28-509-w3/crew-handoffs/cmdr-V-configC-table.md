# G1 Characterization Table: Decoupled vs Incumbent

Generated: 2026-06-28T06:49:48.926684+00:00 UTC

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
