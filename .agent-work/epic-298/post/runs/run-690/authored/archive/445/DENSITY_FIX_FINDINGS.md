# #445 — Air density in the CdA/drag fits (2026-06-16)

The drag/power fits backed CdA out at a **fixed sea-level RHO = 1.2** (`ribbon_reeval.RHO`).
The codebase already MODELS air density — `src/utils/environment.estimate_air_density_kg_m3`
(altitude + air-temp + humidity → ISA pressure → moist-air density). Wired it into the drag fits.

## What was used
- **Measured barometric pressure** from FastF1 weather (`weather_data.Pressure`) through the codebase
  moist-air formula — primary source. It encodes altitude AND actual race-day conditions and needs
  **no circuit-name mapping**, which matters because the name/country altitude lookup is wrong for
  exactly the tracks that count: `"Mexico City" → 0 m` (misses the whole 2240 m) and the three US
  races share `Country="United States"` (Austin 265 m vs Vegas 610 m — only `Location` disambiguates).
- ISA-altitude model (`estimate_air_density_kg_m3`) is the fallback when Pressure is missing; fixed
  1.2 is last resort. Module: `air_density.py` (`air_density(year, gp, ses)`), cached to
  `session_density.json`. All 22 rounds of 2023 resolved via measured-P.

## Result — densities and the CdA correction (CdA = 2·m·K/ρ scales as 1/ρ)
| effect | ρ | CdA factor |
|---|---|---|
| Mexico City (2240 m) | 0.905 | ×1.326 |
| São Paulo (800 m) | 1.045 | ×1.148 |
| Austria (677 m) | 1.075 | ×1.116 |
| warm sea-level tracks | 1.11–1.17 | ×1.03–1.08 |
| cool/dense | up to 1.23 | ×0.98 |

Fixed 1.2 over-stated density **everywhere** (warm air), so every car read too slippery — ~25% at
Mexico, a few % elsewhere. K (and therefore P) are density-free; only CdA changes. **Lap time is
unaffected** (in the quasi-static sim ρ cancels: drag re-multiplies by the same ρ the CdA was fit at).
The fix matters for the **reported CdA feature** — now the true drag area, comparable across tracks.

Sanity clamp moved to the **density-normalized** value (`0.5 < CdA·ρ/1.2 < 3.0`) so junk-rejection is
identical at every track; otherwise the ×1.326 at Mexico pushed all 7 max-downforce cars past the old
3.0 ceiling (dropped 10→3 teams).

## The validation surprise (the real finding)
The fix did **not** clear the Mexico relational-outlier flags — it made them **worse** (additive
detector: ALF/WIL/RBR 9→12σ SLIPPERIER). Root cause: density is a per-track **multiplicative** factor
(×1/ρ); the relational detector removed the track regime **additively** (median field shift). Additive
detrending can't undo a multiplicative confound — it amplifies the team spread (×1.326 at Mexico), and
that amplification masquerades as per-team anomalies.

