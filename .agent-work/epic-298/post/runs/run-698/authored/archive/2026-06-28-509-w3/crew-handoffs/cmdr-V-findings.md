# Commander V Findings — #523 Decoupled Throttle/Coast Views

## Verdict

**HONEST-NULL.** All three throttle/coast views (TractionView, PowerDragView, CoastView) were measured against the incumbent `clean_longitudinal_from_raw` across RBR 2023-Q Spa/Monaco/Bahrain and HELD. `decision:decoupled_1d_longitudinal` remains WIRED for braking only. Throttle/coast views stay on `clean_longitudinal_from_raw`.

## Per-view Results

| View | Belgium shift | Monaco | Bahrain | Verdict |
|------|--------------|--------|---------|---------|
| TractionView (a_t, b_t) | +0.73σ / -0.30σ | +10.3σ (b_t=0, wrong-sign) | -7.1σ / +11.5σ (swap) | HOLD |
| PowerDragView (P_max, CdA) | -1.02σ / +1.63σ | degenerate=True (20σ+) | -17.7σ / -7.9σ | HOLD |
| CoastView (theta_R, CdA) | -1.54σ / +2.53σ | -2.78σ / +3.39σ | -3.35σ / +1.38σ | HOLD |

Measurement script: `scripts/characterize_decoupled_views.py`

## Root Causes

### Throttle/PowerDrag (TractionView + PowerDragView)
The decoupled estimator uses smoothed trajectory speed (`s.speed` from KinematicSample) as the v-axis for the frontier, while the incumbent uses raw-sensor-interpolated speed from `spd_d["V"]`. The P/v power-drag signal is highly sensitive to v accuracy:
- Monaco: PowerDrag `degenerate=True` (CdA=0), TractionView `b_t=0` (10σ+ shifts)
- Bahrain: a_t and b_t parameter swap (7-11σ shifts)

This is a structural v-source discrepancy — not tunable away.

### Coast (CoastView)
The Kalman-RTS filter on coast segments produces positive `a_long` for 23-33% of samples where the finite-difference incumbent gives negative. These samples fail the `al_at < 0` filter before CoastView's lower-quantile fit. CoastView's regen-robust methodology (τ=0.20) assumes the full sample set; systematic loss biases the lower envelope.

## Decision Anchor Updated

`docs/architecture/decisions/decoupled-1d-longitudinal.md` — section "#523 Throttle/Coast Verdict: Measured-and-Held (2026-06-28)" added.

## Follow-on

Fix-or-hold issue filed: **#546** — `#523 follow-on: investigate decoupled-estimator throttle/coast before re-evaluating wiring`

Required before re-evaluation:
1. Characterize with matched v-source: use raw-sensor-interpolated speed (`spd_d["V"]`) in the decoupled path's frontier v-axis for throttle/drag views
2. Investigate coast sample-loss mechanism (regen pulse at coast start? filter lag at segment boundaries?)

## PR

`feat: #523 measure decoupled a_long throttle/coast — honest null (Refs #509)`

Branch: `feat/509w3-decoupled-views`
