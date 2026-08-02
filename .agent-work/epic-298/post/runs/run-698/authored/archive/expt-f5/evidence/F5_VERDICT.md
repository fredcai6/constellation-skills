# F5 — Grip envelope + utilization (epic #445 Phase-2 ladder)

Question: can we measure the friction-ellipse (available grip envelope) from honest
accelerations, and separate available grip (car/compound/conditions) from utilization
(driver skill)?  **Answer: YES — grip resolves STRONGLY (S/C 8–15); the car-grip envelope
is a tight, shared property; driver utilization separates from it, and the separation is
clearest in the race.**  One binding caveat: the envelope's *absolute scale* is set by the
smoother length-scale `ell`, which must be PINNED to a physical value (see below).

## Method (dogfooded the production estimator)
`from src.preprocessing.trajectory import load_session_offline, driver_streams, stint_span,
fit_stint_hp, StintSmoother`.  Per driver: fit StintSmoother **per flying lap** (laps within
10% of the driver's best), pull honest 2D accel + 2×2 posterior covariance
(`acc_at` + `_state_at`, indices 2/5), rotate into the velocity frame (a_long, a_lat) with
the covariance propagated through the same rotation.  Pool corner/brake/traction samples
across all flying laps.  Fit the envelope per channel as `extent(v)=e0+e2·v²` (downforce
growth) via per-speed-bin 95th-percentile boundary; covariance by lap-block bootstrap.
Utilization r = elliptical radius toward the fitted boundary.  Scripts:
`scripts/experiments/f5_run.py`, `f5_plot.py`, `f5_verdict.py`.

## THE ell PROBLEM (binding cross-cutting caveat from F1) — and the fix
`fit_stint_hp` optimises `ell` against held-out **pos/speed** chi², which is **blind to
acceleration variance**.  On flying laps it lands at `ell≈1–2` (sf≈200), which interpolates
GPS jitter as acceleration → |a| of **100–2000 m/s²** (50–200 g, physically absurd) at
chi²≈0.9.  An ell-sweep on a fixed lap shows the accel magnitudes **stabilise on a plateau
at ell≈8–20** (accel_sd falls 28→1 m/s²) at physically credible grip.  **We therefore PIN
ell=10** (sf/sig_pos still from `fit_stint_hp`) and report the sweep:

| session    | ell=6  | ell=8  | ell=10 (pinned) | trend |
|------------|--------|--------|-----------------|-------|
| Belgium Q  | 3.94g  | 3.69g  | 3.51g           | −12%/step, monotone, flattening |
| Britain Q  | 4.85g  | 4.69g  | 4.54g           | −4%/step, flatter (auto_ell already 1–5) |

**ell sensitivity is the dominant systematic on the absolute grip number (~±10–15% over
ell 6→10), but it is COMMON across drivers — so the car-vs-driver SPLIT is robust to ell
even though the absolute g-number is not.**

## Fitted grip envelope (ell=10), per session — with covariance

| session   | lat grip (g)        | brake (g) | traction (g) | edge S/C | speed-dep e2 |
|-----------|---------------------|-----------|--------------|----------|--------------|
| Belgium Q | 3.51 (drv sd .056, boot sd .096) | 3.18 | 1.29 | **8.3 STRONG** | 0.00036 |
| Britain Q | 4.54 (drv sd .088, boot sd .125) | 3.30 | 1.15 | **14.7 STRONG**| 0.0016 |
| Spain  R  | 3.33 (drv sd .047, boot sd .021) | 2.67 | 1.18 | **15.5 STRONG**| 0.0081 |

- Physically credible: Silverstone (Britain) > Spa (Belgium) lateral grip (faster corners);
  race (Spain) lateral 3.3g < quali (fuel load + tire management), brake 2.7g < quali 3.2g.
- **Speed/downforce dependence (e2>0 everywhere)**: lateral extent grows with v². Strongest
  in the race (e2=0.0081, low base e0=13.8) — on race tires/fuel the envelope is more
  v²-(downforce-)driven. This is the downforce signature predicted by the direction doc.

## Available-grip vs utilization split — THE result
Coefficient of variation across drivers (lower = more shared):

| session   | cv(lateral grip) | cv(brake grip) | cv(utilization p90) |
|-----------|------------------|----------------|---------------------|
| Belgium Q | 0.016            | 0.054          | 0.006               |
| Britain Q | 0.019            | 0.027          | 0.007               |
| Spain  R  | 0.014            | **0.055**      | **0.027**           |

- **Lateral car grip is SHARED** (cv ≈1.4–1.9% across drivers; in Belgium/Britain the
  across-driver spread is *within* the bootstrap noise → statistically one envelope = the car).
- **Quali utilization barely separates drivers** (cv 0.6–0.7%): in qualifying everyone pins
  the limit (util_p90 all ≈1.05). Expected — quali is a maximal-utilization regime.
- **Race utilization separates ~2× the lateral-grip spread** (cv 0.027 vs 0.014): RUS pushes
  closest (p90 1.23), SAI most margin (1.14). The race is where the driver axis lives.
- Brake grip carries the most car/driver mix (cv up to 0.055 — SAI 2.93g vs PER 2.54g in
  Spain), consistent with braking being the most driver-modulated channel.

**Verdict: the friction envelope IS identifiable per session and IS a shared car property;
driver utilization separates from it, weakly in quali (saturated) and clearly in the race.**

## Compound notes (physics grip, NOT lap-time; no src/compound_prior import)
Spain R, SOFT vs MEDIUM lateral grip per driver: RUS +0.15g, HAM +0.11g, PER +0.10g,
SAI +0.10g, VER −0.03g. **SOFT shows higher lateral grip for 4/5 drivers** (~+0.1g, ~3%) —
the right physical direction (softer compound → more transmitted lateral force), measured
from forces. Honest scale: the compound delta (~0.1g) is small relative to the ell
systematic and near the lap-to-lap envelope noise — measurable and consistently signed, not
dominant. This is the THINKING for a physics-based compound regularizer; the evo bridge
stays for Phase 3.

## Honest limits
- Absolute grip g-number is ell-dependent (±10–15%); pin ell and treat the number as a
  *relative* car descriptor, not an absolute friction coefficient.
- The QHI=0.95 boundary sits below the true peak, so utilization r can exceed 1 (fine for
  relative ranking; not a calibrated 0–1 fraction).
- Quali cannot separate drivers on utilization (all saturated) — the driver signal needs a
  race (varied utilization) to emerge. For Phase-2 features, grip envelope = car (use quali
  for the cleanest envelope), utilization = driver (use race).

## Evidence
- `f5_verdict.json` — assembled cross-session verdict + ell sensitivity
- `f5_2023_Belgium_Q.json`, `f5_2024_Britain_Q.json`, `f5_2022_Spain_R.json` (+ `_ell6/8`)
- `f5_envelope_{session}.png` — extent-vs-speed curves per channel + utilization bars
- scripts: `scripts/experiments/f5_run.py`, `f5_plot.py`, `f5_verdict.py`
