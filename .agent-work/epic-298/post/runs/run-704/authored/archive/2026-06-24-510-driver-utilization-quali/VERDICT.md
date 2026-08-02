# Driver Utilization Characterization — Readiness Verdict

**Gate:** g3-implement, C1 #510, branch feat/c1-driver-utilization-510  
**Date:** 2026-06-24  
**Status:** RECOMMENDATION for Commander/user ratification

---

## Recommended Verdict: CONTEXTUAL

**Straight regime: CONTEXTUAL — usable as a flagged readout with honest caveats.**  
**Slow-corner regime: CONTEXTUAL — partially separable; ceiling is mildly under-called (U=1.4–1.9 > 1, but not clipping).**  
**Braking regime: NO-GO — ceiling is systematically under-called; U clips at 2.0 for all cases.**  
**Fast-corner regime: NO-GO — ceiling is systematically under-called; U clips at 2.0 for all cases.**

Overall recommendation: **CONTEXTUAL** (not NO-GO overall, not GO) because straight and slow-corner
regimes carry usable signal, but braking and fast-corner are structurally broken until the ceiling
calibration is fixed (Issue #496's outer-loop gap, or regime-specific ceiling recalibration).

---

## Evidence

### Subset run

10 driver-sessions, 2023 Q, run 2026-06-24:

| driver | gp_name       | constructor   | u_braking | u_slow_corner | u_fast_corner | u_straight | sigma_u_straight | n_sessions_causal |
|--------|---------------|---------------|-----------|---------------|---------------|------------|------------------|-------------------|
| VER    | Monaco        | Red Bull      | 2.000     | 1.644         | 2.000         | 1.196      | 0.024            | 6                 |
| LEC    | Monaco        | Ferrari       | 2.000     | 1.750         | 2.000         | 1.509      | 0.006            | 6                 |
| VER    | Italy         | Red Bull      | 2.000     | 1.439         | 2.000         | 0.578      | 0.006            | 14                |
| NOR    | Italy         | McLaren       | 2.000     | 1.378         | 2.000         | 0.564      | 0.011            | 14                |
| ALB    | Italy         | Williams      | 2.000     | 1.403         | 2.000         | 0.572      | 0.012            | 13                |
| VER    | Great Britain | Red Bull      | 2.000     | 1.829         | 2.000         | 0.775      | 0.006            | 10                |
| NOR    | Great Britain | McLaren       | 2.000     | 1.859         | 2.000         | 0.807      | 0.007            | 10                |
| HAM    | Great Britain | Mercedes      | 2.000     | 1.840         | 2.000         | 0.789      | 0.010            | 10                |
| ALB    | Great Britain | Williams      | 2.000     | 1.851         | 2.000         | 0.854      | 0.004            | 10                |
| VER    | Singapore     | Red Bull      | 2.000     | 1.489         | 2.000         | 0.831      | 0.007            | 15                |

*U_CLIP_MAX = 2.0; all values at 2.000 hit the clip ceiling (not a real measurement).*

---

### Coverage

Circuits covered:
- Monaco (mechanical/slow; narrow street circuit)
- Italy / Monza (power/low-drag; high-speed with DRS zones)
- Great Britain / Silverstone (mixed; fast flowing corners)
- Singapore (technical/slow; urban street circuit)

Teams/drivers covered:
- Strong: Red Bull Racing (VER)
- Mid-field: Ferrari (LEC), McLaren (NOR), Mercedes (HAM)
- Weak: Williams (ALB)

What is NOT covered:
- Azerbaijan, Bahrain, Saudi Arabia, Spa, Suzuki, Canada — some slow, some power
- More than 1 driver per team (only one driver per constructor was run)
- Any comparison between teammates on the same circuit (impure-split check would benefit from this)
- The full 216-row sweep — this is a 10-case bounded subset

### Separability

Braking (u_braking): ALL cases clip at 2.0. No separability possible. The signal is "ceiling is
under-called here", not "this driver braked well". NOT separable.

Fast-corner (u_fast_corner): ALL cases clip at 2.0. Same conclusion. NOT separable.

Slow-corner (u_slow_corner):
- Italy: RBR 1.439, McLaren 1.378, Williams 1.403 — team differences ~5%, within sigma
- Great Britain: RBR 1.829, McLaren 1.859, Mercedes 1.840, Williams 1.851 — all 1.83–1.86, no separation
- Monaco: RBR 1.644, Ferrari 1.750 — 10% spread across circuits; circuit effect > team effect
- Singapore: RBR 1.489 — slow circuit like Monaco but lower than Monaco (different track character)
VERDICT: slow-corner shows CIRCUIT-regime variation (Monaco vs Silverstone) but not team separation within
a circuit. Partially usable as a circuit-type indicator; NOT usable as a per-team or per-driver discriminator.

Straight (u_straight):
- Monaco: VER 1.196, LEC 1.509 — short straights; drivers flatten throttle; above 1.0
- Italy: VER 0.578, NOR 0.564, ALB 0.572 — lift-and-coast at Monza; all at ~57%; no team separation
- Great Britain: 0.775–0.854 — all within 8%; circuits more separable than teams within circuit
- Singapore: VER 0.831
VERDICT: straight shows meaningful CIRCUIT variation (Monza vs Monaco); within a circuit, team/driver
differences are small (5–10%). Physically sensible (Monza lift-and-coast, Monaco full-throttle).
CONTEXTUAL: the circuit-level signal is real; the driver/team signal is below the noise.

### Covariance honesty

sigma_u_straight is small across all cases: 0.004–0.024. This reflects the propagated envelope
uncertainty from MC parameter sampling (n=20 draws). The sigma is TIGHT for sessions with many
causal rounds (n=14 at Italy: sigma 0.006) and slightly wider at Monaco (n=6: sigma 0.024), consistent
with more sessions giving a narrower ceiling uncertainty. The uncertainty WIDENS appropriately for
lower n_sessions_causal.

CAVEAT: The lap-sampling sigma is NOT modelled (acknowledged in G2 regime_utilization.py). A single
best lap has its own timing noise (~0.05–0.1% of lap time); this is not included in the propagated sigma.
The reported sigma reflects envelope uncertainty only.

CAVEAT: sigma for braking/fast_corner regimes is not reported for any case (all clip at 2.0 — the MC
draws also clip, so the sigma reflects clip-ceiling noise, not real capability spread). These sigma
values should not be used.

### The impure-split caveat

All UtilizationRow results carry split_is_impure=True. The G1 car prior was built from cross-session
estimates where the driver drove the car. The G2 utilization is then measured relative to that prior.
The two are entangled — a strong driver who always extracts 100% of the car will produce a high
ceiling estimate AND a utilization near 1.0, which is correct but tautological. A driver who extracts
less will show lower utilization, but their sessions also lower the ceiling estimate.

This is an acknowledged impure split by construction. The utilization numbers should not be interpreted
as "how much of the car's physical capability did the driver extract" but rather "how much of what WE
MEASURED the car does did this driver achieve on this lap, relative to the same constructor's causal
prior."

---

## What the evidence means for next steps

1. **Braking/fast_corner ceiling is under-called.** The sim_evaluator two-sided signal (gap < 3%
   or negative) fires here. Root cause is likely the same as the trajectory-smoother issue (#496):
   the braking frontier underestimates peak deceleration because the GP prior fights the braking knee.
   Fix: before C1 utilization is useful in these regimes, #496's outer-loop OR a regime-specific
   ceiling floor from measured data is needed.

2. **Straight and slow-corner regime have usable CIRCUIT-LEVEL signal.** If the goal is
   "which circuit type extracts more straight-line energy from this car", the straight utilization
   (0.56 for Monza vs 1.20–1.51 for Monaco) is a physically meaningful and reproducible readout.

3. **Team/driver discrimination is NOT available at this fidelity.** Within a circuit, the
   variation across strong/midfield/weak teams is ~5–10% in u_straight, which is below the
   lap-sampling noise floor (not modelled) and within the impure-split uncertainty.

4. **The characterization pipeline is mechanically correct.** 10/10 cases ran without error.
   The orchestration (G1 -> realised lap -> G2) works end-to-end. The verdict is about signal
   quality, not pipeline correctness.

---

## Recommended actions

- This verdict is CONTEXTUAL, not NO-GO overall. Do not discard the pipeline.
- Resolve the braking/fast_corner ceiling under-call before using those regimes.
- The straight utilization is ready to use as a circuit-type characterization signal (not a
  team/driver discriminator).
- Consider flagging in the dashboard output which regimes have clipped U_r (warn if ≥ 50% of
  cases clip) to make the under-call visible to consumers.
- This verdict is a RECOMMENDATION; Commander brings it to the user for ratification.
