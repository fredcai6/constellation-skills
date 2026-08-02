# GRIP-1 — Static grip model: isotropy test + μ-from-load separation (epic #445 Phase-2)

Model tested: **grip-limit accel = μ·N/m = μ·(g + k_df·v²)**, separating tyre friction
coefficient **μ** from normal-load accel **N(v)/m = g + k_df·v²** (weight + aero downforce).
Forces dogfooded from the production estimator (`src.preprocessing.trajectory`):
- **LATERAL** = kinematic `a_lat = v²·κ`, κ=(vx·ay−vy·ax)/|v|³ — clean speed × geometric
  curvature from the smoother's velocity & honest accel (NOT raw accel magnitude; weak-form).
- **LONGITUDINAL** = smoother's honest tangential force `(vx·ax+vy·ay)/|v|` (position-anchored).
2×2 posterior accel covariance rotated into the velocity frame per sample.
Per flying lap, **ell PINNED = 10** (auto-ell landed 1.0–4.5 → rejected, F1/F5 caveat;
chi2_pos≈0.96–1.02 confirms pos/speed fit honest). k_df=1.298e-4 s⁻²/(m/s)² from G1's
lateral fit (C_df/μ_lat). Sessions: 2023 Belgium Q, 2024 Britain Q, 2022 Spain R.

## (1) ISOTROPY VERDICT — **ELLIPSE, strongly anisotropic. NOT a circle.**

Load-normalized μ per direction (μ_dir = peak grip accel ÷ N(v)/m), pooled over 5 drivers,
±across-driver sd (the covariance referee):

| session    | μ_lat        | μ_brake       | μ_trac (low-v grip) | brake/lat | trac/lat | z(lat−brake) |
|------------|--------------|---------------|---------------------|-----------|----------|--------------|
| Belgium Q  | 3.27 ± 0.06  | 2.46 ± 0.14   | 1.35 ± 0.07         | 0.75      | 0.41     | 5.6 σ        |
| Britain Q  | 4.19 ± 0.10  | 2.58 ± 0.05   | 1.30 ± 0.05         | 0.62      | 0.31     | 13.9 σ       |
| Spain  R   | 3.72 ± 0.14  | 2.02 ± 0.09   | 0.95 ± 0.10         | 0.54      | 0.26     | 10.5 σ       |

**μ_lat > μ_brake > μ_trac in every session, separated by 5–14 σ.** The friction limit is a
flattened ellipse, not a circle: braking grip is ~25–46 % below lateral, and grip-limited
low-speed traction is ~60–75 % below lateral. The brief's ratified isotropic-first assumption
is empirically **FALSIFIED** — anisotropy is first-order here, not second-order. (μ_lat ordering
Britain>Spain>Belgium matches F5's g-numbers and the physics: Silverstone's fast corners.)
Plot: `grip1_isotropy_and_load.png` (top row = ellipse vs isotropic circle).

Caveat on the *interpretation* of the asymmetry: μ_lat is a clean steady-state grip plateau;
μ_brake/μ_trac are honest but each carries a known confound — braking includes engine-brake +
aero-balance/weight-transfer, and **traction's downforce growth competes with the power cap**
(see §4). So the ellipse is real and large, but "μ_brake/μ_trac" are *directional grip indices*,
not pure tyre coefficients in the way μ_lat is.

## (2) μ-FROM-LOAD SEPARATION — **load model is DIRECTIONALLY RIGHT but INCOMPLETE.**

Does N(v)=m·g+downforce·v² absorb the F5 envelope speed-dependence (e2>0), leaving μ flat in v?
μ_lat(v) = boundary(v)/(N(v)/m), per speed bin (22–83 m/s; top straightline bin excluded):

| session    | μ_v rel-slope over range | free e2 (F5 comparison) | reading |
|------------|--------------------------|-------------------------|---------|
| Belgium Q  | **+0.03 (flat)**         | 0.00024 (F5: 0.00036)   | load model absorbs the speed-dep → μ clean & flat ✓ |
| Britain Q  | +0.20 (mild residual)    | 0.00158 (F5: 0.0016)    | μ still drifts up with v — k_df too small |
| Spain  R   | +1.30 (strong residual)  | 0.00783 (F5: 0.0081)    | load model clearly under-absorbs — μ grows with v |

**Honest verdict: PARTIAL.** With the *single* G1-lateral-calibrated k_df, μ becomes ~speed-flat
in low-downforce quali (Belgium) — the separation works there and μ_lat IS a clean per-tyre
coefficient. But where the downforce signature is strongest (Britain's fast corners, the race on
race-tyres/fuel), the e2 residual is larger than a fixed k_df explains, so μ(v) still rises — the
**load model is incomplete**: a single car-level k_df underestimates downforce growth in the
high-load cases (ride-height/rake aero sensitivity, deferred in MODEL_SCOPE, is the likely missing
term; also tyre-temp build-up through fast corners). This is the right physical direction
(N(v) does soak up *most* of e2) but k_df needs to be session/car-fitted, not borrowed —
GRIP-2 should fit k_df jointly with μ, not assume it.

## (3) PER-COMPOUND μ (Spain R, SOFT vs MEDIUM) — physics-based, NO compound_prior import

μ_lat per compound (corner samples split by Compound tag, same load model):

