# Session 2026-06-15: grip-axis shape, smoother contamination + wide redo, Matérn-7/2

Collaborative exploration (human-driven, Socratic). Three threads: (A) what shape the
grip frontier can support, (B) a discovered smoother-calibration contamination + full
re-extraction on clean kinematics, (C) the acceleration order question (Matérn 5/2 vs 7/2).
All envelope files under `.agent-work/445/envelope/`.

## A. Grip-frontier shape — what the (v, g_tot) cornering cloud can support

The quali cornering cloud is a **2-parameter object per fit**: one shared mechanical
intercept `A` + one per-car downforce slope `B` on `v²` (+ the G_sat ceiling). Every
attempt to add a third shape DOF on the same projection fails identically (cond# 1e10–1e11,
held-out worse, steals from B):

- **Linear `v` term** (`vterm_experiment.py`): cond# 5e10, held-out pinball +400–535%, C
  sign-inconsistent. `v` and `v²` collinear over a corner's speed range — not separable.
  (Clean-data nuance: C sign-consistency 77%, so a faint real load-sensitivity exists, but
  the collinearity wall makes it unusable.)
- **Per-car intercept `A_c`** (`shape_intercept_experiment.py`): cond# 2e11, A_c teammate
  gap 0.47–0.59 g (≫0.3 g → noise/line, not a car property), and it CORRUPTS B (+145–174%).
  Mechanical grip is environmental (tyre×surface), shared across the weekend's cars, NOT a
  separable car axis. Free exponent `v^p` is the same degeneracy → ruled out.
- **G_sat fitted shared per weekend**: rejected on design grounds (human) — a shared ceiling
  removes cars' ability to differ at top-end grip; same field-coupling sin as a shared field term.

**Anisotropy (the productive move).** Split `g_tot = hypot(a_lat, a_long)`:
- **Pure-lateral apex** (`a_lat`, `|a_long|/a_lat < 0.3`) is a STRICT SNR upgrade over the
  magnitude frontier: cleaner per-car B (teammate gap 0.19 vs 0.23) AND tighter uncertainty
  (bootstrap R ratio L/M ≈ 0.62×) on ~40% of the nodes. The discarded combined-loading content
  is DRIVER, not car (trail-brake/on-power "combined excess" teammate-gap ≥ between-team
  spread). So the magnitude frontier was lateral-signal + driver-noise; lateral strips the noise.
  → **ADOPT the pure-lateral apex frontier as the grip observable.**
- **Longitudinal (braking)** via friction-ellipse projection (`braking_collect.py`,
  `aniso_long_fit.py`): pure straight-line braking ~doesn't exist (cars trail-brake; median
  lateral on braking points ~2.3 g), so project the combined cloud onto the long axis using
  G_lat. Sensor-cap limited: speed channel is 4.2 Hz, peak decel sub-sample → truncated ~3.5 g
  (real ~5 g unrecoverable; not a code cap, a Nyquist floor).
  **DUD — retire the channel (2026-06-16 reeval, A1, LONGITUDINAL_REEVAL_FINDINGS.md).** The
  "+0.48 corroboration" I claimed below in §B was a **GSAT-clip artifact**: reusing `fit_weekend`
  silently clips along_eq at GSAT=5.2 (a LATERAL tyre ceiling) on the longitudinal cloud, discarding
  ~9% high-trail-brake points whose ellipse-inflation is computed from B_lat → manufactured coupling.
  Relax clip → −0.29; remove → +0.04 (vanishes). Compounding: G_lat extrapolated 1.3–2× beyond its
  support (80% of braking points), sensor truncation suppresses the v² slope 3.4× (frontier peaks at
  ~230 km/h then DECREASES — impossible). No κ·B_lat decomposition recovers drag (≈ −0.05 vs CdA).
  Only lateral-apex B and the independent CdA channel are valid aero observables.

## B. Smoother contamination + wide redo (the big one)

**Discovery (human prompt: "common errors for position and speed?").** Every envelope
extraction used `grip_iter`'s hardcoded `StintSmoother(ell=2, sf=100, sig_pos=0.3, delta=0.06)`.
At those HPs the per-channel held-out **χ²_pos = 33, χ²_spd = 25** (target 1.0) — i.e. `sig_pos`
declared 0.3 m when the position channel is really ~1.8 m noisy → over-trusting position ~6× and
leaking its noise into velocity/accel; AND the time offset `delta` was an assumed constant 0.06
when it varies per session. Position/speed noise models are correctly SEPARATE units, but the
hardcoded values bypassed the production per-channel χ²-target calibration.

