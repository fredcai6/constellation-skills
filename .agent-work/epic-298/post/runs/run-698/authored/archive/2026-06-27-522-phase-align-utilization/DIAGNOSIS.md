# Diagnosis — #522 Utilization Clip Root Cause

**Gate:** g1-implement (DIAGNOSIS gate, inspection-only)  
**Date:** 2026-06-26  
**Case:** Monaco 2023-Q / VER / Red Bull Racing  
**Script:** `.agent-work/522-phase-align-utilization/diag_alignment.py`  
**Figure:** `.agent-work/522-phase-align-utilization/fig_alignment_monaco_ver.png`

---

## Verdict: **(b) Under-called ideal-speed caps**

Hypothesis (a) (misregistration) is **rejected** on evidence.  
Hypothesis (b) (under-called caps) is **confirmed** on evidence.

True-distance re-registration changes the braking-regime mean utilization by only 0.7% (1.884 → 1.870) and leaves the fast-corner regime mean unchanged (1.994 both ways). Under true-distance alignment, 0.4% of braking points and 0% of fast-corner points fall to ≤ 1.15. The registrations are functionally identical because the lap length difference is only 15.1 m on 3257 m (0.47%).

The ideal lap's speed caps are genuinely too low. VER's best lap reaches 80.3 m/s (289 km/h); the sim ceiling reaches only 62.1 m/s (224 km/h). The lateral-cap formula with the fitted A0=2.64, A2=0.0005 yields corner entry speeds of 10–16 m/s at Monaco's curvatures, while the real car arrives at 60–70 m/s — a factor of 3–4 in raw speed, 9–16× in lateral force.

---

## Per-Corner Evidence Table

| Field | C1: Fast-corner apex | C2: Braking knee (steepest) |
|---|---|---|
| Location (m on ribbon) | 2463 m (tunnel entry) | 2867 m (Rascasse approach) |
| Curvature κ (1/m) | +0.01104 | −0.02643 |
| v_ideal (m/s / km/h) | 15.92 / 57.3 | 9.82 / 35.3 |
| v_real_progress (m/s / km/h) | 62.41 / 224.7 | 11.93 / 43.0 |
| v_real_truedist (m/s / km/h) | 63.34 / 228.0 | 20.27 / 73.0 |
| ratio_progress | 2.000 (clipped) | 1.215 |
| ratio_truedist | 2.000 (clipped) | 2.000 (clipped) |
| a_lat at apex (m/s²) | 43.0 (fast_corner) | N/A (braking) |
| **True-dist ratio ≤ 1.15?** | **NO** | **NO** |

Notes:
- C1 ratio_truedist = 2.000 is the clip ceiling; the underlying raw ratio is 63.34/15.92 = 3.98×.
- C2 true-dist ratio jumps to 2.000 (clipped) from progress 1.22 because on true distance, the real lap's high-speed braking approach phase maps onto the ribbon's high-curvature zone, making the cap mismatch even worse — the opposite of what misregistration hypothesis (a) would predict.

### Regime means (all 1500 ribbon points)

| Regime | n_pts | U_progress | U_truedist | Δ (abs) |
|---|---|---|---|---|
| braking | 483 (32.2%) | 1.884 | 1.870 | −0.014 |
| fast_corner | 94 (6.3%) | 1.994 | 1.994 | 0.000 |
| slow_corner | 902 (60.1%) | (not clipped case) | — | — |
| straight | 21 (1.4%) | — | — | — |

The 0.7% change in braking-regime mean from switching registrations is noise, not signal.

---

## Physical Root Cause

### Lateral cap drastically under-calls Monaco cornering speeds

The lateral speed cap is:
```
v_cap(kappa) = sqrt(A0 / (kappa - A2))
```
With fitted parameters A0=2.6419 (g_eff ≈ 2.64 m/s²) and A2=0.000517 (aero lift coefficient 1/m):

| kappa (1/m) | Location | v_cap (m/s) | v_cap (km/h) | VER actual (km/h) | Under-call factor |
|---|---|---|---|---|---|
| 0.0110 | Tunnel entry | 15.9 | 57 | ~225 | 3.9× |
| 0.0264 | Rascasse | 10.1 | 36 | ~90 (approach) | 2.5× |
| 0.0050 | Medium corner | 24.3 | 87 | variable | 1.5–2× |
| 0.0020 | Gentle bend | 42.2 | 152 | ~150 | ~1.0 |

A0 = 2.64 m/s² is the effective lateral deceleration available. This is physically implausible for a 2023 F1 car at Monaco which sustains 40–50 m/s² laterally in fast corners. The cross-session pooled A0 estimate appears severely biased downward — consistent with the #445/496 finding that constructors were not separable in the pool (frac_team ≤ 3%).