**Fix: relational comparison in LOG space.** A per-track multiplicative factor becomes a common
additive log-shift the median removes. Proven density-invariant: log-relational on the fixed-ρ and
real-ρ CdA are identical (residuals match to 3 d.p., max |Δz| = 0.12 = clamp/bootstrap noise).
Applied to `outlier_detect.relational_outliers` (now reports % deviation from the car's rating).

After log-space, density-invariant relational flags (NOT density artifacts — they survive):
- RBR Singapore −23%, ALF/WIL/RBR Mexico −20/−20/−18%, AMR US +21%, MCL/FER Dutch +19/+16%.
- Pattern: the strongest residual flags cluster on **high-downforce / low-top-speed tracks**
  (Singapore, Mexico, Dutch). At low top speed the full-throttle a(v) curve has a short high-speed
  lever arm, so the CdA (drag) term is weakly constrained → **suspected CdA fit-reliability issue at
  low-top-speed tracks**, a separate open thread (not density).

## Files
- NEW `air_density.py`, `session_density.json`, `cda_density_compare.py`, `relational_logspace_test.py`
- `season_cda_fixedrho.json` = pre-fix CdA (kept for the before/after).
- threaded optional `rho` (defaults to old RHO): `ideal_lap_v2.fit_anchored/fit_2param/av_measured`,
  `long_throttle_probe.frontier_fit`, `ribbon_reeval.full_q_pd`; wired in `season_cda_collect.py`.
- `outlier_detect.relational_outliers` → log-space.

## RESOLVED — the residual flags were a DRS-closed lever-arm artifact (2026-06-16, follow-on)

Chased the residual flags to ground. Two hypotheses tested and **refuted**:
- **Lever arm by overall top speed** — refuted: Mexico has the 2nd-HIGHEST top speed (346 km/h, thin
  air) yet the biggest residual; Monaco the lowest top speed yet a small one. Spearman −0.29, broken
  by Mexico.
- **Aero-efficiency × downforce demand** — refuted: per-team residual vs the exogenous circuits.yaml
  downforce trait explains R²=0.04, BELOW the shuffle-W null (0.048, p=0.57). Slope SIGNS order
  sensibly (RBR/ALF/FER efficient, AMR/MCL/MERC draggy — known 2023 character) but carry no variance.

**Root cause = DRS-closed lever arm.** The CdA fit used DRS-CLOSED points only (`m = ~op`). At Mexico
the cars are on DRS for the whole straight, so the closed set tops out at v95=267 km/h with **0% of
fit points above 280** (Monza/Vegas: 49–50% above 280, 35% above 300). Drag — the high-speed `v²`
term — was pure extrapolation, then amplified ×1.326 by the low density. The bootstrap σ was blind to
it (3.9%, deceptively tight) because it only resamples the within-range cloud.

**Fix 1 — joint DRS fit (`drs_joint_fit.py`).** Fit BOTH regimes with a SHARED power P:
`a = P/(mv) − ½ρ·CdA_state·v²/m`. The DRS-OPEN points reach high speed (Mexico open vmax 355) and pin
P, which propagates through shared P to identify CdA_closed from the closed mid-speed points. Mexico
CdA_closed: **2.8–3.68 (extrapolated) → 1.2–1.76 (sane, normal track range)**; the WIL "slippery
outlier" (was lowest) corrected to mid-high. `season_drs.json`.

**Fix 2 — honest identifiability σ.** From the linear-fit covariance σ²(XᵀX)⁻¹, not bootstrap. Now
large where the lever is short (Monaco 17.7%, Singapore 14%, US 13.6%, Mexico 11.9%) and small where
levered (Japan 5.1%, São Paulo 6%) — vs the old uniform ~2–4%. (Printed `cond` is scale-dominated,
ignore it; the σ is the signal.)

**Fix 3 — σ-aware detector + filter.** `relational_outliers` z now divides by `sqrt(rsd² + σ_meas²)`
so a poorly-levered fit can deviate without flagging. Result: the Mexico SLIPPERIER cluster (9–12σ)
is **gone**; only a single marginal MERC +29% @2.9σ remains (one team, good σ there → candidate real,
not environmental). `SeasonFilter` on CdA_closed+σ_c gives Mexico Kalman gains 0.10–0.25 (leans on the
season prior), gain tracking σ — the per-weekend+prior middle path, mediated by honest σ.

## Research result — DRS closed/open is NOT a per-team fingerprint
Is the closed→open relationship a stable per-car aero signature across setups? **No.** DRS drag-cut is
~universal **~21%** (AMR 18.5% → WIL 23.8%); between-team σ=1.4% vs within-team σ=6.4% ⇒
discriminability 0.22 (≪1). Team means' SE (~1.6%) exceeds their spread — not distinguishable. Fits the
tightly-regulated DRS flap/slot. The *relationship* is real and structural (CdA_open ~ CdA_closed,
slope 0.4–0.7 < 0.79 const-fraction line, +intercept ⇒ more absolute drag shed at higher wing) but
**common**. Upshot: `CdA_open ≈ 0.79·CdA_closed + noise` — not an independent per-car axis; configured-
wing `CdA_closed` is the drag feature. Plot: `drs_consistency.png`. Code: `drs_consistency.py`.

## Files (follow-on)
NEW: `drs_joint_fit.py`, `season_drs_collect.py` (`season_drs.json`), `validate_drs.py`,
`drs_consistency.py` (+`.png`), `season_drs_filter.py`, `topspeed_discriminator.py`,
`drag_efficiency_decomp.py`, `drs_closed_leverarm.py`, `cda_sigma_check.py`.
`outlier_detect.relational_outliers` → σ-aware; `main` reads `season_drs.json` (CdA_closed).

## Power identifiability — degenerate with drag (2026-06-16, follow-on)
Hoped the better-levered joint fit would also resolve per-team POWER. It does NOT, cleanly. Setup:
field-relative P (global baseline, not PU-grouped) with the covariance σ_P. `power_analysis.py`.
- Absolute joint-fit power median **616 kW** (IQR 600–634), σ_P ≈ 17.6 kW (~3%).
- Per-team P shows between/SE = 2.9 ("resolved"), within-team scatter = pure measurement noise
  (no real per-weekend power tuning — power IS less per-track-variable than drag, as predicted).
- **BUT the P↔CdA degeneracy is unbroken: median per-FIT corr = +0.78** (over-P forces over-CdA to
  hold the curve — leakage is POSITIVE). Cross-team corr(power, drag) = **+0.69** ≈ the per-fit
  degeneracy ⇒ the per-team "power" is mostly drag leaking along the degenerate axis. The high-power
  teams (MCL +22, WIL +20, FER +20 kW) are exactly the high-drag teams. ~half the per-team power
  variance is drag-shared; the independent half is within noise.
- **PU baseline insufficient** (independent of the leakage caveat): within-PU σ = 9.3 kW > between-PU
  σ = 4.3 kW — same engine ≠ same measured power (Merc PU: MCL+22 … MERC−3). Measured "power" =
  effective propulsive (ICE + ERS deployment + drivetrain + residual drag leak), not bench ICE.
- Delivered power P(v)=m·a·v+½ρ·CdA·v³ is FLAT ~600–620 kW from ~160 km/h up (`power_curve_probe.py`)
  — the car is at peak power by 160 km/h (NOT torque-limited low). So a mid-band read exists:
  **MID-BAND power** (`power_midband.py`), P=90th-pct of m·a·v+½ρCdA·v³ over 150–215 km/h, cuts the
  leakage from joint +0.63 → **+0.48** — a PARTIALLY independent power axis (WIL +11.5, FER +10.1 kW
  read high-power at neutral drag — face-valid: Williams straight-line speed is power not just low
  drag; ATR/MERC low). Still ~half-confounded (drag term ~24% of delivered P, and CdA is fit-coupled).
- CONCLUSION: power is ~half-recoverable, not clean, from full-throttle alone — P and CdA share one
  equation. The clean decoupling is a **power-free drag measurement**: when COASTING (throttle off,
  no brake) drive power≈0 so a=−½ρCdA·v²/m−rolling gives CdA INDEPENDENT of power; feed that into the
  full-throttle fit and power falls out with no degeneracy (reuses the braking-frontier machinery with
  zero brake). NOT YET RUN — the decisive next lever for a clean power axis.
- Meanwhile: use GLOBAL baseline + per-team pickup + season prior for the COMBINED straight-line axis
  (well-resolved), and the mid-band power as a partial/uncertain power read; PU only a weak prior.

## Coast-down decoupling FAILS — hybrid regen (2026-06-16)
Ran it on quali cooldown/in-laps (`coast_decouple.py`). Data is plentiful — **median 2357 coast pts
per team** (cooldown laps, as predicted). But it does NOT work:
- VALIDATION corr(coast-CdA, joint-CdA) = **−0.12** — the coast drag doesn't match the real
  full-throttle drag at all.
- Feeding coast-CdA into power: leakage **+0.92**, absurd P (WIL +58 kW).
- ROOT CAUSE: F1 coast-down isn't free-rolling. Off-throttle the car HARVESTS with the MGU-K (regen
  braking ~up to 120 kW) + engine overrun braking; harvest amount is per-team/per-moment strategy. That
  powertrain deceleration swamps the v² aero term, so the fitted "CdA" measures harvest intensity, not
  drag (coast says WIL +24% drag while real drag is neutral — Williams harvesting, misread as drag). No
  ERS/MGU-K channel in FastF1 to subtract it. A road-car coast-down works; a hybrid F1 cooldown lap
  does not.

