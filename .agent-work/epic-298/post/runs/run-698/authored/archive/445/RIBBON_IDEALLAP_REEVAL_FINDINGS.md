# Ribbon + Ideal-Lap Re-evaluation on Clean Kinematics

**Epic #445 — run 2026-06-15**
**Code: `.agent-work/445/envelope/ribbon_reeval.py`**
**Cached ribbons: `ribbon_clean_{monza,hungary,suzuka}.npz`**

---

## Context

Prior work (`cross_circuit.py`) built the track ribbon and ran the quasi-static ideal-lap
simulation using a contaminated smoother (`StintSmoother(2, 100, 0.3, 0.06)`, χ²_pos ≈ 33 —
over-trusting position 6×). The position noise inflated high-speed `a_lat = v²/R` estimates
(noisy radius from the circle fit), which in turn inflated the per-car downforce coefficient B.
That run found the constructor spread was track-invariant (~750 ms at all three circuits) and
that ordering scrambled nonsensically (RBR slowest at Hungary, WIL fastest at Suzuka).

This re-evaluation uses per-session calibrated HPs from `calibrated_hp.json`
(χ²_pos ≈ 1, χ²_spd ≈ 1) and apex nodes from `calibrated_aniso_nodes.npz` (the full-season
clean node extraction). Three tracks: Monza (low-DF), Hungary (high-DF), Suzuka (balanced).

---

## 1. Track Ribbon (Clean vs Contaminated)

Re-pooled the mean-lap XY path over all Q+R laps for VER+HAM at each track using the
calibrated smoother HPs. Kappa(s) computed from mean heading slope.

| Track   | N laps | Old ribbon Rmin | Clean ribbon Rmin | Kappa corr (old vs clean) |
|---------|--------|-----------------|-------------------|--------------------------|
| Monza   | 124    | 44 m            | **26 m**          | 0.869                    |
| Hungary | 159    | 26 m            | 27 m              | 0.982                    |
| Suzuka  | 108    | 16 m            | 16 m              | 0.937                    |

**Kappa RMS (smoothed profile):**

| Track   | Old    | Clean  |
|---------|--------|--------|
| Monza   | 0.00421 | 0.00513 |
| Hungary | 0.00943 | 0.00948 |
| Suzuka  | 0.00860 | 0.00864 |

### Ribbon verdict

**The ribbon is geometrically sound either way.** Pooling ~100–159 laps averages individual-lap
position noise by √N, so the contaminated smoother's larger per-lap XY error still produced a
coherent mean line. The clean and contaminated ribbons are highly correlated (0.87–0.98) —
they agree on which corners are tight and which are wide.

**One material difference:** Monza's tightest corner radius is 26 m (clean) vs 44 m (old).
The old smoother over-smoothed the positions (sig_pos=0.3 m declared when positions are ~1.8 m
noisy → over-trusted → artificially smooth per-lap path → under-estimates peak curvature in
pooling). 26 m is physically more credible for Monza's tight chicane exits/Lesmo complex.

**The kappa RMS is slightly HIGHER for the clean ribbon** — not lower as one might expect.
This is not noise; it reflects that the contaminated smoother over-constrained individual lap
paths (artificially smooth XY), producing a mean line with artificially low curvature. The
clean ribbon lets position uncertainty breathe → mean line follows the true road geometry
more faithfully → picks up real curvature in tight sections the old smoother muted.

**Conclusion: the clean ribbon is a marginally better track model (truer Rmin, higher structural
correlation with actual geometry). But the qualitative conclusion from the old run — that the
ribbon is a sound foundation for the lap sim — holds. The ribbon is NOT the source of the
prior fit-noise problem.**

---

## 2. Ideal Lap — Clean Constructor Numbers

Grip frontier: `G(v) = min(A + B·v², Gsat)` fitted to calibrated apex nodes (alat in g's,
pure-lateral cornering nodes from quali sessions). Power/drag from CAN-bus car_data (unchanged
by smoother calibration).

### 2a. Monza

All four constructors have B = 0.00050 (the curve_fit lower bound). Flat g(v) profile:
g90 ≈ 1.88–2.18g across 72–143 km/h — no measurable rising trend with speed. The A/B split
is **unidentifiable from quali-only Monza data.** Monza has very few slow-speed corners;
all corners are in the 88–148 km/h regime where A and B v² are collinear (cannot separate
mechanical grip from aerodynamic load on a single-speed-regime dataset).

| Team | A    | B      | Ideal (s) | vs pole (+80.29s) | Utilization |
|------|------|--------|-----------|-------------------|-------------|
| WIL  | 1.59 | 0.0005 | 82.34     | +2.05s            | **1.026 (>1 = unphysical)** |
| FER  | 1.53 | 0.0005 | 82.96     | +2.67s            | **1.033** |
| RBR  | 1.56 | 0.0005 | 83.13     | +2.84s            | **1.035** |
| MERC | 1.50 | 0.0005 | 83.96     | +3.67s            | **1.046** |