**Fix.** Production `session_offset()` (one global inter-stream `delta`/session) +
`fit_stint_hp()` (χ²-target grid over ell/sf/sig_pos). Per-session calibrated HPs vary widely:
**ell 0.8→7.0, sig_pos 1.4→2.5 m, delta 0.0→0.15 s**, all at χ²≈1. Re-extracted all node clouds
through the calibrated smoother (`calibrated_extract.py` → `calibrated_aniso_nodes.npz`,
`calibrated_braking_nodes.npz`, `calibrated_hp.json`); re-ran the four tests
(`calibrated_reanalysis.py`).

**What clean kinematics CHANGED:**
- **Constructor grip ordering FIXED.** Contaminated put HAA top / **RBR 8th** ("Haas paradox").
  Clean: **RBR top** cornering grip (3.43, top in both magnitude and lateral), FER drops low.
  RBR-top is physically right (RB19 benchmark). **The old "RBR low-DF yet fast" contradiction was
  a contamination artifact, not a real finding** — corrects [[physics-three-stage-bootstrap]].
- ~~**Longitudinal rescued** dud→corroborating~~ **RETRACTED 2026-06-16 (see §A):** the +0.48 was
  a GSAT-clip artifact, not corroboration. Clean kinematics did NOT rescue the braking channel —
  it's a dud (un-clipped corr ≈ 0). Retire it.

**What HELD:** lateral-apex SNR win (slightly stronger, R ratio 0.62×); v-term DEAD; per-car
intercept DEAD.
**What did NOT change:** between/within car-signal ratio still <1 (weekend car signal below
teammate noise → season filter still required); grip-frontier ≠ lap-pace at the observable level
(Haas #2, FER low persist — a single grip-vs-speed number isn't pace).

## C. Acceleration: Matérn-5/2 vs 7/2 (human idea — jerk as the random process)

Production smoother is Matérn-5/2: state `[f,ḟ,f̈]`, white noise on JERK → acceleration
continuous but NOT differentiable. Human proposal: push white noise up one derivative →
**Matérn-7/2** state `[f,ḟ,f̈,⃛f]`, white noise on SNAP → acceleration differentiable (physically
truer; driver inputs / tyre build-up are continuous). Built a generic-order smoother
(`matern_smoother.py`, order-3 reproduces production to 1e-10; P_inf via Lyapunov solve).

**Arbiter (corrected several times).** Held-out POSITION is the wrong, velocity-dominated, noisy
observable. Held-out **SPEED** (σ 0.49 m/s, clean) is acc-sensitive. RMSE is outlier-gamed (a ~1%
tail of telemetry-glitch bridges, uncorrelated with |dv/dt|) — use ROBUST metrics (median|e|,
glitch>5). And HPs must be per-order χ²-calibrated, not hand-tuned.

**Result** (`accel_order_calibrated.py`, both orders calibrated identically to χ²≈1, 4 sessions):

| order | median \|e\| (m/s) | MAE | glitch>5 |
|---|---|---|---|
| 5/2 | 2.114 | 8.38 | 36.4% |
| **7/2** | **0.465** | **1.04** | **2.8%** |

Mechanism: to hit χ²≈1, **5/2 sometimes collapses to short ell** (Hungarian 1.0, Vegas 1.2) — a
short-ell 5/2 is well-calibrated but a terrible point-predictor (rough non-differentiable velocity
→ noisy between-post speed). **7/2 reaches χ²≈1 at moderate ell every session** (4.5–5.6) — flexible
WITHOUT roughness → velocity/accel both calibrated AND accurate, held-out speed at the sensor floor.
χ²≈1 guarantees honest uncertainty, not good prediction; 7/2 gives both.

**7/2 doesn't beat the 0.49 m/s floor (4.2 Hz Nyquist) — it REACHES it robustly where 5/2 falls
into a rough-velocity trap.** Worth proposing for the production smoother (cost: 8-state vs 6-state,
~1.7×/step). Scope caveat: 4 sessions, HPs from VER's stint — widen before a PR.

## D. Recursive Bayesian downforce prior + clean baseline fingerprint (`season_prior_bayes.py`)

Replaced `season_prior_filter.py`'s fit-fresh-then-smooth (Kalman on point estimates) with
the correct **prior-IN-the-fit**: carry each car's downforce-deviation posterior `δ_c` forward
and use it as a penalty INSIDE next weekend's penalized quantile-IRLS frontier fit
(`B_c` pulled toward `L_r + μ_c⁻` with the carried precision; posterior from Laplace curvature).
- Config handled by an **exogenous** track downforce-demand index `W_r` (hardcoded, NOT field-fit):
  `L_r = b0 + β·W_r`, `δ_c = B_c − L_r` is the season-carried latent. No field-mean coupling.
- **Calibrated uncertainty** (the key fix): weights normalised to honest effective-N + Hessian
  scaled by frontier residual σ̂², so thin tracks read genuinely uncertain and the prior can bite.

**Monza borrow-strength (prior over rounds 1–13 → Monza posterior vs Monza-only fresh):**
posterior var(B) **71% tighter**, teammate |Δδ| **88% more consistent**, rank-corr vs season
truth **+0.255 (prior) vs −0.445 (fresh)** — fresh thin-Monza ANTI-correlates with truth; the
prior flips it positive. Validates the architecture on the thin-data stress case, on clean nodes.

**FULL-SEASON BASELINE fingerprint (clean kinematics; descriptor = season-average δ + drag fusion):**
RBR **efficient #1** (DF_z +1.22, drag_z −1.21, eff +2.43) — the contamination-fix headline (dirty
fingerprint had RBR low-DF). Quadrants: RBR/HAA/ALP efficient; AMR/MERC/MCL draggy-grippy; WIL/ATR/FER
slippery-minnow; ALF draggy-no-DF. Known weak spots (pre-existing, not contamination): HAA reads
efficient #2 (grip-frontier ≠ pace — real quali cornering grip it can't translate); MCL reads draggy
(drag channel averages its mid-season upgrade — needs the adaptive-jump term). Descriptor uses the
season-AVERAGE δ, not the forward-filter final state (which drifts recency-biased to late low-DF tracks);
the filter's validated value is per-race borrow-strength, not the season aggregate.