## BOTTOM LINE on power (all levers exhausted)
Power is NOT cleanly separable from drag with available telemetry: full-throttle joint fit 78%
degenerate; mid-band recovers it to ~half (+0.48 leakage); coast-down killed by regen. A clean split
needs an ERS deployment+harvest channel FastF1 doesn't expose. USE: straight-line capability as a
COMBINED well-resolved axis (global baseline + per-team + season prior); mid-band P as a partial/
uncertain power lean only; PU as a weak prior at most. DRAG (CdA_closed) remains the clean per-car
longitudinal axis (joint fit + honest σ + log-space σ-aware detection).

## Networked power baseline — robust but doesn't decouple (2026-06-16)
`power_network.py`: σ-weighted pairwise network rating of P vs field-mean. Hoped the network would cut
leakage because σ_P is largest where the degeneracy is worst (down-weight the leaked fits). It does NOT:
network vs field-mean orderings corr +0.97; leakage with drag network +0.61 vs field-mean +0.58 (no
gain). KEY INSIGHT: aggregation (mean OR network) reduces VARIANCE (noise), but the power↔drag confound
is a per-fit BIAS — same direction in every fit — and no aggregation removes a common-direction bias.
σ-weighting addresses variance, not bias. (Also physical: at top speed v_max³=2P/(ρCdA), so more-drag
AND same-top-speed ⇒ more-power is forced — power/drag are locked, not separable by any aggregation.)
WHAT WE RECOVER: a robust per-team LONGITUDINAL/straight-line rating — real (between/SE 2.9), stable,
face-valid (MCL/WIL/FER high, ATR/MERC low) — but ~60% drag-confounded. Use it as a "straight-line
performance" feature, not clean engine power. Network still worth it as the baseline (robustness +
σ-weighting for noise + non-mean aggregate), just no decoupling benefit.

## Open
- Lone-shot salvage if ever revisited: lower-ENVELOPE coast (least-regen points) might approach pure
  aero, but track gradient confounds and validation was −0.12 — low expected value.
- MERC Mexico +29% @2.9σ: real high-DF setup or noise (single-team, good σ). Non-structural; low priority.
- The lone MERC Mexico +29% @2.9σ: real high-downforce setup or residual fit noise? (single-team, good σ.)
- Production graduation: wire real density (`air_density`) AND the joint DRS fit + covariance σ into
  `src/physics/longitudinal_fit.py` (it uses its own RHO/`reference_density`); carry CdA_closed with its
  identifiability σ, not a bootstrap.
- Drag is now a per-weekend measurement + season prior (honest σ), NOT a season constant — the
  operating-point variance σ²_op≈0.034 (σ_op≈0.18 on CdA) is real setup variation, not noise to average.
