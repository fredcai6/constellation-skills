# Longitudinal (braking) acceleration — math re-evaluation (#445)

Re-evaluation of the braking channel (`aniso_long_fit.py`) on the CLEAN calibrated
caches (`calibrated_braking_nodes.npz`, `calibrated_aniso_nodes.npz`, χ²≈1 smoother).
Scope: is the longitudinal math correct, and does a valid per-car FEATURE emerge?

**Verdict up front.** The math has a real algebra defect AND the headline result is a
fitter artifact AND the underlying sensor truncation is fatal in the regime that
matters. The braking channel does **NOT** yield a valid independent per-car feature.
The previously-reported `corr(B_long, B_lat)=+0.48` "corroboration" is **spurious** —
it is produced entirely by a mis-applied `GSAT=5.2` clip, not by physics. Recommend
**retiring the braking channel as a car-aero observable** and keeping only the lateral
(cornering) frontier. Details, derivations, and numbers below.

All numbers reproducible from `.agent-work/445/envelope/longreeval_analysis.py`
(report dumped to `longreeval_report.json`).

---

## 1. Ellipse-projection algebra — is `along_eq = decel / sqrt(1 − (alat/G_lat)²)` right?

### The friction ellipse, derived properly

A car at the combined-grip limit sits on the friction ellipse in the acceleration plane:

```
    (a_lat / G_lat(v))²  +  (a_long / G_long(v))²  =  1            (E)
```

where `G_lat(v)`, `G_long(v)` are the **per-axis frontiers at that speed**. If a braking
sample `(a_lat, decel)` lies ON the ellipse, then solving (E) for the longitudinal arm:

```
    a_long = G_long(v) · sqrt(1 − (a_lat/G_lat(v))²)
```

The code instead computes `along_eq = decel / sqrt(1 − (alat/G_lat)²)`, i.e. it
**divides the measured decel by the lateral utilisation factor** to "lift" a combined
point back onto the pure-longitudinal axis. That recovers `G_long(v)` **only if the
sample is exactly on the ellipse**. It is *algebraically self-consistent* for a
frontier point. So the formula itself is the correct inversion — the problem is the
**inputs it is fed**, which violate every assumption the inversion needs:

### Where it breaks (measured on clean data)

| symptom | measured | why it's fatal |
|---|---|---|
| `a_lat/G_lat > 1` (outside the ellipse) | **12.0%** of braking points | √ of a negative → the denominator is imaginary; these are clipped, not inverted |
| ratio clipped at 0.97 (singular) | **14.3%** | projection blows up toward ∞; the cap is arbitrary |
| `G_lat` extrapolated above its fit support | **80%** of braking points sit above the lateral fit's p95 speed | the normaliser is an extrapolation, not a measurement (next box) |
| `G_lat` hit the `GSAT=5.2` ceiling | **28.8%** of braking points | the normaliser is a flat constant there, carrying zero car signal |
| `a_lat` physically impossible (>5.2 g) | **6.0%** | the `_alat` circle-fit on near-straight, high-speed segments is noise — it corrupts the denominator |

**The extrapolation problem (root cause).** `G_lat(v)=A+B·v²` is fit on the cornering
cloud, which lives at **70–153 km/h** (mid-corner, `alat`-gated >0.6 g). Braking happens
at **114–303 km/h** (median 196). So the ellipse normaliser is **extrapolated 1.3–2× beyond
its data**, and above ~250 km/h it is pinned to the constant `GSAT`. Example (Bahrain, VER):

```
  G_lat fit support:        70 – 153 km/h
  G_lat(150) = 3.05 g   (in support)
  G_lat(200) = 4.01 g   (extrapolated)
  G_lat(250) = 5.20 g   (clipped at GSAT)
  G_lat(300) = 5.20 g   (clipped — all car signal gone)
```

The real lateral frontier at 250–300 km/h is almost certainly **higher** than the
corner-speed `v²` extrapolation (downforce keeps growing), and certainly higher than
the flat `GSAT`. Using a too-low normaliser **inflates** `alat/G_lat` past 1 — which is
exactly the 12% of impossible points. The projection is being driven by an extrapolated
constant, not a measurement. **Verdict: the inversion formula is correct; its inputs are
not valid in the braking regime, and the result is dominated by extrapolation + clip
artifacts, not physics.**

---

## 2. The `+0.48` "corroboration" is a GSAT-clip artifact (the central finding)

The briefing's clean-data headline — `corr(B_long, B_lat) = +0.48`, "weakly corroborates
downforce" — **reproduces exactly (+0.483)** with the original recipe. But it is not a
physics signal. It is manufactured by the `GSAT=5.2` clip inside `fit_weekend` when that
fitter is (mis-)applied to the longitudinal cloud:

