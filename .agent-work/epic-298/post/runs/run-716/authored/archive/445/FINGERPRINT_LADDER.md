# Capability fingerprints — data-driven regime discovery (epic #445 Phase-3)

User instinct (2026-06-14): don't levy our own slow/fast-corner splits — let the DATA find the natural
capability axes. FP-1 (PCA on fixed-k_df-normalized μ signatures) = honest-null: only overall pace LEVEL
replicated; regime axes failed split-half (cos ~0.3-0.4 vs 0.7 bar). Next: confront whether regime-character
even exists (level vs shape), and fix the signature (raw a_lat not normalized μ; try metric variants).

## FP-2 — Metric variants × level/shape variance decomposition (worktree expt-fp2, branch expt/448-fp2)
Question: (A) of the STABLE (replicable) cross-car capability variance, how much is overall LEVEL vs
regime SHAPE? (B) which METRIC best reveals stable shape — raw acceleration, force, or longitudinal power?

Signature: same 24 speed bins (25-88 m/s), field-relative (−field median / field IQR per bin/channel/race),
teammates pooled at sample level. THREE metric variants (run all three):
- V1 ACCEL (mass-free): lateral = raw a_lat = v²·κ(s); longitudinal = a_long = dv/dt (peak fwd + peak brake).
- V2 FORCE: lateral = m(lap)·a_lat; longitudinal = m(lap)·a_long. [×mass]
- V3 LONG-POWER: lateral = m(lap)·a_lat (force, lateral does no work so NOT power); longitudinal =
  m(lap)·v·a_long (energy-rate: power-add fwd, power-remove braking).
MASS m(lap) ESTIMATED AT TIME OF MEASUREMENT — do NOT assume static. m(lap)= reg_min_mass(year, ~798 2022)
+ fuel(lap); fuel ≈ linear from ~start (per-race full-race fuel, ~100-110 kg) to ~end (~2 kg), by lap
number of each sample. Per-race fuel slope. (Mass ~common across cars → relative comparison robust; the
point is the time-variation, not absolute.)

LEVEL/SHAPE decomposition (per metric variant) — the gate:
- Per (car, race) signature s[c,r,b]. Split: level L[c,r] = mean over bins; shape u[c,r,·] = s − L (sum-zero).
- Variance-components: s[c,r,b] = μ[b] + L_c + u_c[b] + ε[c,r,b] (car-consistent level + shape, + car×race
  residual). Estimate σ²_level (between-car var of L_c), σ²_shape (between-car var of u_c over bins),
  σ²_noise (residual). Report shares + the key ratio STABLE-SHAPE / STABLE-LEVEL.
- Cross-check: split-half across each car's races — correlate half-A vs half-B for L_c (expect high) and
  u_c (the test). Stable part = reliability × variance; should match the components model.
- Decompose per-channel (lateral / long-acc / long-brk) AND pooled — a car can be level-different overall
  but shape-different in one channel.
- Unit = (car, YEAR) not car (mid-season upgrades break fixed-car). Equal-bin-weight first; note occupancy.

Verdict gate (per metric): σ²_shape ≈ noise → regime fingerprint dead for that metric (feature = level +
replicables like compound deg). σ²_shape real+significant → PCA the car-consistent shape covariance u_c
(de-noised — more stable than FP-1's raw-signature PCA). Compare which metric (accel/force/power) gives the
largest stable σ²_shape — i.e., which best exposes regime-character.

Light (reuse FP-1's per-sample harvest in sibling expt-fp1/scripts/experiments/fp1_run.py — extend to return
RAW a_lat (pre-normalization) + LAP number per sample for mass; no smoother). ~6 races 2022-24. ONE bounded
foreground run; EVID under THIS worktree; never background-end-turn. `py`; numpy/scipy.

Return: per metric (V1/V2/V3) the level/shape variance shares + stable-shape/stable-level ratio + split-half;
which metric maximizes stable shape; honest-null status (regime-character real or just level); if real, the
de-noised shape modes; evidence paths.
