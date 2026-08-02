# Geometry -> physics substrate session (2026-06-14) — consolidation

Built the geometry->physics scaffolding for car capability (epic #445). What is
SOLID, what is NOT, and the near-term direction. Working code: .agent-work/445/
envelope/.

## What holds (trust these)
- **Geometry reconstruction**: smoothed position is clean (Suzuka path validated,
  lap length within 1%, 130R radius 97 m @ 291 km/h — textbook). Speed from the
  SENSOR (the smoothed |velocity| has isolated spikes ~477 km/h; never use it for
  magnitude — use sensor speed + smoothed position).
- **Corner segmentation**: corners = peaks in sideways-accel along the lap;
  radius from an adaptive node-count circle fit (auto-scales with speed). Apex
  cornering grip = v^2/R is scale-STABLE (unlike pointwise accel).
- **Cornering grip vs speed**: clean, physical, rises 2.6g->4.5g with speed
  (= downforce). This is the reliable cornering observable.
- **Mechanical grip (common level)**: ~3.0-3.3g for ALL cars across 6 tracks,
  teammates agree. And it does NOT rise with softer compound (flat across C3-C5)
  -> on fresh quali tyres peak grip is ~compound-independent (compounds differ in
  WEAR not peak, per the degradation work). So the mechanical anchor is more
  trustworthy than feared.

## What does NOT hold (do not lean on these yet)
- **Pointwise lateral acceleration**: prior-dominated. The smoother's accel state
  has sigma ~3-7g; pointwise a_lat ceiling swings 135g->2.3g with the smoothing
  scale (ell/window/Hermite all confirmed). Curvature is an irreducible 2nd
  derivative of noisy position. USE corner-level apex (circle fit), not pointwise.
- **Per-car downforce**: too noisy at single-session level. Across 6 tracks the
  per-track downforce ORDER scrambles unphysically (Williams "most downforce" at
  Hungary/Britain). The car-distinguishing signal is a small DIFFERENCE below the
  per-corner scatter (+-0.5-1g). The earlier "RBR more downforce" (2-track) did
  not survive more tracks.
- **Absolute braking**: resolution-limited. Speed sensor is 4.2 Hz; the ~5g bite
  lasts <240 ms, so the sharpest derivative (3-pt central) tops at ~3.5g. A
  consistent LOWER BOUND (fine for car-vs-car), not the true peak.

## Target architecture (the bootstrap)
3 stages: processed telemetry -> state synthesis (smoother, merged) -> corner ID
& fit -> [BOOTSTRAP corner geometry back into the state to crush the 3g accel
sigma: a_lat=v^2/R centripetal in corners, ~0 on straights] -> physics fitting
(grip mech+downforce, power, drag). See PIPELINE_BOOTSTRAP.md.

## Near-term direction: correlation in RACE conditions (user, 2026-06-14)
Quali freezes compound/fuel/wear/config -> can't separate them; downforce (a
small difference) has no within-weekend variation to lean on. RACE gives, within
ONE fixed car config: multiple compounds, full fuel burn-down, tyre aging through
stints -> a matrix of conditions to regress out (compound [use the degradation
model], fuel mass, tyre age), leaving intrinsic car grip measured MANY times.
Recurring compounds/conditions cross-link observations into one network. This is
how downforce (and a conditions-normalized car parameterization) becomes
resolvable. Near-term because the degradation model + geometry method + race
telemetry all already exist; the work is wiring grip-from-geometry onto race laps
with compound/fuel/age as covariates. Same data prediction lives in.

## Capability chain (unchanged goal)
clean kinematics -> car force params (mech grip / downforce / power / drag) ->
per-corner apex-speed capability -> driver energy efficiency (utilization of the
pseudo-ceiling; we never observe the ceiling, only measurements approaching it
with varying reliability) -> prediction.
