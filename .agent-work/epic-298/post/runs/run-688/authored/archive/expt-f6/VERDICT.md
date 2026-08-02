# F6 Verdict — Acceleration observability & physical-ell prior (epic #445, THE CRUX)

**Question:** Can we set the smoother length-scale `ell` from a PHYSICAL prior on the car's
jerk/acceleration bandwidth, so the latent acceleration covariance is honest, consistent across
drivers, and tight enough to unlock the small-force channels (power/downforce/mass)?

**Verdict: QUALIFIED YES, via a FIXED PHYSICAL `ell`, not a data-fit one.** The data genuinely
cannot pin `ell` (honest-null on data-driven jerk-bandwidth identification), so `ell` MUST be an
assumed physical constant. Fixing `ell = 4.5 s` for every driver replaces the production lottery
with a consistent honest accel floor and unlocks the small-force channels (resolved-driver fraction
**4/10 -> 9/10**; per-driver accel sd spread **138x -> 1.8x**). Sensitivity of every downstream force
to `ell` is documented below and is the binding caveat for #449.

Sessions: 2022 Spain R (5 drivers) + 2023 Belgium Q (5 drivers), production estimator dogfooded
(`src.preprocessing.trajectory`: `fit_stint_hp`, `StintSmoother`, `heldout_chi2_full`, `acc_at`,
`vel_at`, `_state_at`).

---

## 1. The ell -> accel-covariance map (the crux, made crisp)

Sweeping `ell` at fixed (`sf`, `sig_pos`) from the production fit, per driver:

- **Held-out pos/speed chi² is FLAT** across the entire sweep. Example, Spain RUS:
  `chi2_pos` stays in **[0.68, 0.93]** (target = 1) across **ell = 0.9 -> 8.0**, while
  `accel_sd_long` ranges **401 -> 2.8 m/s²** — a **140x** swing at indistinguishable chi².
  Pooled over all 10 drivers in ell∈[1.2,6.0], 83% of chi²_pos points sit in [0.5, 2.0].
- **Posterior accel sd is prior-dominated:** it tracks the analytic Matérn-5/2 stationary
  `accel_sd_prior = 5·sf/ell²` (verified in the sweep JSON). chi² sees position/speed fit;
  acceleration is the 2nd derivative and is set by the prior, not the data.
- **Resolved-fraction is monotone in ell** and only takes off at ell ≳ 4.5. The single "resolved"
  driver per session was simply the one whose `fit_stint_hp` happened to draw a long `ell`:
  Spain VER drew ell=4.5 (res 0.238); Belgium PER drew ell=7.03 (res 0.691). Everyone else drew
  ell≈0.8–1.75 and was unresolved. **The resolution lottery IS the `ell` draw.**

`fit_stint_hp` drew `ell` over **0.80–7.03 (8.8x)** across these 10 driver-stints on two sessions —
it is loosely pinned exactly as F1/F3 reported.

Evidence: `evidence/f6_ell_accel_cov_map.png`, `evidence/f6_2022_Spain_R.json`,
`evidence/f6_2023_Belgium_Q.json` (per-driver `sweep` arrays).

## 2. Physical jerk/accel bandwidth — derivation + HONEST-NULL

From the **directly-measured speed channel** (a_long_truth = d|v|/dt is observable, NOT latent),
the brake-application 10–90% rise time at corner entry — a physical actuator timescale — is
**consistent across drivers**: pooled median **0.40 s**, range **0.18–0.55 s** (Spain race ~0.35–0.55;
Belgium quali sharper, ~0.18–0.43). This is the genuine longitudinal accel transient bandwidth.

**But this bandwidth does NOT pin `ell` data-drivenly (the honest-null):** an acceleration-calibration
probe (compare posterior a_long to raw a_long on hard-brake samples; find `ell` where posterior sd ≈
actual tracking RMS) gives a **calibrated ell that ranges 0.7 -> 8.0 across drivers** (median 3.35),
because:
  - In Spain (race, gentler transients) tracking error keeps falling with ell to ~2 m/s² at ell=8,
    so "calibration" pushes ell long.
  - In Belgium (quali, sharp ~0.2 s braking) long ell over-smooths real transients (tracking RMS
    stays high while posterior sd shrinks → over-confidence), pulling calibrated ell short (0.7–0.9).
  There is **no single ell where the longitudinal posterior is calibrated for all** — the kernel
  cannot simultaneously be tight enough for quali braking and honest about race coast. **This is the
  honest-null: the data cannot uniquely determine jerk bandwidth → `ell` must be assumed.**

Evidence: `evidence/f6_jerk_bandwidth.png`, `evidence/f6_accel_calibration.png`,
`evidence/f6_accel_calib.json`.

## 3. Recommended acceleration-aware calibration for #449 (concrete)

**Primary recommendation: pin `ell` to a fixed physical constant `ell = 4.5 s`** (do NOT let
`fit_stint_hp` choose `ell`; let it choose only `sf`, `sig_pos`). Rationale: 4.5 s is the shortest
`ell` at which the smoother reliably *tracks* the observable a_long to within a few m/s² across both
race and quali (tracking RMS floor ~3–5 m/s²), while keeping the posterior accel sd at a **consistent
honest ~9 m/s²** rather than the prior-blow-up of short ell. It is long enough to suppress the
spurious accel variance that swamps small forces, short enough to follow the genuine ~0.4 s brake
transients without large bias.