Utilization > 1 (ideal slower than actual pole) = **unphysical**. The model says the
physics-limited pace is SLOWER than what drivers actually achieved. Root cause: with B at
the lower bound, grip is underestimated at the high speeds where Monza corners happen,
so the sim runs too slow. This is the honest failure of a model with insufficient data
for its own parameterization.

**Old contaminated Monza:** spread 749 ms, field mean 70.98 s, utilization 88%. The old
results looked physically coherent because chi2=33 noise inflated B (apparent high-speed
grip from noisy a_lat), artificially boosting corner speeds in the sim. Clean kinematics
reveals the inflation was wrong.

### 2b. Hungary

Best-behaved track. Enough nodes (456–1054 per constructor) for B to be identifiable.

| Team | A    | B       | Ideal (s) | d_mean (ms) | vs OLD d_mean |
|------|------|---------|-----------|-------------|---------------|
| MERC | 1.52 | 0.00106 | 73.59     | −1316       | was −252      |
| RBR  | 1.60 | 0.00095 | 74.79     | −113        | was +417      |
| WIL  | 1.54 | 0.00096 | 74.89     | −17         | was +138      |
| FER  | 1.88 | 0.00066 | 76.35     | +1446       | was −298      |

Clean vs OLD spread: **2763 ms vs 720 ms** (much larger on clean data).
Clean vs OLD ordering: **completely inverted.** OLD put RBR slowest (+417ms) and FER fastest
(−298ms). CLEAN puts MERC fastest (−1316ms) and FER slowest (+1446ms).

Utilization check: all ideals < pole (76.61s), so utilization 96–100% — tight but physical.
MERC ideal at 73.59s is 3s faster than pole, which means the sim says HAM/RUS only extracted
96% of their theoretical max. **This is overly generous** (actual physical utilization at
Hungary was ~90% in old runs); the clean grip frontier for MERC is slightly too high.

**FER anomaly:** the calibrated_aniso_nodes show FER's g90 at 136–148 km/h = 2.80g
(slightly DROPPING from 2.87g at 124–136 km/h), while RBR's continues rising to 3.05g.
This forces the fit to interpret FER as high mechanical grip (A=1.88) but limited aero
(B=0.00066). This is at the boundary of being physically real (Ferrari's 2023 car was
genuinely stronger in mechanical grip regime than aerodynamic) vs a thin-data artifact —
inconclusive at single-weekend resolution.

### 2c. Suzuka

**Failed gracefully.** Japanese GP calibrated nodes: VER = no data; PER = 35 nodes, WIL ALB = 44
nodes. RBR and WIL fall below the 30-node minimum, triggering the live fallback. The live
fallback uses ell=1.25 (Suzuka calibrated HP), which with the 5/2 smoother gives rough
per-lap position paths → noisy curvature per lap → apex kappa inflated → B hits upper bound
(0.00500) for RBR and WIL. MERC and FER calibrated nodes (99 and 84 nodes) are used, but
show flat g(v) and B hits lower bound.

The slim Japanese calibrated node set is a limitation of `calibrated_extract.py` running
on quali only: Suzuka 2023 had very few flying laps per driver due to yellow flags
(HAM stopped early, VER had no usable clean stint in calibration drivers). This is NOT a
clean-kinematics failure; it is a data-availability failure at this particular round.

---

## 3. Discrimination Check (Clean): Does Constructor Ordering Vary by Track?

| Team | Monza (ms vs mean) | Hungary (ms vs mean) |
|------|--------------------|-----------------------|
| FER  | −140               | +1446                 |
| MERC | +862               | −1316                 |
| RBR  | +35                | −113                  |
| WIL  | −756               | +143                  |

(Suzuka excluded: too few valid constructors for comparison.)

**Compared to old contaminated results:**

| Team | Monza OLD | Hungary OLD |
|------|-----------|-------------|
| FER  | −190      | −298        |
| MERC | +430      | −252        |
| RBR  | +80       | +417        |
| WIL  | −320      | +138        |

The old run showed ~flat spread (750/715ms, track-invariant) and scrambled ordering
(RBR was slowest at Hungary). The clean run shows a LARGER spread at Hungary (2763ms) but
FER/MERC ordering is physically suspect (MERC fastest at Hungary is plausible — HAM took
pole at 2023 Hungary — but FER slowest at 3s behind MERC ideal is inconsistent with FER
P3 in quali, and Monza is unreliable due to B lower-bound collapse).