| driver | MEDIUM | SOFT  | Δ(SOFT−MED) |
|--------|--------|-------|-------------|
| VER    | 3.63   | 3.73  | +0.10       |
| RUS    | 3.58   | 4.13  | +0.55       |
| HAM    | 3.59   | 3.71  | +0.12       |
| SAI    | 3.80   | 3.29  | −0.51       |
| PER    | 3.92   | 3.86  | −0.06       |

**SOFT shows higher lateral μ for 3/5 drivers** (mean ≈ +0.04, median +0.10) — the right physical
direction (softer compound → more transmitted lateral force), measured purely from forces. But
the per-driver scatter (SAI/PER invert) exceeds the mean delta: the compound μ-difference (~0.1,
≈3 %) is real-but-small, swamped by lap-to-lap envelope drift and stint phase (deg/temp) in an
18-lap race. Consistent with F5's ~+0.1 g. → physics CAN recover compound ranking, but needs the
**degradation STATE** (GRIP-2) to clean the stint-phase confound before it can supplant the
incumbent lap-time estimator.

## (4) POWER-CAP vs GRIP-LIMIT on the traction side

At corner exit, +a_long is **grip-capped at low v** (μ·N/m, the "wheels hold the ground stepping on
the pedals" regime) and **power-capped at high v** (a ≈ P/(m·v) − drag, falls ~1/v). In Belgium/
Britain quali the full-throttle traction boundary **falls monotonically from v≈40 m/s up**
(17→2 m/s²; a·v power-index decays with drag) → at racing speed traction is *entirely power-/drag-
limited*, NOT grip-limited. The grip-capped branch that measures μ_trac lives **below ~35 m/s**
(low-speed corner exit, throttle application). Reading μ_trac there gives the clean low-v values:
Belgium 1.13, Britain 0.92, Spain 0.82 — consistently the smallest of the three directions. So the
traction envelope = **circular-μ·N limit ∩ power cap**, exactly the ratified model: only the
low-speed corner-exit samples are grip-limited and define μ_trac; everything above the crossover
is the power-cap, which carries *engine* capability, not tyre μ.

## Guardrails (proving ourselves wrong)

- **Held-out (leave-one-lap-out) posterior-predictive**: train μ on N−1 laps, predict the held-out
  lap's per-speed-bin boundary = μ·N(v)/m. Reduced χ²: Belgium **3.8**, Britain **2.8**, Spain **35**;
  frac within 2σ: 0.86 / 0.72 / 0.61. **Quali reproduces held-out grip within ~2–4× the formal
  covariance** (μ·N predicts unseen laps, modulo a quantile-sampling/between-lap-drift inflation —
  the same ×2.6 overconfidence G1 measured). **The race χ²≈35 is the honest red flag**: an 18-lap
  race stint has large real between-lap drift (tyre deg, fuel burn, traffic) that a *static* μ
  cannot capture — i.e. the static model is falsified across a race stint and **demands the
  GRIP-2 degradation STATE.** Honest-null on static-μ-over-a-race-stint.
- **Isotropy falsified honestly**: it IS an ellipse (5–14 σ), quantified above — not assumed.
- **Load model falsified honestly**: μ is NOT fully flat in v where downforce is strong (§2) — a
  single borrowed k_df is incomplete; reported, not hidden.

## ell reported
Pinned **ell = 10** (grip regime, per F5/F6). auto-ell 1.0–4.5 (rejected: chi2_pos blind to accel
var). chi2_pos median 0.96–1.02 (pos/speed fit honest). Production → NSStintSmoother state-dependent
ell (decided in PHASE2_SYNTHESIS).

## Provenance caveat (flagged)
Longitudinal grip uses the **position-anchored smoother force** (not the raw Speed channel), per the
expt-spdcheck concern that Speed may be wheel-derived (lockup/wheelspin bias on braking/traction).
This is the brief's preferred source; the lateral channel is curvature (position geometry), immune.

## Evidence
- `grip1_verdict.json` — cross-session μ_lat/brake/trac ± sd, ratios, z, load-flatness, held-out χ².
- `grip1_2023_Belgium_Q.json`, `grip1_2024_Britain_Q.json`, `grip1_2022_Spain_R.json` — per-driver
  envelopes, μ(v) bins, traction split, compound μ, held-out.
- `grip1_isotropy_and_load.png` — friction ellipse vs isotropic circle (top) + μ_lat(v) flatness (bottom).
- scripts: `scripts/experiments/grip1_run.py`, `grip1_plot.py` (branch expt/448-grip1).
- layer-1 harvest checkpoints: `.agent-work/expt-grip1/ckpt/grip1_*.npz`.

## Bottom line for the grip MODEL (GRIP-2 input)
1. The friction limit is an **anisotropic ellipse** (μ_lat ≫ μ_brake ≫ μ_trac, 5–14 σ) — the
   isotropic-circle first model should be **upgraded to a 3-axis ellipse**, OR μ_lat used as the
   primary clean tyre coefficient with brake/traction as separate directional indices.
2. **N(v) separation works in clean quali** (μ_lat speed-flat, Belgium) → μ_lat IS the clean
   per-tyre coefficient GRIP-2 should let evolve; but **k_df must be fitted, not borrowed** (it
   under-absorbs e2 in high-downforce/race cases).
3. **Static μ is falsified over a race stint** (held-out χ²≈35) → GRIP-2's degradation STATE is
   required, and is exactly where the compound signal (small & drift-confounded here) will resolve.
