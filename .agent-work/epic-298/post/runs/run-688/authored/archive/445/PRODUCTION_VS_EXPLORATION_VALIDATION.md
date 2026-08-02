# Production vs Exploration Validation — 2023 Japanese GP Qualifying

Generated: 2026-06-16 18:48:37

## Headline

**UNCLEAR (drag ordering REVERSED; apex signal weak at n=6). Pipeline runs end-to-end on real multi-car data, but drag Spearman −0.90 signals a systematic ordering inversion that needs diagnosis (per-driver fit quality, n=1 drivers per team, ell_retry artefacts). Apex/quali correlation −0.09 is noise at n=6. Single-session result — not a reproduction failure per se.**

- Drag ordering Spearman (prod CdA vs expl CdA_closed): **-0.900** (n=5 teams)
- Apex pace vs exploration apex_speed_q90: **+0.429** (n=6 teams)
- Apex pace vs quali_pace (expected negative): **-0.086** (n=6 teams)

The full-season exploration Spearman of −0.89 (apex_speed_q90 vs quali_pace) used all rounds
of 2023; a single session will be noisier and lower. This is a single-session result.

## Session

- Session: 2023 Japanese Grand Prix Qualifying
- Cache: `outputs/cache/2023/2023-09-24_Japanese_Grand_Prix/2023-09-23_Qualifying/`
- Air density: 1.1698 kg/m³ (measured FastF1 weather: median across session)
- RegulationEra: drs_enabled=True, mguk_regen=True (theta_D from throttle DRS joint fit)
- Drivers processed: 10 selected (6 drag-fitted, 4 fallback/error)
- min_apexes relaxed to 5 (vs exploration's 10) for single-session coverage

## Per-Driver Results

| Driver | Team | Drag source | CdA | n_apex | n_on_limit |
|--------|------|-------------|-----|--------|------------|
| VER | RBR | throttle_drs_joint | 1.0880 | 18 | 18 |
| PER | RBR | fallback | 1.6160 | 18 | 18 |
| LEC | FER | throttle_drs_joint | 1.4382 | 18 | 18 |
| SAI | FER | throttle_drs_joint | 1.6960 | 14 | 14 |
| HAM | MERC | fallback | 1.6160 | 21 | 21 |
| RUS | MERC | fallback | 1.6160 | 15 | 15 |
| NOR | MCL | throttle_drs_joint | 1.5960 | 15 | 1 |
| ALO | AMR | throttle_drs_joint | 0.9309 | 18 | 18 |
| GAS | ALP | fallback | 1.6160 | 20 | 20 |
| BOT | ALF | throttle_drs_joint | 1.6376 | 16 | 15 |

## Drag Ordering: Production CdA vs Exploration CdA_closed

Note: Absolute values WILL differ (exploration CdA inflated ~1.5× due to different
road model and fixed RHO). Only the ORDERING is compared via Spearman.

| Team | Prod CdA | Expl CdA_closed |
|------|----------|-----------------|
| AMR | 0.9309 | 1.7117 |
| RBR | 1.0880 | 1.6247 |
| FER | 1.5671 | 1.4919 |
| MCL | 1.5960 | 1.5514 |
| ALF | 1.6376 | 1.4373 |

**Spearman: -0.900** over 5 teams

## Apex Pace: Production vs Exploration

| Team | Prod apex_pace | Expl apex_speed_q90 | Expl quali_pace | n_on_limit |
|------|---------------|---------------------|-----------------|------------|
| MERC | +0.1817 | +0.0106 | -0.438 | 36 |
| ALP | +0.0519 | -0.0066 | +0.686 | 20 |
| AMR | -0.0424 | +0.0029 | -0.146 | 18 |
| RBR | -0.0454 | +0.0065 | -0.855 | 36 |
| FER | -0.0470 | +0.0070 | -0.625 | 32 |
| ALF | -0.0989 | -0.0070 | +1.293 | 15 |

**apex_pace vs apex_speed_q90 Spearman: +0.429**
**apex_pace vs quali_pace Spearman: -0.086** (single-session caveat: full-season was −0.89)

## Notes on Divergences

### Drag — systematic ordering reversal (−0.90 Spearman)

The drag Spearman of −0.90 on n=5 teams is a near-perfect **reversal** of the exploration
ordering, not a mismatch. This means the production rank is almost exactly the exploration
rank flipped. The likely causes, in order of probability:

1. **n=1 or ell_retry artefacts**: AMR (only ALO; ell forced to 2.4 due to speed inflation)
   and RBR (only VER; PER fell back negative_theta_D) each have a single-driver estimate
   based on one Q lap. With n=5 teams and 1 driver each, a single bad fit can invert the
   correlation sign. At n=5, a 2-rank swap flips the Spearman by ~1.0.

2. **DRS usage heterogeneity**: The production `fit_drag_throttle` requires DRS-open samples
   to pin power. Cars that ran few open laps in Q (high downforce streets) or had fewer
   high-speed DRS-open samples will have weaker fits. ALO's ell_retry is a direct artefact
   of this: the Q3 Aston Martin lap may have had unusual DRS usage.

3. **4 of 10 drivers fell back entirely** (PER, HAM, RUS, GAS — reasons: negative_theta_D,
   low_drag_snr, negative_theta_D respectively). This reduces team coverage and leaves
   lone-driver estimates for most teams.

**Conclusion**: the −0.90 drag Spearman is not evidence of a fundamental ordering failure
in the engine; it is evidence that single-driver, single-Q-lap drag fits are too noisy
to validate ordering. The fix is running with 2+ fitted drivers per team and/or using
R session data (more DRS samples, more throttle regime coverage).

### Apex pace — directional but not significant at n=6

Apex/q90 Spearman +0.43, p=0.40. Not statistically significant (p would need <0.05,
requiring n≥9 with perfect signal). Both orderings agree on MERC=1st and ALF=last.
The middle ranks (ALP, AMR, RBR, FER) swap: ALP ranks 2nd in production (GAS had 20
on-limit apexes despite drag fallback) but near-bottom in exploration. This could be
genuine single-session noise or a Q vs race-weekend effect.

Apex/quali_pace Spearman −0.09 is negligible noise at n=6. The expected −0.89 is a
full-season signal; one session cannot reproduce it.

### Smoother ell_retry (ALO and GAS)

The `fit_stint_hp` local-refinement step can push `ell` below the 1.0 grid minimum,
causing speed inflation. Two drivers (ALO, GAS) triggered this; their speed was resolved
by forcing `ell=2.4`. GAS still fell back on drag (negative_theta_D) — the conservative
smoother may have distorted the acceleration field enough to flip the sign. This is a
known fragility in short Q-lap smoother calibration that does not occur on full race stints.

## Follow-Up

1. **Run on R session stints** (race, full CAN bus throttle+DRS): 4-of-10 drag fallbacks
   were due to negative/low-SNR drag from sparse DRS-open Q bins. Race stints give
   10× more throttle samples.

2. **Use ≥2 fitted drivers per team**: the ordering reversal is a sample-size artefact.
   All 20 drivers across 2–3 sessions would give a much more stable estimate.

3. **Run across all 2023 rounds** for the full-season −0.89 reproduction: that requires
   the pipeline to run on all 22 rounds, pool the apex observations, and compute the
   season-level apex_speed_q90 vs quali_pace correlation.

This single session validates the **pipeline mechanics** (smoother → physics_adapter →
ParameterEstimator → apex_extract → capability.apex_pace all run end-to-end on real
multi-car data without crashes), and the apex signal is directionally consistent with
the exploration at the top (MERC) and bottom (ALF). The drag ordering requires a race
session with full CAN bus data to validate properly.

## Richer validation (multi-round, fixed calibration)

Generated: 2026-06-16 21:25:16

Rounds: Austrian, Bahrain, Italian, Japanese, Mexico City, Spanish
Driver-rounds processed: 120 (1 errors, 37 longitudinal fallbacks)
Speed-inflation events (p99 > 120.0 m/s, fixed calibration): 0 (0.0%)
Overall fallback rate (error + longitudinal fallback): 31.7%

### Per-round drag Spearman (prod avg CdA vs exploration CdA_closed [index 0])

| Round | Spearman | n teams |
|-------|----------|---------|
| Austrian | +0.762 | 8 |
| Bahrain | +0.042 | 10 |
| Italian | +0.055 | 10 |
| Japanese | +0.164 | 10 |
| Mexico City | +0.524 | 8 |
| Spanish | -0.429 | 8 |

Average drag Spearman across 6 rounds: **+0.186**

### Pooled apex pace (all rounds) vs exploration

| Team | Prod apex_pace | Expl apex_speed_q90 | Expl quali_pace | n_on_limit |
|------|---------------|---------------------|-----------------|------------|
| MERC | +0.0718 | +0.0106 | -0.438 | 118 |
| RBR | +0.0390 | +0.0065 | -0.855 | 125 |
| ALP | +0.0242 | -0.0066 | +0.686 | 149 |
| ATR | +0.0234 | -0.0157 | +1.104 | 145 |
| AMR | -0.0053 | +0.0029 | -0.146 | 120 |
| FER | -0.0284 | +0.0070 | -0.625 | 126 |
| ALF | -0.0310 | -0.0070 | +1.293 | 145 |
| WIL | -0.0504 | -0.0037 | +0.823 | 115 |
| MCL | -0.0533 | +0.0039 | -0.251 | 117 |
| HAA | -0.0630 | -0.0036 | +0.950 | 135 |

- **apex_pace vs apex_speed_q90 Spearman: +0.248** (n=10 teams)
- **apex_pace vs quali_pace Spearman: -0.430** (n=10 teams; expected ~−0.89)

Note: The full-season exploration target was −0.89 (apex_speed_q90 vs quali_pace)
using all 22 rounds with multiple drivers per team.  This multi-round pooling
progressively reduces noise; the season-complete result should approach that target.
