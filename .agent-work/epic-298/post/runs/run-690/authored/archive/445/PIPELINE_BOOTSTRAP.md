# Three-stage preprocessing pipeline + corner-geometry bootstrap (epic #445)

User direction (2026-06-14): corner geometry is INFORMATION that should feed back
into state synthesis to reduce uncertainty in velocity and **especially
acceleration**. A second-stage bootstrap. Target architecture:

```
processed telemetry
   --> [Stage 1] state synthesis        (windowless Matern-5/2 Kalman-RTS smoother)
   --> [Stage 2] corner ID & fitting    (segment corners, fit radius R(s))
        ^----------- BOOTSTRAP: feed corner geometry back to re-constrain the state
   --> [Stage 3] physics fitting         (grip / drag / downforce / power params)
   --> car parameterization --> driver energy efficiency --> prediction
```

## Why the bootstrap matters (the core mechanism)

Stage-1 acceleration is **prior-dominated**: per-node sigma ~29 m/s^2 (~3g),
because instantaneous acceleration (2nd derivative of ~4 Hz position) is
under-determined; the Matern jerk prior (ell) fills the vacuum. The ell/W/Hermite
sweeps proved the pointwise lateral-accel CEILING is set by the smoothing scale,
not the data (135g -> 2.3g across ell).

But the corner FIT supplies a near-deterministic acceleration that the smoother
could not:
- In a corner of fitted radius R, lateral accel = v^2 / R, with v MEASURED
  (sensor, sigma 0.49 m/s) and R from a circle/clothoid fit pooling ~10-30
  position points. Direction is centripetal (toward the fitted center).
- On straights (R -> inf), a_lat ~ 0 — also a strong constraint.

So geometry + measured speed give a clean acceleration field across the whole
lap. Fed back as a pseudo-measurement / local constraint in a Stage-2 re-smooth,
it **collapses the 3g acceleration uncertainty to a tight, data-driven value**,
and tightens velocity and position by consistency. The corner geometry is a
strong LOCAL prior that replaces the weak global jerk prior exactly where the
jerk prior was failing (in corners).

This is the "bootstrap our knowledge / whittle down uncertainty with hypotheses"
idea from earlier in the session, made concrete: fit a corner hypothesis, then
use it to sharpen the state.

## Stage details

- **Stage 1 (done, merged PR#474):** StintSmoother — position clean (sector gates
  20-48 ms), velocity good (sigma ~1 m/s), acceleration weak (sigma ~3g).
  NOTE: the smoothed |velocity| has isolated spikes (saw 477 km/h); use SENSOR
  speed for magnitude, smoothed position for geometry.
- **Stage 2 (building now):** corner segmentation by a_lat(s) peaks; adaptive
  node-count circle window (auto-scales: ~110 m arc at 330 km/h, ~30 m at the
  hairpin). Validated on VER Suzuka 2023: path = Suzuka, lap 5755 m (<1% off),
  130R at R=97 m @ 291 km/h (nominal 85-130). Then BOOTSTRAP back into the state.
- **Stage 3 (future):** physics fitting on the clean kinematics — grip mu*N
  (N = m g + k_df v^2), drag, downforce, power. Bounded because the kinematics
  are now tight. -> car params -> driver energy efficiency -> prediction.

## Open items before the bootstrap

- Confident corner algorithm first (current focus): clean over-detection (29 vs
  ~18 at Suzuka), tame high-speed a_lat over-read (v^2/R amplifies R noise at
  330 km/h), robust apex localization (a_lat-peak vs speed-min).
- Then design the Stage-2 feedback: corner-derived (a_lat magnitude + centripetal
  direction) as a measurement update on the acceleration state; straights as
  a_lat~0 constraints. Re-smooth, re-fit corners, iterate to convergence.

## Capability chain this unlocks

Clean bounded kinematics -> car force parameters (grip/drag/downforce/power) ->
per-corner apex-speed capability (slow vs fast) -> driver energy efficiency
(how well the driver keeps energy high within the car's envelope) -> prediction.
