# Apex-speed vs frontier-g: resolving the HAA paradox (#445 feature engineering)

**TL;DR.** The cornering grip *ceiling* (frontier-g `B`) is NOT pace-relevant
(cross-sectional Spearman to quali pace **−0.15**, Haas reads grippiest yet runs
P8). The pace-relevant cornering observable is **apex speed normalized to corner
radius**: cross-sectional Spearman **−0.89** (90% CI [−0.93, −0.56]), Haas drops
from grip-rank #1 to apex-rank #6 (its true pace rank is #8). Apex-speed is the
grip feature to productionize. All on clean calibrated kinematics (χ²≈1).

Method note: everything below is on the **clean** calibrated nodes/trajectories
(`calibrated_aniso_nodes.npz`, per-session χ²≈1 smoother), NOT the contaminated
caches. Quali only (fresh-tyre limit). Pace reference = `quali_pace_2023.json`
(per-round per-team gap-to-field-median; negative = faster).

---

## Part 1 — The HAA tell: why high cornering grip but slow

### The paradox, sharpened
Season frontier-g feature (lateral-apex downforce `B`, season-MEAN of per-weekend
`B·vref²`) vs quali pace, team level:

| team | gripG | quali_gap | | team | gripG | quali_gap |
|---|---|---|---|---|---|---|
| **HAA** | **3.07** | **+0.95 (slow)** | | AMR | 2.55 | −0.15 |
| MERC | 2.81 | −0.44 | | MCL | 2.54 | −0.25 |
| ALP | 2.76 | +0.69 | | WIL | 2.47 | +0.82 |
| RBR | 2.69 | −0.86 (fast) | | ALF | 2.45 | +1.29 |
| | | | | **FER** | **2.20** | **−0.63 (fast)** |

Spearman(gripG, quali) = **−0.152**, Pearson = +0.056. HAA reads **#1 grip**,
runs **P8**; FER reads **#10 grip (lowest)**, runs **P2**. The frontier-g number
is nearly orthogonal to pace.

### Mechanism — three findings, in order of importance

**(1) The #1 grip ranking is a fat-tailed-aggregation artifact.** The season
feature is the MEAN of a per-weekend frontier slope `B`. The per-weekend `B·vref²`
is heavy-tailed for every team, but **HAA's tail is by far the worst**:

| | median per-wknd `B·vref²` | max | max/median |
|---|---|---|---|
| **HAA** | 2.13 | **18.52** | **8.7×** |
| RBR | 2.33 | 9.77 | 4.2× |
| (others) | ~1.8–2.5 | ~9 | ~4× |

The smoking gun is **Miami / HUL**: `B·vref² = 18.5` while its median apex speed is
only **97 km/h** (the SLOWEST of the four RBR+HAA cars; VER was 127). A handful of
near-ceiling apex nodes (`g_lat` up to 4.49 g, vs GSAT 5.2) on a steep `v²`-slope
fit force an enormous `B`; the MEAN then propagates it. **Switching MEAN→MEDIAN
aggregation drops HAA from grip-rank #1 to #5 and lifts the pace correlation from
−0.15 to −0.41.** So roughly half the paradox is the non-robust aggregation of a
heavy-tailed slope estimator — not a real grip reading.

**(2) Even pooled cleanly, HAA's *achieved* grip is not higher than RBR.** Pooling
all near-apex lateral nodes across the season and taking the 90th-pct `g_lat` per
speed bin, RBR ≥ HAA at **every** speed bin (e.g. 122 km/h: RBR 2.80 vs HAA 2.65 g).
The pooled-season frontier fit even gives HAA the **lowest** `v²`-slope
(`B=0.88e-3` vs RBR `1.64e-3`). HAA's apex-speed distribution ≈ RBR's
(p50 121 vs 123 km/h) — HAA is neither grippier nor much slower in the *raw cloud*;
the gap is created by the fitter + aggregator, plus residual ceiling≠pace (next).

**(3) Where HAA actually loses time: the medium-speed corners.** Matched-radius
head-to-head (season-pooled apex speed at the same corner radius), RBR − HAA:

| radius | apex Δ | entry Δ | exit Δ | corner-time Δ |
|---|---|---|---|---|
| 20–40 m (tight) | −1.3 | +4.6 | −4.7 | +0.8% |
| **40–70 m** | **+4.3** | **+8.0** | **+4.0** | **+2.0%** |
| **70–120 m** | **+6.0** | **+5.0** | **+4.4** | **+1.1%** |
| 120–200 m | +1.6 | +0.2 | +2.6 | +1.0% |
| 200–400 m (fast) | −4.4 | −3.9 | −0.1 | −1.1% |