**Verdict: the clean run does NOT resolve the discrimination problem.** The ordering at
the one reliable track (Hungary) shows MERC fastest and FER slowest — partially consistent
with 2023 reality (MERC dominated Hungary, FER was struggling) but the magnitudes are
unstable (the FER anomaly at 136-148 km/h is a possible artifact).

---

## 4. Diagnosis: Why Noise Enters

The ideal-lap sim has three contamination sources, ranked:

**1. Grip frontier (A, B) — primary noise source.**
The biggest issue is not the ribbon or the sim; it's the grip parameterization:
- Monza: B unidentifiable from single-weekend qual-only data (flat g(v) in the available
  speed regime) → lower-bound collapse → underestimates corner speeds → unphysical sim.
- Suzuka: data too thin per constructor (VER absent, others 35–99 nodes) with a short-ell
  calibrated smoother making per-lap curvature noisy.
- Hungary: identifiable but FER shows a probable high-speed-dropoff artifact in its 
  per-car node cloud. Still the best data of the three tracks.

**2. Ribbon kappa — minimal contributor.**
The ribbon is pooled over 100+ laps; per-lap noise averages √N. The clean and contaminated
ribbons are 87–98% correlated. Neither the ribbon's structure nor its curvature statistics
are a material source of discriminating noise (the two ribbons give the same track model).

**3. Power/drag fit — negligible for ordering within a track.**
CAN-bus data (Throttle, Speed, DRS) is not affected by the smoother calibration. Power
and drag estimates are stable across the two runs. **Drag is still the one channel that
gives physically sensible cross-circuit ordering** (CdA_closed: Monza 1.11–1.21, Hungary
1.73–1.93, in the expected low→high direction as wing is added).

---

## 5. Clean vs Old — Summary Comparison

| Track   | Spread OLD (ms) | Spread CLEAN (ms) | Ordering stable? | Unphysical? |
|---------|-----------------|-------------------|------------------|-------------|
| Monza   | 750             | 1618              | No (B=bound)     | Yes (util>1)|
| Hungary | 720             | 2763              | No (FER flipped) | Borderline  |
| Suzuka  | 750             | N/A (data failure)| —                | —           |

Track-invariant spread (OLD signature of fit noise): ~750ms across all three.
CLEAN spread varies 1618–2763ms, but BOTH Monza and Hungary results are suspect
(Monza = B degenerate, Hungary = FER anomaly, Suzuka = data absent).

**The OLD fixed-fractional-spread (750ms everywhere = fit noise) diagnosis was CORRECT as a
diagnosis.** The contaminated smoother was inflating B via noisy high-speed a_lat, which
was then consistently ~wrong across all tracks. Clean kinematics removes that inflation but
exposes a different problem: the grip frontier parameterization cannot identify B robustly
from single-weekend qualification data at low-aero tracks (Monza), and the data coverage
is too thin at some tracks (Suzuka).

---

## PRODUCTION NOTES

**Do NOT use the ideal-lap time as a per-car feature** from single-weekend data with the
current pipeline. The sim result is dominated by the grip frontier parameterization, which
is noise-floor limited from single-weekend quals.

**The ribbon IS production-ready as a track model.** The clean ribbon gives a geometrically
correct kappa(s) profile for any lap simulation. Recommended: use clean calibrated smoother
HPs for ribbon construction. The ribbon itself is not a discriminating per-car feature.

**What DOES work from the clean kinematics (from prior work, reinforced here):**
- Per-season Bayesian downforce prior with calibrated obs-variance (season_prior_bayes.py):
  borrows strength across rounds, reduces teammate variance, handles thin-data rounds.
- Drag channel (CdA): physically sensible per-track and per-car (contamination did not
  strongly affect the CAN-bus-based power/drag fit).
- The calibrated smoother kappa profiles WILL help the corner-energy analysis (#445 phase 2).

**Why the clean ribbon gives higher kappa_rms than contaminated:** the contaminated smoother
(sig_pos=0.3m vs real ~1.8m) over-constrained XY → artificially smooth individual lap paths
→ muted pooled kappa → underestimated peak curvature at tight corners. This is a correctness
issue in the old ribbon that the clean version fixes, at the cost of slightly higher kappa
variance in the pooled mean. This is the right trade-off.

**Suzuka ell=1.25 is the short-ell trap** identified in SESSION_2026-06-15: a short ell gives
χ²≈1 but rough per-sample velocity/geometry, making per-lap curvature noisy. For the ribbon
(pooled mean), this is manageable. For per-lap apex detection (live fallback), it breaks B
identification. If rerunning Suzuka, use Matérn-7/2 smoother (SESSION result: 7/2 reaches
χ²≈1 at moderate ell=4.5–5.6 every session, avoiding the short-ell collapse).