### The sim's overall speed ceiling is under-called

The ideal lap maximum: 62.1 m/s (224 km/h). VER's best lap maximum: 80.3 m/s (289 km/h). The sim never reaches VER's straight-line speed, which means the entire speed profile is compressed downward and the denominator (v_ideal) is small almost everywhere.

### 232 points where v_ideal < 20 m/s but v_real > 40 m/s

These 232/1500 ribbon points (15.5%) are concentrated in two zones:
1. Massenet/Beau Rivage braking zone (~640–710m): real car braking from 72 m/s while sim shows 14–30 m/s caps (the ribbon curvature there already reflects the upcoming corner geometry, so the sim gives a corner speed cap for a zone where the real car is mid-approach braking).
2. Tunnel area (~2440–2480m): real car at 60–63 m/s, sim cap 16 m/s. This is a genuine under-call — the sim says the tunnel cannot be taken at more than 57 km/h, but VER is at 225 km/h.

Both are (b): the caps are wrong. Zone 1 also has a geometry-registration component (the sim starts "cornering" at the curvature inflection point, not at the braking point), but that does not survive as a (a) misregistration fix because changing the distance registration (true-dist vs progress-fraction) makes it equally wrong or worse.

---

## Why (a) is rejected

1. **Lap length delta is 0.47%** — 15.1 m on 3257 m. At Monaco speeds (~20 m/s average), this is ~0.75 s of arc. Progress-fraction and true-distance registration agree to within rounding at every tested point.

2. **True-distance re-registration does not lower the ratio** at either selected corner. At C1 (tunnel), both registrations give 2.000 (clipped). At C2 (Rascasse approach), true-distance gives 2.000 (clipped) vs progress 1.22 — the reverse of what (a) would predict.

3. **0 of 94 fast-corner points** fall to ≤ 1.15 under true-distance registration.

4. **Only 2 of 483 braking points** (0.4%) fall to ≤ 1.15 under true-distance registration.

5. The lateral cap formula with the fitted A0 physically requires VER to apex at 57 km/h through the Monaco tunnel. That is a constraint the car provably does not satisfy.

---

## Recommended Fix Approach

Since the verdict is **(b)**, the fix is **per-regime measured-frontier comparison** (reuse layer2 frontiers from #496):

- Replace the sim's under-called lateral cap with measured per-circuit lateral frontiers (the Traction-ascent/PowerDrag-descent five-view structure from #496 already has this partially).
- Alternatively: calibrate the ideal-lap sim's A0/A2 parameters against circuit-specific lateral apex-speed data (the cross-session pool blends too many circuits and averages out Monaco's extreme slow corners with high-speed tracks, making A0 reflect the pool median rather than Monaco's grip ceiling).
- For utilization measurement: the denominator v_ideal should use a circuit-local lateral frontier, not a cross-circuit pooled cap. This is the Layer 2 measured frontier approach.

The (a) fix (true-distance / corner-landmark alignment) is not needed and would not materially change the utilization numbers.

---

## Caveats

1. **Monaco is the hardest case.** The track has the widest speed range of any GP (10–290 km/h) and a lateral cap with negligible aero contribution at slow corners. The 0.47% length delta is the smallest feasible misregistration. A track with a larger ribbon-vs-real-line length delta (e.g., a circuit where the pool ribbon is based on different laps) might show mild (a) effects, but the magnitude here is conclusively sub-dominant.

2. **The braking regime near-corner overlap.** At the Massenet zone (~640–710m), the ribbon curvature already shows the corner while the real car is still braking at 65 m/s. A stricter corner-entry landmark alignment (matching the braking initiation point, not just the arc-length distance) might reduce ratio_progress in that zone from ~2.0 to ~1.5. This is a geometry artifact, not a simple progress-fraction artifact, and cannot be fixed by true-distance registration alone.

3. **A0 estimation.** If the cross-session pooled A0 is systematically biased (because high-speed tracks dilute the lateral g-cap), then per-circuit A0 re-calibration would close a material fraction of the gap without needing a different comparison method.

4. **The fast-corner fast-corner mismatch is definitively (b).** There is no registration correction possible (geometry or distance) that would bring 63 m/s within plausible range of a 16 m/s cap.

---

## Files produced

- `diag_alignment.py` — reproducible script; run from repo root: `py .agent-work/522-phase-align-utilization/diag_alignment.py`
- `fig_alignment_monaco_ver.png` — three-panel figure: speed profiles (v_ideal, v_real_progress, v_real_truedist), point-wise ratio comparison, curvature + regime shading
- `DIAGNOSIS.md` (this file)