(km/h faster at apex/entry/exit; % corner-time faster. + = RBR better.)

RBR beats HAA across **all three phases** (brakes later, carries more apex speed,
gets on power earlier) in the **40–120 m mid-speed corners that dominate a lap**.
At the extremes they're near-parity, and HAA is even marginally faster in the very
fast (200–400 m) corners — **exactly the high-g tail the frontier-g is built from.**

### Verdict (HAA)
The frontier-g measures the **grip ceiling**, dominated by the high-g tails (very
fast corners + tight-corner peak spikes) where HAA's downforce is competitive. It
is blind to the **mid-speed corner deficit** — entry/apex/exit, ~1–2% of corner
time each — where HAA loses the lap. Compounded by a non-robust MEAN over a
fat-tailed per-weekend slope, this inflates HAA to #1. Grip-ceiling ≠ pace; the
quantity that translates grip into lap time is **apex speed through the corners
that matter**.

---

## Part 2 — The apex-speed feature

### Extraction (clean kinematics)
`apex_extract.py` → `apex_corners.npz` (63,702 corner-records, 438 car-weekends,
all 22 rounds, 20 cars). Per session: same per-session **calibrated** smoother as
`calibrated_extract.py` (`session_offset` + `fit_stint_hp`, χ²≈1). On every flying
quali lap (≤1.07× best): segment corners as prominent `a_lat(s)` peaks (the
Suzuka-validated `corner_segment` detector), and for each corner record:
`v_apex` (min speed in the corner window), `R_apex` (adaptive circle-fit radius),
`alat_apex`, entry/exit speeds `v_in/v_out`, corner time `corner_dt`, arc
`corner_ds`. Corners pooled across all flying laps for stability.

### Feature definition (geometry-normalized)
Apex speed depends on the car AND the corner radius (`v_apex ≈ sqrt(a_lat·R)`). To
get **car capability not track**, within each weekend regress
`log v_apex = β·log R + α_car`, with a **shared slope β** (the field shares that
weekend's corners) and a **per-car offset α_car**, then center offsets to zero mean
across cars (removes the weekend grip *level* → car-relative). Season feature =
**median over rounds** of the per-car offset.

Headline variant **A′ (on-limit)**: take the **90th percentile** of the per-car
radius-residual within each weekend (the car on its best lap), not the mean. This
is the strongest. (Mean-offset variant A is weaker but same sign.) A corner-time
variant B (`corner_dt/corner_ds`) corroborates with opposite sign.

### Pace-relevance — apex-speed vs frontier-g

| feature | Spearman→quali | Pearson | HAA rank |
|---|---|---|---|
| frontier-g `B` (mean agg) | **−0.152** | +0.056 | **#1 (grippiest)** ✗ |
| frontier-g `B` (median agg) | −0.406 | — | #5 |
| apex-speed @ radius (mean) | −0.636 | −0.733 | #6 |
| **apex-speed @ radius (90th, on-limit)** | **−0.891** | **−0.896** | **#6** ✓ |
| corner inverse-speed (B) | +0.685 | +0.748 | #8 |

The on-limit apex-speed feature is a **near-perfect cross-sectional pace match**
(−0.89 vs −0.15 for the grip ceiling). The apex-rank tracks pace-rank almost
1:1 in the top 5 (RBR/FER/MERC/MCL/AMR aligned). See `apex_vs_pace.png`:
frontier-g is a scattershot (HAA bottom-right, FER top-left); apex-speed is a
clean diagonal.

### Does it resolve the HAA paradox? YES.
HAA: grip-rank **#1** → apex-rank **#6** (true pace rank #8). It moves HAA off the
"grippiest" perch to mid-pack, the right direction. FER (fast, read lowest grip)
moves to apex-rank #2. The gross failures are fixed.

### Robustness (honest)
- **Leave-one-team-out: −0.85 to −0.90** — not driven by any single team.
- **Bootstrap 90% CI [−0.93, −0.56]** — robustly negative, cleanly separated from
  the frontier's −0.15.
- **Fitted β ≈ 0.32** (not the ideal 0.5). Apex speed scales **sub-√R**: big-radius
  corners aren't taken proportionally faster (friction-circle/power ceiling; the
  corner window mixes entry/exit states, not a pure apex point). Doesn't break the
  feature (β only sets the normalization), but the corner segmentation is a *mix of
  corner states*, not an idealized apex — a known approximation.
