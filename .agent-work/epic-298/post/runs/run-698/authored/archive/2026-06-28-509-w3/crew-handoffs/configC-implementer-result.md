# IMPLEMENTER_RESULT — Config C Parity

## Status
DONE

## Files Changed
- `C:\Programs\f1Brainz-509w3-views\scripts\characterize_decoupled_views.py`

## Data Source Note
The `telemetry_store.db` has a session record for Belgium/Monaco/Bahrain 2023 Q but with empty pos/car data (shape `(0, 6)` and `(0, 8)`). This caused `session.pos_data["1"]` → `KeyError: '1'` for all circuits. Fixed by setting `STORE_PATH` to a non-existent path to force the FastF1 offline cache path, which has full telemetry for all three circuits. This is a data-layer issue (store was seeded with metadata only), not a code issue.

## Config C Table (verbatim from output)

```
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
```

## Key Observations

### Belgium (Spa) — pathology cleared by Config C
- Traction: B=0.73σ → C=0.37σ (negligible). The v-source confound was the main driver of the Belgium shift. Config C is clean.
- PowerDrag CdA: B=+1.63σ → C=+1.62σ (essentially unchanged — not v-driven). A ~1.6σ CdA shift persists independently of v-source.

### Monaco — pathology REDUCED but NOT cleared
- Traction: B=+10.3σ → C=+4.0σ. Still 4σ after controlling for v-source. About 60% of the signal was confound; 40% is from a_long.
- TractionAero: B=-8.4σ → C=-2.7σ. Reduced but still notable.
- PowerDrag: Config B was DEGENERATE (CdA=0); Config C is NOT degenerate (CdA=0.928). This is meaningful — the v-source confound was causing the Monaco PowerDrag collapse. However P_max still shifted -13.4σ and CdA shifted -8.4σ relative to incumbent.
- CONCLUSION: Monaco pathology is PARTIALLY v-confound, PARTIALLY a_long itself. The decoupled a_long estimator is producing anomalous acceleration values at Monaco even when v is held constant.

### Bahrain — pathology BARELY changes in Config C
- Traction: B=-7.1σ → C=-6.2σ. Essentially unchanged. The Bahrain pathology is almost entirely from a_long, not from the v-source.
- TractionAero: B=+11.5σ → C=+9.4σ. Same conclusion.
- PowerDrag: B=-17.7σ → C=-11.3σ (CdA: -7.9σ → -5.3σ). Reduced but large shifts remain.
- CONCLUSION: Bahrain pathology is predominantly from decoupled a_long itself.

### Summary verdict
Config C isolates that the a_long signal from the decoupled estimator is genuinely inconsistent with the incumbent at Monaco and Bahrain, independent of the v-axis source. The v-source confound explains:
- Belgium: ~50% of the shift (renders it negligible in C)
- Monaco: ~60% of the confounded signal was v-source; 40% remains as a_long artifact
- Bahrain: <15% of the shift was v-source; Bahrain pathology is almost entirely a_long

The decoupled estimator's `a_long` is the root-cause driver of the Monaco/Bahrain pathologies, not the v-axis mismatch.
