# G2 M3 Result -- 1D Physics-Constrained Longitudinal Filter

**Date:** 2026-06-24
**Mechanism:** m3 -- Decoupled 1D Kalman-RTS on speed channel
**Re-run:** cd C:/Programs/f1Brainz && py C:/Programs/f1Brainz/.claude/worktrees/agent-aff9de88b4e6d6d6c/scripts/run_m3_scoreboard.py

---

## Mechanism (3 sentences)

M3 bypasses the 2D position smoother for longitudinal dynamics entirely: it runs a separate small 1D Kalman-RTS filter on the raw speed channel inp.v with state [v, a], using regime-dependent jerk process variance (sig_a_brake >> sig_a_other) so sharp braking onsets are a predicted feature of the process model rather than fighting a position-smoothness prior. An optional soft accel pseudo-obs from inp.a_long_raw weakly links the filter to the raw sensor. The 2D StintSmoother is untouched; M3 is a parallel 1D estimator whose a_long output feeds directly into the scoreboard seam.

---

## Synthetic Step Sanity Check

**Setup:** v0 = 80 m/s, true decel = -45 m/s2 step at t = 1 s, dt = 40 ms, sig_v = 0.15 m/s.
Soft accel obs = truth + N(0, 1) m/s2. Filter knows brake regime from t >= t_brake_start.

| Metric | Value |
|--------|-------|
| True knee | -45.0 m/s2 |
| Recovered knee | -48.97 m/s2 |
| Recovered plateau | -47.43 m/s2 |
| Error (recov - true) | -3.97 m/s2 |
| PASS (abs(error) < 5) | **True** |

Interpretation: 4 m/s2 overshoot at step edge from the RTS backward pass is expected. At 40 ms synthetic sampling the 1D filter correctly identifies and passes through the sharp decel without Gaussian-smoothness rounding. The mechanism is sound in isolation. The Bahrain failure is a DATA BANDWIDTH problem (see below), not a mechanism defect.

---

## Jerk-Process-Variance Sweep (Bahrain 2023 VER)

Reference: raw_knee = -52.13 m/s2

| sig_a_brake | knee (m/s2) | gap_vs_raw | ringing | ring_ok |
|-------------|-------------|------------|---------|---------|
| 5           | -38.74      | +13.39     | -8.78   | YES     |
| 10          | -39.24      | +12.89     | -8.69   | YES     |
| 20          | -39.44      | +12.69     | -8.68   | YES     |
| 35          | -39.49      | +12.64     | -8.67   | YES     |
| 50          | -39.50      | +12.63     | -8.67   | YES     |
| 80          | -39.51      | +12.62     | -8.67   | YES     |

The knee does not move with sig_a_brake at all. Soft obs weight sweep (sig_a_soft = sig_a_brake x 0.1 to 20) shows identical insensitivity. Both sweeps confirm the Bahrain failure is structural, not tunable.

---

## Full Scoreboard -- m3 + gaussian + kind3 (all 3 circuits)

| Circuit | Lap | n_brake | n_coast | gaussian_knee | kind3_knee | m3_knee | raw_knee |
|---------|-----|---------|---------|---------------|------------|---------|----------|
| Bahrain | 14  | 18      | 0       | -39.50        | -39.42     | -39.49  | -52.13   |
| Monaco  | 29  | 21      | 1       | -38.07        | -37.60     | -38.57  | -37.51   |
| Belgium | 21  | 22      | 0       | -34.93        | -37.41     | -37.32  | -38.84   |

**Per-variant detail:**

| Circuit | Variant  | knee   | raw_knee | gap_vs_raw | ringing | raw_ring | ring_gap | ring_ok |
|---------|----------|--------|----------|------------|---------|----------|----------|---------|
| Bahrain | gaussian | -39.50 | -52.13   | +12.63     | +0.46   | -2.86    | +3.32    | NO      |
| Bahrain | kind3    | -39.42 | -52.13   | +12.71     | +0.41   | -2.86    | +3.28    | NO      |
| Bahrain | m3       | -39.49 | -52.13   | +12.64     | -8.67   | -2.86    | -5.81    | YES     |
| Monaco  | gaussian | -38.07 | -37.51   | -0.56      | +13.14  | +5.64    | +7.50    | NO      |
| Monaco  | kind3    | -37.60 | -37.51   | -0.09      | +13.38  | +5.64    | +7.73    | NO      |
| Monaco  | m3       | -38.57 | -37.51   | -1.06      | +2.97   | +5.64    | -2.68    | YES     |
| Belgium | gaussian | -34.93 | -38.84   | +3.91      | +4.36   | +4.57    | -0.21    | YES     |
| Belgium | kind3    | -37.41 | -38.84   | +1.43      | +4.44   | +4.57    | -0.13    | YES     |
| Belgium | m3       | -37.32 | -38.84   | +1.52      | -2.21   | +4.57    | -6.78    | YES     |

---

## Failure Modes (Honest)

### PRIMARY FAILURE: Bahrain knee not recovered -- structural bandwidth limitation