```
  corr(B_long, B_lat), 10 constructors, clean cache:
    GSAT = 5.2,  tau 0.92   (ORIGINAL recipe)   →  +0.483
    GSAT = 8.0,  tau 0.92   (clip relaxed)       →  −0.223     ← sign FLIPS
    GSAT = ∞,    tau 0.92   (no decel clip)       →  −0.030     ← vanishes
    GSAT = 5.2,  tau 0.80                          →  +0.351
    GSAT = ∞,    tau 0.80                          →  +0.035
```

**Mechanism.** The ellipse projection inflates raw decel (max ~3.5 g) into `along_eq`
with **p99 = 7.5 g** (median 2.5). About **9% of projected points exceed GSAT=5.2**.
`fit_weekend`'s frontier selection gate is `(g < GSAT − 0.2)`, so those 9% are
**discarded**. Which points are they? The **high-trail-brake** points (large `alat/G_lat`
→ large inflation) — and their inflation is computed *from the lateral fit B_lat itself*.
So discarding them via a clip tied to the lateral fit **couples B_long to B_lat through
the fitting machinery**, not through the car. Remove the clip (which has no business
being on a braking-decel axis — decel never reaches the 5.2 g *lateral tyre* ceiling) and
the correlation is zero. **The `+0.48` is circular. It is not independent evidence of
downforce.**

The drag cross-check confirms emptiness: `corr(B_long − B_lat residual, independent CdA)`
ranged **−0.06 to +0.08** across every fitter variant — i.e. the braking residual carries
**no** recoverable drag order. (A best-case joint regression `CdA ~ B_long + B_lat` gives
R²=0.27, and the only contributing term is the GSAT-clip-contaminated B_long.)

---

## 3. Correct downforce/drag decomposition — and why the naive subtraction is wrong

### The physics model

Braking and cornering at the grip limit, with linear downforce `F_z(v)=m·k_DF·v²` and
quadratic drag `F_d(v)=m·k_drag·v²` (so accelerations in g, dividing by m·g):

```
  a_long(v) = μ_x·g·(1 + k_DF·v²/g)/g + k_drag·v²/g
            = μ_x         +  (μ_x·k_DF + k_drag)·v²            ... braking
  a_lat(v)  = μ_y         +  (μ_y·k_DF)·v²                     ... cornering
```

so the fitted slopes are

```
  B_long  =  μ_x·k_DF  +  k_drag          (downforce-grip  +  drag)
  B_lat   =  μ_y·k_DF                       (downforce-grip only)
```

### Why `B_long − B_lat` is NOT a drag proxy

The naive proxy assumes `B_long − B_lat = k_drag`. That requires `μ_x = μ_y`. It is not:
longitudinal and lateral tyre friction coefficients differ (typically `μ_x/μ_y ≈ 0.85–1.1`,
and the load-sensitivity differs too). The correct isolation is

```
  k_drag  =  B_long  −  (μ_x/μ_y) · B_lat  =  B_long − κ·B_lat
```

I tested the de-confounding with `κ ∈ {1.0, 0.85, 0.70}` against the independent CdA
channel. **All give corr ≈ −0.05 ± 0.01** — the κ correction does not rescue it, because
the problem is upstream: `B_long` is dominated by projection/clip artifacts and a
truncated v² slope (§4), so there is no clean `μ_x·k_DF` term left to subtract `κ·B_lat`
from. **Even with the correct algebra, the drag channel cannot be recovered from braking.**
The independent `drag_fingerprint10` CdA channel remains the only valid drag observable.

---

## 4. Sensor truncation — quantified, and it is fatal in the downforce regime

The 4.2 Hz speed channel under-samples the peak deceleration; `dv/dt` over a finite window
averages the peak **down**, and the suppression **worsens with speed** (faster → more
violent → coarser relative sampling of the peak). This is not a hard cap — it is a
**speed-dependent upper-tail censoring**. Measured frontier (per-band decel percentiles):

```
  speed band     p90    p95    p99      (g)
   80–100 km/h   1.64   1.76   2.01
  140–160        2.47   2.64   3.00
  200–220        3.20   3.41   3.69
  220–240        3.27   3.47   3.81   ← frontier PEAKS here
  260–280        3.11   3.31   3.67
  300–320        2.63   2.83   3.18   ← frontier FALLS at high speed
```

**The braking frontier turns over and DECREASES above ~230 km/h.** Physically impossible
— more downforce at high speed must give *more* braking grip, so the true frontier is
monotonically rising. The observed turnover is pure truncation. This is fatal because the
**downforce v² signal lives precisely in the high-speed braking zone that is most
censored.** No quantile choice fixes a frontier bending the wrong way.

**Bias quantified.** Fitting `a_brake = A + B·v²` on near-straight braking, all speeds vs
low-speed-only (<200 km/h, less censored):

```
  B_long·vref²  (all speeds, censored)     =  0.51 g
  B_long·vref²  (v < 200 km/h only)        =  1.76 g     ← 3.4× larger
```

Truncation **suppresses the apparent v² (downforce) slope by ~70%**. The censoring is not
a constant offset that cancels in a field-relative subtraction — it is speed-dependent and
interacts with each car's speed distribution, so it injects per-car bias.