Concrete config change for the #449 estimator:
  - `StintSmoother(ell=4.5, sf=<fit>, sig_pos=<fit>, delta=<session>)`;
  - restrict `fit_stint_hp`'s `ell_grid` to a single value (4.5) OR add an `ell_fixed` argument and
    calibrate only `sf`/`sig_pos` to the chi² target.
  - Report posterior accel sd alongside every force estimate; flag any sample with |a| < 2·sd as
    unresolved (covariance-limited), per the F1 cross-cutting rule.

Two refinements worth a follow-up (NOT required for #449 v1):
  - **Non-stationary `ell`/roughness** (the `NSStintSmoother` already in the module): keep the long
    `ell=4.5` baseline but raise the per-step jerk variance in high-demand corner/brake samples via
    `build_roughness(kind="lon"/"tot")`, so quali braking transients are followed without inflating
    straight/coast accel variance. This is the principled fix for the race-vs-quali tension and is
    already plumbed in production code.
  - If a single constant is preferred for race-only mass work (F4), `ell=6.0` tightens the accel sd
    further (~5 m/s²) at minimal tracking cost on gentle race transients.

## 4. Does it unlock the small-force channels? Before/after (ell_prod -> fixed ell=4.5)

| driver        | ell_prod | res_prod | res@4.5 | accel sd_long prod | accel sd_long @4.5 |
|---------------|---------:|---------:|--------:|-------------------:|-------------------:|
| Spa/VER       |    4.50  |   0.238  |  0.238  |    9.3             |   9.3 |
| Spa/RUS       |    1.25  |   0.034  |  0.212  |  189.4             |   9.2 |
| Spa/SAI       |    1.40  |   0.043  |  0.227  |  141.7             |   9.0 |
| Spa/HAM       |    3.00  |   0.028  |  0.248  |   24.0             |   9.1 |
| Spa/PER       |    0.80  |   0.028  |  0.438  |  373.0             |   6.6 |
| Bel/VER       |    1.00  |   0.041  |  0.098  |  406.5             |  12.1 |
| Bel/PER       |    7.03  |   0.691  |  0.137  |    3.5             |   9.0 |
| Bel/LEC       |    1.00  |   0.101  |  0.507  |  203.0             |   9.0 |
| Bel/HAM       |    0.80  |   0.064  |  0.323  |  482.6             |  11.8 |
| Bel/SAI       |    1.75  |   0.380  |  0.628  |   49.2             |   6.9 |

- **Resolved-driver count: 4/10 -> 9/10.** Mean resolved fraction 0.165 -> 0.306.
- **Per-driver accel sd: from 3.5–483 m/s² (138x spread) -> 6.6–12.1 m/s² (1.8x spread).**
  This consistency — not just the lower floor — is the unlock: pooling across drivers/laps (the F1
  cross-cutting prescription) is only valid when the per-driver covariance is comparable, which it now
  is.
- The one driver that drops (Bel/PER 0.691 -> 0.137) is the former "lucky 1": ell_prod=7.03 made its
  posterior sd 3.5 m/s² — **over-confident**, not real resolution. At the honest ell=4.5 its sd is 9.0,
  the same floor as everyone else. Its old number was an artifact; correcting it is the right move.

**Implication for downstream F-experiments:** with a consistent ~9 m/s² longitudinal accel floor, the
small forces are still below a single-sample's noise (drag ~1–3 m/s², downforce/mass smaller), so they
remain covariance-limited per-sample — BUT they are now resolvable by POOLING, because the covariance
is honest and uniform across drivers/laps (N samples beat the floor as 1/√N). Power (F3, full-throttle
a_long ~2–10 m/s²) crosses the 9 m/s² floor on the strongest pulls and becomes resolvable per-stint
for most drivers, not the lucky 1. Grip (F5, ~15–40 m/s²) was always above the floor and is unaffected.

---

## Bottom line for #449

Set **`ell = 4.5 s` as a fixed physical constant** in the estimator; calibrate only `sf`/`sig_pos` to
chi². This is forced by an honest-null (data can't pin jerk bandwidth), justified by the consistent
brake-transient timescale (~0.4 s) and the tracking-error floor, and it converts the accel posterior
from a per-driver lottery (sd 3.5–483) into a consistent honest channel (sd ~9) that unlocks
pooling-based identification of the small forces. Every downstream force's covariance scales with
`ell`; report `ell` and accel sd with every estimate. Optional next step: `NSStintSmoother` roughness
on corner/brake samples to resolve the race-vs-quali tension without per-driver tuning.

Evidence: `.agent-work/expt-f6/evidence/` — `f6_2022_Spain_R.json`, `f6_2023_Belgium_Q.json`,
`f6_accel_calib.json`, `f6_ell_accel_cov_map.png`, `f6_jerk_bandwidth.png`,
`f6_accel_calibration.png`, `f6_before_after.png`. Scripts: `scripts/experiments/f6_run.py`,
`f6_accel_calib.py`, `f6_beforeafter.py` (branch expt/448-f6).
