# #445 Physics — Production Notes (overnight 2026-06-16, consolidated)

Feature-engineering pass on CLEAN per-session-calibrated kinematics (χ²≈1). Four prongs adjudicated by
the Admiral; details in LONGITUDINAL_REEVAL_FINDINGS.md, APEX_PACE_FINDINGS.md,
RIBBON_IDEALLAP_REEVAL_FINDINGS.md, MATERN72_VALIDATION.md. Source-of-truth caches:
calibrated_{aniso,braking}_nodes.npz, calibrated_hp.json, apex_corners.npz.

## ✅ VALIDATED — productionize

1. **Apex-speed cornering-pace channel — THE win.** Geometry-normalized apex speed: per weekend regress
   `log v_apex = β·log R + α_car` (shared corner-radius slope, per-car offset), take the 90th-pct
   on-limit residual, season-MEDIAN. Cross-sectional **Spearman vs quali pace = −0.89** (vs frontier-g's
   −0.15); resolves HAA (#1 grippiest → #6, matching #8 pace). Robust (leave-one-team-out −0.85→−0.90).
   It is the FIRST cornering observable in this epic that is pace-relevant. CAVEATS: only the SEASON
   aggregate is stable (per-round split-half +0.29 — noisy); fitted β≈0.32 (sub-√R; corner window mixes
   states). USE: a separate **cornering-pace** feature, NOT a per-race signal. Code: apex_extract.py +
   apex_feature.py. Production module: corner segmentation (a_lat peaks) on the calibrated smoother →
   per-corner (v_apex, R) → the per-weekend regression → season-median offset.

2. **Frontier-g downforce descriptor — keep as CHARACTER, not pace.** Pure-lateral apex frontier
   `G_lat=A_r+B_c v²` (shared environmental A, per-car downforce B). On clean kinematics orders RBR top
   (correct). It measures the downforce CEILING, which is NOT lap pace (HAA reads high). Keep B as an
   aero-platform descriptor; pair with apex-speed (pace) and drag (efficiency). AGGREGATION LESSON:
   aggregate per-weekend B with MEDIAN not MEAN (the HAA #1 artifact was a heavy-tail MEAN).

3. **Drag channel (CdA) — cleanest independent per-car aero signal.** Already validated (known 2023
   character: RBR/WIL low, MERC/FER/AMR high). Independent of the smoother (uses car_data). KNOWN GAP:
   the simple filter averages across mid-season upgrades (McLaren mis-tagged draggy) — a drag Kalman
   with an adaptive jump *might* help here (drag has higher per-race SNR than grip; untested).

4. **Season Bayesian downforce prior — the right tool for per-car capability from thin data.** Two-stage
   Kalman, obs noise `R = within-weekend var + σ²_op` (operating-point noise, ~34× the within-weekend
   var — MUST be included or the filter is overconfident). Exogenous track downforce-demand covariate
   (no field-coupling). Monza borrow-strength: 62% tighter, 70% more teammate-consistent. Baseline
   efficiency fingerprint: RBR efficient #1. Code: season_prior_bayes.py.

5. **Track ribbon κ(s) — sound track-geometry model.** Pooled per-track curvature (100+ laps, √N noise
   averaging). Clean slightly truer (Monza tightest radius 26m vs 44m contaminated). Usable as a track
   descriptor and as the substrate for apex-speed corner geometry.

## 🔧 INFRASTRUCTURE — adopt

6. **Per-session smoother calibration is MANDATORY.** Hardcoded HPs (StintSmoother(2,100,0.3,0.06))
   give χ²_pos=33 — over-trust meter-noisy position 6× and INVERT the car ranking (RBR 8th→top once
   fixed). Always calibrate: session_offset (delta) + fit_stint_hp (ell/sf/sig_pos to χ²≈1). Calibrated
   HPs vary widely per session (ell 0.8–7.0, sig_pos 1.4–2.5 m, delta 0–0.15 s).

7. **Matérn-7/2 smoother — recommended production upgrade.** Validated 18/18 sessions: held-out speed
   median 0.451 vs 5/2 0.759 m/s, glitch 2.5% vs 14.6%; 5/2 collapses to short-ell rough-velocity in
   3/18 sessions (med 7–11 m/s), 7/2 never. Cost ~1.10× (8-state vs 6-state). PR plan in
   MATERN72_VALIDATION.md (add order param, keep order-3 default + analytic P_inf for E4-nesting safety,
   Lyapunov P_inf for order≥4, regression-gate then flip default). This is the foundational upgrade —
   it improves every downstream channel and would fix the Suzuka short-ell thinness.

## ❌ RETIRED — not features

8. **Longitudinal / braking channel — RETIRE.** The "+0.48 corroboration" claimed earlier this session
   was a GSAT-clip artifact (lateral tyre ceiling silently applied to the longitudinal cloud via
   fit_weekend reuse; un-clipped corr ≈0). Compounded by G_lat extrapolation (80% of braking points
   beyond support) + 4.2 Hz sensor truncation (3.4× v² slope suppression; frontier peaks then DECREASES
   with speed). No κ·B_lat decomposition recovers drag. Only lateral-apex B + independent CdA are valid.
9. **Idealized lap time — NOT a per-car feature.** B is unidentifiable from single-weekend quali data
   (A/B collinear at low-aero tracks; only Hungary has enough nodes). Old "fixed-fractional fit-noise
   spread" confirmed, mechanism = noisy-B. (Ribbon ok; the sim is not a per-car feature.)
10. **v-term, per-car intercept, free exponent** — dead (collinearity wall, cond# 1e10–1e11).
11. **Adaptive jump on the grip channel** — no-op (the per-race grip-δ signal is below the operating-
    point noise; nothing to track). It might earn its keep on the higher-SNR DRAG channel only.

## GUARDRAILS / LESSONS
- The `GSAT` saturation clip must be an EXPLICIT required arg — never let a lateral ceiling silently
  leak onto a non-lateral axis (caused the longitudinal false-positive).
- Aggregate heavy-tailed per-weekend slopes with MEDIAN, not MEAN (the HAA #1 artifact).
- Kalman obs variance must include the between-race operating-point noise, not just within-weekend fit var.
- Smoother HPs are per-session; never hardcode.

## OPEN — morning decisions
- Wire the apex-speed cornering-pace channel into the feature pipeline? (Strong yes — it's the win.)
- Land the Matérn-7/2 PR (order param, keep 5/2 default, regression-gate, then flip)?
- Re-extract grip/apex on 7/2 kinematics once landed (fixes Suzuka-type thin/short-ell cases)?
- Build a drag Kalman + jump to fix the McLaren-upgrade mis-tag? (only channel where a jump might pay off)