A censored-regression (Tobit) fix would in principle model decel as a lower bound above the
truncation onset. It is **not worth building here**: (a) the onset is speed-dependent and
gradual, not a clean threshold; (b) below the onset (<~180 km/h) downforce is a small part
of grip, so the un-censored data is mechanically-dominated and weak in car signal; (c) the
near-straight braking data that would anchor a clean longitudinal fit barely exists —
**median 3 points/car at `alat<0.6 g`** (pure straight-line braking ≈ doesn't exist, which
is why the ellipse projection was introduced in the first place). The fix has nothing solid
to stand on.

---

## 5. Traction (positive `a_long`) — correctly excluded

Confirmed power/traction-confounded, not a clean aero-grip frontier:

```
  positive-along p90 (corner exit), 60→160 km/h:  0.80 → 1.46 g  (rising, traction-limited
    low-speed launch transitioning into power deployment)
```

At low speed it is **wheelspin/traction-limited** (μ·load), at higher speed it is
**power-limited** (`a ≈ P/(m·v)`, falls with v). 2023 PUs are a near-frozen spec quantity
with team PU differences that confound any aero read. Positive-along mixes three things
(traction grip, power, PU) and isolates none. **Exclusion is correct.**

---

## 6. Net verdict on the longitudinal FEATURE

**No valid independent per-car braking feature emerges.** Summary of the three
independent failure modes, each sufficient on its own:

1. **Algebra inputs invalid.** The ellipse normaliser `G_lat` is extrapolated 1.3–2×
   beyond its corner-speed support and pinned to `GSAT` for ~30% of braking points; 12% of
   points fall outside the ellipse (impossible). The projection is artifact-driven.
2. **Headline result is circular.** The `+0.48` corr(B_long, B_lat) is manufactured by a
   mis-applied GSAT clip; it flips sign or vanishes under any reasonable fitter change.
   Drag cross-check ≈ 0 throughout. No independent physics signal.
3. **Sensor truncation is fatal where it matters.** The braking frontier *decreases* above
   230 km/h (impossible); the downforce v² slope is suppressed ~70% by speed-dependent
   censoring. The high-speed downforce regime is unrecoverable at 4.2 Hz.

Teammate test on the cleanest variant (near-straight pure-decel B_long): teammate gap
≈ between-team spread (ratio ~1.0) → **noise-dominated**, not a car property.

**Decisive recommendation: retire braking as a per-car aero observable.** The lateral
(cornering) apex frontier remains the single valid grip observable; the independent
`drag_fingerprint10` CdA channel remains the single valid drag observable. Braking adds
nothing the other two don't already carry more cleanly, and what it appears to add is an
artifact.

---

## PRODUCTION NOTES

**What becomes a real feature/module: nothing new from braking.** The actionable
production outcome is a *removal* plus two guard-rails.

1. **Do not promote `aniso_long_fit.py` / `braking_collect.py` to a feature module.**
   Mark them experimental/negative-result. The per-car `B_long` (and any `B_long − B_lat`
   drag proxy) must **not** feed the descriptor/fingerprint. If anything downstream already
   references a braking-downforce or braking-drag term, drop it — it is GSAT-clip noise.

2. **Lateral-only grip + independent CdA drag are the production channels** (unchanged).
   The validated per-car aero features remain: (a) lateral-apex downforce slope `B_lat`
   from the cornering frontier (`aniso_fit.clouds_lat` → `fit_weekend`), season-filtered
   per `season_prior_bayes.py`; (b) `CdA_c` per-team-per-round from
   `drag_fingerprint10_fits.json`. These two span the downforce and drag axes without
   braking.

3. **Guard-rail for the lateral fitter: never let `GSAT` clip leak onto a non-lateral
   axis.** The artifact here was `fit_weekend` (a *lateral* frontier fitter with a 5.2 g
   *tyre* ceiling) reused verbatim on a *longitudinal* cloud whose projected values exceed
   5.2 g for legitimate reasons. Any future reuse of `fit_weekend` on a different
   acceleration axis must pass an axis-appropriate ceiling (or none). Encode this as a
   required explicit `gsat=` argument rather than the module constant, so the clip can
   never be silently inherited. This is the single most important code lesson.

4. **If the braking regime is ever revisited, the prerequisite is higher-rate telemetry.**
   The blocker is the 4.2 Hz Nyquist floor making the high-speed braking frontier turn
   over. Nothing in post-processing recovers a censored frontier that bends the wrong way.
   Revisit only with native ~10 Hz+ car-data (FastF1 `car_data` brake/throttle channels are
   distinct from the GPS-derived speed used here and may sample finer) — and even then,
   re-prove a *monotonic-in-v* braking frontier before trusting any v² slope. Until that
   precondition is met, braking stays out of the feature set.

5. **Caches.** No heavy re-extraction was needed (clean caches sufficed). Analysis script
   `longreeval_analysis.py` and machine-readable numbers `longreeval_report.json` are the
   durable artifacts; both additive and namespaced.