At the first braking sample (i=26, t=4951.7 s), the speed finite difference gives only -21.2 m/s2 (dt=439 ms, dv=-9.3 m/s) despite a_long_raw = -52.13 at that sample. The peak decel was achieved within a sub-sample window at the ~18 Hz raw speed sensor rate; by the time the 4 Hz position grid fires, the speed has already fallen from ~90 to 79.4 m/s. The 1D filter on the 4 Hz speed channel cannot reconstruct a transient faster than ~0.5 Hz.

This is a bandwidth problem, not a filter design problem. Raising sig_a_brake or tightening soft obs coupling does nothing because:
- Soft obs are aligned to the same 4 Hz grid (the -52 spike in a_long_raw[26] is surrounded by -37 and -26 neighbors; the speed trajectory implies -21 to -38 over those intervals)
- The RTS smoother is forced toward speed-consistent trajectories regardless of the prior

**This failure is shared by ANY mechanism operating on inp.v at the 4 Hz position-grid rate.**

### Monaco slight over-deepening

Monaco m3 knee = -38.57 vs raw -37.51 (over-corrects by 1.06 m/s2). Small RTS backward-pass artefact. Not clinically significant.

### Bahrain ringing: structural win (not the primary target but notable)

M3 ringing = -8.67 m/s2 vs Gaussian +0.46, kind3 +0.41. Both baselines fail ring_ok on Bahrain; M3 satisfies it. The 2D smoother position-coupling creates positive a_long artefacts in non-throttle zones; a 1D speed-only filter has no such coupling.

---

## Invariant Note: decision:two_cycle_external_anchor_design

M3 does not use the kind=3 anchor channel. The two-cycle invariant is not touched. M3 a_long derives from inp.v (raw speed, external and un-biased) and optionally inp.a_long_raw (raw sensor reference, also external and un-biased). M3 is a fully independent estimation path; the invariant does not apply and is not extended.

---

## Decoupling Boundary

M3 adds a small parallel 1D longitudinal estimator. It does NOT replace StintSmoother, modify AccelObs or emit_accel_obs, or do a full joint collocation. The 2D smoother still owns geometry. If productionised, M3 registers as a variant in the scoreboard with no changes to the 2D smoother path.

---

## Soundness Self-Assessment

- Monaco ringing gain: REAL. Structural elimination of 2D position coupling, not suppression.
- Belgium knee: REAL. 1D filter reads accel from 4 Hz speed derivative; Belgium braking events are sustained enough to appear within 263 ms windows. Matches kind3 within 0.1 m/s2.
- Bahrain failure: HONEST. Not a tuning miss. The -52 peak is sub-4Hz; same limitation as 2D smoother. M3 does not worsen it but does not fix it either.
- No cherry-picking: all three circuits, all three metrics as measured.

---

## Re-Run Command

    cd C:/Programs/f1Brainz
    py "C:/Programs/f1Brainz/.claude/worktrees/agent-aff9de88b4e6d6d6c/scripts/run_m3_scoreboard.py" 2>&1 | grep -E "STEP|sig_a_brake|knee|ring|Variant|True|False|Belgium|Monaco|Bahrain|---"

Prototype files:
- C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/m3/filter_m3.py
- C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/m3/run_m3_scoreboard.py

---

## Recommendation: MIXED

**Monaco ringing:** M3 is the cleanest structural fix found (2D position coupling eliminated at the mechanism level). Ringing drops from 13.1 to 2.97 m/s2 (ring_ok YES). Recommend as the ringing solution if the G3 winner needs to address Monaco ringing structurally.

**Bahrain knee:** M3 is a dead end at the position-grid speed channel. The -52 m/s2 peak is temporally compressed below the 4 Hz bandwidth. Recovering it requires access to raw speed sensor at ~18 Hz resolution, OR a 2D/joint filter with a physics process model that hard-constrains the braking peak rather than soft obs. Mechanisms that inject the raw peak as a hard anchor or operate at the raw sensor rate are the correct path for Bahrain.

**Belgium:** does not regress, matches kind3. No concern.

---

## Workflow Feedback

- **Handoff gaps:** g2-COMMON.md does not specify that inp.t is the ~4 Hz GPS position grid while the raw speed sensor operates at ~18 Hz. This bandwidth gap is the single most important constraint for M3 viability on Bahrain and was discovered empirically. Adding "inp.t is the position GPS grid (~4 Hz, ~263 ms per sample); a_long_raw comes from an ~18 Hz raw sensor and is interpolated to this grid" would have predicted the Bahrain failure immediately and saved the sig_a_brake sweep.
- **Context rediscovered:** _build_case_inputs internals (n_samples=341, dt~263ms, n_brake=18 on Bahrain) were key. Inspected live session data to understand observation bandwidth.
- **Instructions improvised around:** Checklist engine (scripts/checklist_engine.py) is not accessible from the worktree without extra path manipulation; executed all plan steps directly without engine format. Compliant with closest-compliant-thing rule.
- **What would have made this easier:** One line in handoff -- "effective temporal resolution of inp.v is ~4 Hz (~263 ms)." Would have immediately flagged the bandwidth constraint for Bahrain.
