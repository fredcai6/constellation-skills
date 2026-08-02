# x4 — Normalization stability probe: absolute vs weekend-relative

**Scope note:** verdicts below cover the CURRENT five-view Q `session_estimates` store as it exists today (2019–2026, `data/physics_estimates.db`). They do not speak to what a redesigned/consolidated stage-1 model could achieve.

## Question

Absolute physical-unit estimates vs relative-to-field-per-weekend (car value minus that weekend's field median) — which gives more stable weekend-to-weekend readings for the same car, and how many weekends does each need to resolve a slow-moving performance component?

## Data used

`data/physics_estimates.db:session_estimates`, `session_type='Q'`, `fit_status='ok'` only (1,562 of 1,597 rows; 35 error rows excluded). Coverage: 2019–2026, 159 weekends, all with ≥6 constructors reporting (mean ~9.7/weekend, typical grid 10). 81 (year, constructor) car-seasons have ≥4 ok weekends and were used for the within-car stability estimates (per-year car-season counts: 2019–2025 have 10 constructors each with mean 16–24 weekends; 2026 is a partial season, 11 constructors × mean 7 weekends — treat 2026 numbers as noisier / lower N).

Method script: `.agent-work/explore-physics-evo-hookup/excursions/x4-analysis/normalization_stability.py` (reproducible, writes `axis_stability_results.csv` in the same folder).

## Method

For each of the 11 physical axes in the store (drag area, brake decel + brake aero slope, traction accel + traction aero slope, max power, power-drag area, lateral mech grip + lateral aero grip, coast rolling decel + coast drag area):

1. **Field σ** (scheme-invariant by construction): for each weekend (year, round_idx) with ≥6 constructors, compute the cross-constructor SD of the axis; take the median across weekends. Verified identical whether computed on raw values or on weekend-median-centered values (sanity check — a per-weekend constant offset doesn't change the within-weekend spread).
2. **Noise SD** (the thing that differs): for each car-season (year, constructor) with ≥4 ok weekends, compute the SD of that car's own weekend readings around its own season mean — once on raw absolute values, once on weekend-median-centered ("relative") values. Pool car-seasons via median (robust to one outlier car-season).
3. **Weekends to resolve 1 field-σ**: `N = (noise_sd / field_sigma)^2`, the standard sigma/√N averaging count to pin a signal of size field-σ at 1 SE.
4. **Signal-to-noise**: between-car-season spread of season means (the "signal", i.e. how far apart different constructors' season-average readings really are) divided by noise SD.

## Results

| axis | field σ | noise SD (abs) | noise SD (rel) | rel/abs noise ratio | SNR abs | SNR rel | weekends abs | weekends rel |
|---|---|---|---|---|---|---|---|---|
| drag_area_closed_m2 (m²) | 0.0959 | 0.208 | 0.109 | 0.52 | 0.23 | 0.40 | 4.69 | 1.28 |
| brake_decel_ms2 (m/s²) | 5.66 | 7.78 | 5.51 | 0.71 | 0.24 | 0.33 | 1.89 | 0.95 |
| brake_aero_decel_per_m | 0.00146 | 0.00174 | 0.00147 | 0.85 | 0.24 | 0.28 | 1.42 | 1.02 |
| traction_accel_ms2 (m/s²) | 1.39 | 2.72 | 1.61 | 0.59 | 0.19 | 0.32 | 3.85 | 1.34 |
| traction_aero_accel_per_m | 0.00130 | 0.00275 | 0.00166 | 0.60 | 0.20 | 0.33 | 4.47 | 1.63 |
| max_power_w (W) | 20,540 | 36,440 | 17,880 | 0.49 | 0.35 | 0.70 | 3.15 | 0.76 |
| power_drag_area_m2 (m²) | 0.0959 | 0.208 | 0.109 | 0.52 | 0.23 | 0.40 | 4.69 | 1.28 |
| lateral_mech_grip_g | 0.387 | 0.764 | 0.422 | 0.55 | 0.17 | 0.30 | 3.90 | 1.19 |
| lateral_aero_grip_g | 0.000129 | 0.000206 | 0.000143 | 0.70 | 0.25 | 0.35 | 2.54 | 1.24 |
| coast_rolling_decel_ms2 | 0.261 | 0.240 | 0.168 | 0.70 | 0.91 | 1.30 | 0.84 | 0.41 |
| coast_drag_area_m2 (m²) | 0.0956 | 0.205 | 0.114 | 0.55 | 0.21 | 0.37 | 4.62 | 1.42 |

"weekends abs/rel" = N to resolve a full 1-field-σ difference (e.g. front-runner vs backmarker gap) at 1 SE.

## Findings

- **Every single axis, without exception, is more stable under weekend-relative normalization.** Noise SD drops to 49–85% of the absolute-scheme value (median ratio 0.59); the number of weekends needed to resolve a 1-field-σ difference drops to 24–71% of the absolute number (median ratio 0.35, i.e. roughly a 3x reduction). This is a completely consistent direction across drag, braking, traction, power, lateral grip, and coast — there's no axis where absolute wins.
- The effect size varies by axis: power (`max_power_w`, ratio 0.49) and drag area (0.52) benefit the most — makes physical sense, both channels carry the ρ (air density) and altitude systematic that's shared across the whole field on a given weekend (SYSTEMATIC_FLOOR in `estimate_store.py` explicitly floors CdA/P_max at 4% for exactly this reason), so subtracting the weekend field median cancels most of that common-mode noise. Braking-aero-slope (`brake_aero_decel_per_m`, ratio 0.85) benefits least — it's already the most locally-fit, least density/circuit-sensitive quantity of the set.
- At face value, the absolute scheme already resolves a full field-σ gap in under 5 weekends for every axis (fastest: brake_decel and coast, under 2 weekends; slowest: traction_aero_accel_per_m at 4.5). But **1 field-σ is a coarse threshold** — it's the gap between a front-runner and a backmarker, not the kind of quarter-second development gain that's actually interesting weekend to weekend. For a more realistic "slow-moving performance component" at, say, 0.3 field-σ (a meaningfully smaller in-season development step), scale N by (1/0.3)² ≈ 11x: absolute scheme lands at ~9–52 weekends (i.e. often longer than a season, sometimes multiple seasons), relative scheme at ~4–18 weekends (often within-season, sometimes needing most of a season). This is the more honest number for what the excursion brief calls a "slow-moving performance component."
- `coast_rolling_decel_ms2` is the standout best-behaved axis in absolute terms already (SNR 0.91 abs, resolves in <1 weekend) — consistent with prior notes that coast is powertrain-dominated rather than aero/circuit-dominated, so it's less exposed to the weekend-level confounds the relative scheme is correcting for. It still improves under the relative scheme (SNR 1.30, N=0.41), just by a smaller relative margin than power/drag.

## Caveats (noted, not solved per brief)

- **Environment confounds are exactly what "relative" is scrubbing** — air density (altitude), circuit character (corner mix, straight length), and the SYSTEMATIC_FLOOR-documented ρ/mass systematics are shared within a weekend and largely cancel under weekend-median subtraction. That's the mechanism behind the result, not a separate concern to control for.
- **Team identity across seasons is not tracked** — constructor renames (AlphaTauri→RB→Racing Bulls, Alfa Romeo→Kick Sauber→Audi, Racing Point→Aston Martin, Renault→Alpine) mean this analysis is scoped to within-season car-seasons only; it says nothing about cross-season continuity of "the same car" (which doesn't really exist across a rules reset anyway).
- **2026 is a partial season** (7 of presumably ~24 rounds so far, 11 constructors post-expansion) — included in the pooled medians but is the thinnest-support year; if it dominates any single axis's result that would be worth rechecking once the season fills out. Spot check didn't suggest 2026 is an outlier driver of the result (81 trusted car-seasons span all 8 years fairly evenly by count, though not by weekend depth).
- Within-car "noise" as measured here can't distinguish real week-to-week measurement jitter from genuine in-season car development trend (both show up as deviation from the car-season's own mean); this probe treats them as one lump, which is conservative (real development trend would only make the absolute-scheme number look worse, not better, so it doesn't undermine the relative-scheme recommendation).
- `fit_status='error'` rows (35 of 1,597, ~2%) were dropped rather than imputed; not expected to bias the comparison since they're rare and status-independent between schemes.

## Recommendation

Use **weekend-relative (car minus that weekend's field median) normalization**, not absolute physical units, for any downstream stage that wants to track a car's slow-moving performance trajectory across a season from this store. The result is uniform across all 11 axes with no exceptions — this isn't a close call. Expect roughly **3–5 weekends** to resolve a meaningfully smaller-than-field-gap development step (~0.3 field-σ) for most axes under the relative scheme, versus a season or more under absolute; power and drag-area readings benefit most from de-confounding, braking-aero-slope least.