- **Split-half (odd vs even rounds): per-team feature value Spearman only +0.29**,
  yet each half *independently* tracks quali pace (−0.64 / −0.62). I.e. the
  **season aggregate is pace-relevant and stable; per-round values are noisy**
  (consistent with the established between/within<1 for the grip channel — needs
  the full season, few-round estimates are unreliable).

---

## PRODUCTION NOTES

**Is apex-speed the grip feature to productionize? YES — replace the frontier-g
ceiling as the *cornering-pace* channel.** It is the first cornering observable in
this epic that is cross-sectionally pace-relevant (−0.89) AND resolves the HAA/FER
gross failures the grip-frontier could not. The frontier-g `B` still has a role as
a **downforce-capability** descriptor (it genuinely orders RBR top after the
contamination fix), but it is a *ceiling*, not a *pace* feature — keep them as
separate channels.

**How to compute it cleanly (recommended recipe):**
1. **Clean kinematics, always.** Per-session calibrated smoother (`session_offset`
   + `fit_stint_hp`, χ²≈1). Same pipeline as `calibrated_extract.py`. Do NOT use
   the hardcoded `StintSmoother(2,100,0.3,0.06)` (χ²=33).
2. **Corner segmentation** = prominent `a_lat(s)` peaks (`corner_segment` params:
   height 5 m/s², prominence 4, distance 4 nodes), then the local **min-speed**
   node as the apex. Pool across all flying laps (≤1.07× best); single-lap is noisy.
3. **Geometry normalization** = within-weekend regression
   `log v_apex = β·log R_apex + α_car`, shared β, per-car offset α; center α across
   cars. **Use the 90th-pct radius-residual** per car (on-limit), not the mean.
4. **Season aggregate** = median of per-weekend offsets per car; mean over drivers
   for the team feature. The season aggregate is the stable, pace-relevant quantity
   — do NOT trust few-round values (split-half +0.29).
5. **Aggregate robustly.** Whatever the channel, prefer MEDIAN over MEAN across
   weekends — the per-weekend frontier/apex estimates are heavy-tailed; the MEAN
   alone moved HAA's grip from rank #5 (median) to #1 (mean).

**Open items / caveats before a PR:**
- β≈0.32 (sub-√R): the corner window captures a mix of states. A cleaner apex
  isolation (e.g. min-speed ± fixed arc, or fitting only the converging-then-
  diverging speed valley) might sharpen the feature and push β toward 0.5. Worth a
  follow-up, but the current feature is already at −0.89.
- An alternative geometry control that sidesteps the noisy circle-fit radius:
  **matched-corner-by-track-location** apex-speed (same physical corner across
  cars, as in `corner_compare_v2`). Cleaner per-track, but doesn't pool across
  tracks without a radius model — use it as a within-track cross-check.
- Apex-speed is a CORNERING-pace feature; it says nothing about straight-line
  power/drag. Fuse with the drag channel for a full pace descriptor.
- Driver confound: apex speed includes driver commitment. The within-weekend,
  team-mean, season-median aggregation suppresses it, but it's not removed
  (teammate-gap audit not run here — recommend before production).

## Files (all `.agent-work/445/envelope/`, additive, `apex_*` namespaced)
- `apex_extract.py` — clean per-corner extraction → **`apex_corners.npz`** (cache).
- `apex_feature.py` — geometry-normalized apex-speed/corner-time season features +
  pace-relevance comparison vs frontier-g → `apex_feature.json`.
- `apex_baseline_frontier.py` — reproduces the frontier-g `B` baseline →
  `apex_baseline_frontier.json`.
- `apex_haa_tell.py` — where HAA's grip lives by speed (achieved frontier + fit).
- `apex_haa_perweekend.py` — per-weekend `B` dissection (the fat-tail tell).
- `apex_frontier_robust.py` — MEAN vs MEDIAN aggregation (the artifact).
- `apex_haa_decompose.py` — entry/apex/exit corner-phase decomposition HAA vs RBR.
- `apex_diagnose.py` — HAA resolution table + matched-radius head-to-head +
  `apex_vs_pace.png`.
- `apex_robustness.py` — β, leave-one-team-out, bootstrap CI, split-half stability.