## E. Adaptive-jump test + obs-variance calibration fix (`upgrade_jump_test.py`, `season_prior_bayes.py`)

**Adaptive-jump test (NEGATIVE for grip channel).** Tried the jump on McLaren's mid-2023 aero
upgrade. The grip-δ upgrade (~0.3e-3 shift) is BELOW the per-race δ scatter (~0.7e-3), so it's not
per-race detectable (between/within<1 again). The jump fired on noise (every car) and made tracking
WORSE — but that exposed the real bug:

**Obs-variance was under-calibrated 34×.** The within-weekend Laplace var (node scatter, 7.86e-9)
ignores the between-race OPERATING-POINT noise (track/setup/fuel/conditions) — the genuine
observation noise on the season latent, estimated robustly (MAD pooled residuals) at **σ²_op = 2.63e-7**.
FIX: the season update is the correctly-calibrated **two-stage Kalman** with `R = v_w + σ²_op` (NOT the
prior-in-the-fit, which double-counts — the "fit-fresh-then-smooth is wrong" critique was really "wrong
R"; the structure was fine). Thin tracks self-down-weight (large v_w → large R → small gain). Post-fix:
jump never fires spuriously (correct — no shift exceeds σ²_op); Monza borrow-strength holds on robust
metrics (62% tighter, 70% teammate-consistent). Monza rank-corr is noise (per-car δ all within ±0.0003).
The jump is a no-op in this low-SNR channel; it would only earn its keep on the higher-SNR drag channel
(unbuilt). Baseline fingerprint unchanged (season-average, filter-independent).

## Files (all `.agent-work/445/envelope/`)
- `season_prior_bayes.py` — recursive Bayes downforce prior (two-stage Kalman, σ²_op-calibrated R, exogenous wing) + Monza test + baseline fingerprint.
- `upgrade_jump_test.py` — adaptive-jump test (negative for grip; surfaced the obs-var miscalibration).
- `matern_smoother.py` — generic-order Kalman-RTS (5/2 / 7/2), Lyapunov P_inf, self-check vs prod.
- `accel_order_calibrated.py` — per-order χ²-calibrated held-out-speed comparison (the 7/2 result).
- `calibrated_extract.py` — per-session calibrated re-extraction → calibrated_{aniso,braking}_nodes.npz, calibrated_hp.json.
- `calibrated_reanalysis.py` — re-runs the 4 grip tests on clean clouds vs contaminated baseline.
- `aniso_collect.py`/`aniso_fit.py` — lateral-vs-magnitude split. `braking_collect.py`/`aniso_long_fit.py` — longitudinal ellipse.
- `vterm_experiment.py`, `shape_intercept_experiment.py` — the dead shape-DOF tests.
