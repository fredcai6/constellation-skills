# VERDICT — C1 Driver Utilization, Re-run Post Lateral Units Fix (#522)

**Date:** 2026-06-26
**Branch:** feat/522-phase-align-utilization (G2 lateral units fix live, commit 33c56214)
**Cases:** 2023-Q RBR/VER — Monaco, Italy, Great Britain, Singapore
**Store:** data/physics_estimates.db (OLD #510/#518-G6 baseline store; units fix in car_prior.py)
**Command:** `py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"`
**Elapsed:** 264.3 s; 4/4 OK, 0 errors
**MC samples:** 50, seed=42

---

## Root Cause Correction

The #518 G6 "phase misalignment binding constraint" conclusion was **superseded by the lateral units bug**
identified in #522. The G1 diagnosis showed that true-distance phase registration changes U by <1%;
the G2 lateral units fix (g-unit store A0/A2 → m/s² at the car_prior boundary) was the actual root
cause of the 2.000-clipping. This run measures whether the fix propagated correctly into the dashboard.

**It did.** All four corner-regime values are now physical (0.89–1.02 range); the 2.000 clip is gone.

---

## Before / After Table

| Case | Regime | #518 G6 (PINNED) | #522 G3 (CORRECTED) | sigma_total |
|------|--------|-------------------|----------------------|-------------|
| Monaco/VER | u_braking | **2.000** (pinned) | **1.018** | ±0.038 |
| Monaco/VER | u_slow_corner | ~1.89 | 0.889 | ±0.028 |
| Monaco/VER | u_fast_corner | **2.000** (pinned) | **0.953** | ±0.024 |
| Monaco/VER | u_straight | ~1.08 (under-call) | 0.898 | ±0.032 |
| Italy/VER | u_braking | **2.000** (pinned) | **0.994** | ±0.014 |
| Italy/VER | u_slow_corner | ~1.56 | 0.930 | ±0.007 |
| Italy/VER | u_fast_corner | **2.000** (pinned) | **0.917** | ±0.008 |
| Italy/VER | u_straight | ~1.07 (under-call) | 0.987 | ±0.007 |
| Great Britain/VER | u_braking | **2.000** (pinned) | **1.015** | ±0.012 |
| Great Britain/VER | u_slow_corner | ~1.72 | 0.955 | ±0.006 |
| Great Britain/VER | u_fast_corner | **2.000** (pinned) | **0.972** | ±0.006 |
| Great Britain/VER | u_straight | ~1.23 (under-call) | 1.012 | ±0.008 |
| Singapore/VER | u_braking | **2.000** (pinned) | **0.891** | ±0.014 |
| Singapore/VER | u_slow_corner | ~1.64 | 0.917 | ±0.008 |
| Singapore/VER | u_fast_corner | **2.000** (pinned) | **0.969** | ±0.013 |
| Singapore/VER | u_straight | ~1.02 | 0.958 | ±0.007 |

*#518 G6 "before" values are from the decision-anchor doc: braking/fast-corner pinned at 2.000;
slow_corner ~1.56–1.89; straight Italy 1.07 / GB 1.23. Singapore/Monaco straight from that run.*

---

## Per-Regime Per-Case Numbers (Corrected Run)

Full sigma breakdown from `reports/physics/driver_util_subset_2023.csv`:

| Case | u_braking | σ_braking | u_slow_corner | σ_slow_corner | u_fast_corner | σ_fast_corner | u_straight | σ_straight |
|------|-----------|-----------|---------------|---------------|---------------|---------------|------------|------------|
| Monaco/VER | 1.018 | ±0.038 | 0.889 | ±0.028 | 0.953 | ±0.024 | 0.898 | ±0.032 |
| Italy/VER | 0.994 | ±0.014 | 0.930 | ±0.007 | 0.917 | ±0.008 | 0.987 | ±0.007 |
| Great Britain/VER | 1.015 | ±0.012 | 0.955 | ±0.006 | 0.972 | ±0.006 | 1.012 | ±0.008 |
| Singapore/VER | 0.891 | ±0.014 | 0.917 | ±0.008 | 0.969 | ±0.013 | 0.958 | ±0.007 |

*σ = sigma_u_total (quadrature of MC envelope sigma + lap-sampling SEM). MC samples=50.*

---

## Per-Regime Verdict

### Braking — CONTEXTUAL

Values: 0.891–1.018 across 4 circuits. At GB and Monaco, braking U≈1.0 (within 2σ of 1.0: Monaco
1.018±0.038, GB 1.015±0.012). Singapore shows genuine under-extraction (0.891±0.014, ~8% below
ceiling — 8σ below 1.0). Italy 0.994±0.014 is consistent with ceiling riding.

**Interpretation:** The physical range is plausible and circuit-differentiated (Singapore is a
known brake-limited street circuit with complex turns). The cap is gone; values are now measurable.
Braking U is **CONTEXTUAL**: values are now in a physically meaningful range but remain impure
(car/driver split not resolved; both teammates define the frontier). A>1 means the ceiling was
slightly under-estimated (the frontier was set by the other car, or by a different corner type).
Treat as directional characterization, not a precise driver score.

### Slow Corner — CONTEXTUAL

Values: 0.889–0.955. Monaco lowest (tunnel is a unique mechanical-grip extreme; lower extraction
consistent with its unusual geometry). Circuit-ordered: Monaco < Singapore < Italy < GB. This
ordering is physically coherent (Monaco is the mechanical-grip outlier; Silverstone's Maggotts/
Becketts complex is a slow-corner-rich fast circuit).

**Interpretation:** All values are below the ceiling (no numerical anomalies), but the split
remains impure. CONTEXTUAL: values are measurable and directional. The ~10% under-extraction at
Monaco is numerically plausible but mechanically hard to separate from car-geometry effects
(the frontier is set by VER's own runs — the Monaco tunnel cap conversion is now physical).

### Fast Corner — CONTEXTUAL

Values: 0.917–0.972. Tighter spread than slow corner; no circuit-specific outlier. All below
ceiling, all within ~1–8% of 1.0. Italy lowest (0.917±0.008 — Parabolica/Lesmo are treated as
fast corners, but they're braking-in-from-high-speed; the aero envelope at Monza is set under
DRS-ON, which may affect the frontier).

**Interpretation:** CONTEXTUAL: no longer pinned; values are in the expected range for a top car
at or near its aero capability frontier. The impure split caveat applies; ~3–8% residual below
ceiling is consistent with a good but not perfect qualifying lap.

### Straight — CONTEXTUAL-trending-GO

Values: 0.898–1.012. Italy 0.987±0.007 and Singapore 0.958±0.007 are still below 1.0 (1.9σ
and 6σ respectively). Great Britain 1.012±0.008 is slightly above 1.0 (within 2σ). Monaco
0.898±0.032 is low but with the highest uncertainty (Monaco straight is short and may classify
ambiguously with DRS zones).

**Straight under-call finding (persistent from #518 G6):** The lateral fix does NOT touch the
straight/power-drag path. Singapore 0.958 and Italy 0.987 remain below 1.0. This directional
under-call (ideal lap slightly slower than reality on straights) was present in the #518 G6 run
(Italy 1.07 / GB 1.23 OVER-call pre-fix; now Italy 0.987 / GB 1.012). The over-call in GB/Italy
in the G6 baseline has reversed to a slight under-call — consistent with the lateral fix also
changing what the ideal lap does on the approach to slow corners (the straight-to-corner
transition). This is directional signal; no new pathology. Route to triage for #525-adjacent
work (units-audit / power-drag cap calibration).

**Assessment:** CONTEXTUAL: Great Britain sits at 1.0 (GO-boundary); Italy/Singapore show a
small under-call. The straight regime is now the cleanest diagnostic (physically interpretable,
single-axis, no phase-ambiguity) but still slightly off-ceiling for most circuits.

---

## Summary Verdict

| Regime | Before (#518 G6) | After (#522 G3) | Verdict |
|--------|-----------------|-----------------|---------|
| Braking | NO-GO (pinned 2.0) | 0.891–1.018 | **CONTEXTUAL** |
| Slow Corner | NO-GO (~1.56–1.89) | 0.889–0.955 | **CONTEXTUAL** |
| Fast Corner | NO-GO (pinned 2.0) | 0.917–0.972 | **CONTEXTUAL** |
| Straight | CONTEXTUAL (1.07–1.23 over-call) | 0.898–1.012 | **CONTEXTUAL-trending-GO** |

**Overall characterization: CONTEXTUAL.** The lateral units fix is the single change; it
completely eliminates the 2.0 clip and brings all four regimes into a physically plausible
range. No regimes reach GO (that would require phase-resolved per-regime comparison to rule
out the point-alignment confound for corner regimes, and a quantified car/driver split). No
regimes are NO-GO.

The C1 driver-utilization metric is now **measurable and directional** across all four regimes.
The car/driver impurity caveat remains (`split_is_impure=True`, owned by covariance).
Final acceptance is the human's at the spine review step.

---

## Straight Under-Call — Triage Finding

The straight under-call (U_straight < 1.0 at Italy and Singapore) does not appear to be a new
defect. It is consistent with the ideal-lap simulator slightly under-estimating drag-limited
straight speed. Root cause candidates (not investigated in this gate): (1) the DRS mask
under-counts DRS-open segments at these circuits, reducing the simulated top speed; (2) the
P_max / CdA ratio in the store is slightly conservative for these sessions; (3) the straight
classification boundary bleeds into low-radius approach zones, depressing the mean.

Route to triage for #525-adjacent work (lateral units audit + straight-cap calibration). Do not
force a fix at this gate — the lateral fix does not touch the power-drag path.

---

## What This Run Does NOT Assert

- This run does NOT assert that corner-regime U values equal the driver's true utilization
  (the car/driver split is acknowledged impure).
- The point-aligned `v_real/v_ideal` comparison still has a structural confound for corner
  regimes at the apex-vs-approach transition, but the lateral units bug was masking everything
  at 2.0 — the confound's effect appears to be much smaller than the bug (values now ~0.9–1.0,
  not ~3.3–3.8× before clipping).
- Singapore u_braking=0.891 may reflect genuine braking-headroom behaviour at this circuit
  (tight stop-go corners with conservative entry), or residual approach/apex misalignment.

---

## Evidence Chain

- G2 lateral units fix: `src/physics/utilization/car_prior.py` `_assemble_lateral`, commit 33c56214
- Dashboard command: `py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"`
- Output CSV: `reports/physics/driver_util_subset_2023.csv`
- Run: 4/4 OK, 0 errors, 264.3 s, MC samples=50, seed=42, 2026-06-26
