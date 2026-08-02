# P2 — Corner-severity-class granularity noise check

**Question:** when per-driver utilization deficits are measured at corner-severity-class
granularity (k=4, instead of the existing 4 coarse regimes), what is the per-class
per-weekend noise level — usable signal or mush at k=4?

**Verdict: usable signal, not mush.** The noise ratio (within-driver across-weekend
scatter ÷ between-driver separation) stays in a narrow band — **1.93–2.40** across all
four severity classes, essentially indistinguishable from the **2.32–2.39** the existing
macro `slow_corner`/`fast_corner` regimes already carry. Going to k=4 does not blow the
ratio up. See caveats below on what this small excursion does and doesn't establish.

## What was run

`data/driver_utility_observables.db` does **not** exist on disk (confirmed before
starting) — the #628 pipeline is code-complete but unrun at scale, so there was no
persisted table to re-bin. Instead of depending on that DB, this excursion imports the
#628/#510 machinery directly (`car_prior.build_car_ceiling`, `session_fit`, `ribbon`,
`regime_utilization`, `driver_utility_observable.compute_regime_deficits`,
`physics_simulator.PhysicsSimulator`) read-only and runs the live computation in a
throwaway script, computing **both** the macro-regime baseline (unmodified,
`compute_regime_deficits`) and the fine-grained severity-class binning side by side on
the same simulated ideal laps.

- Script: `C:\Programs\f1Brainz\.agent-work\explore-ref-utilization\excursions\scratch\P2\severity_class_noise.py`
- Outputs: `p2_point_level.csv` (29,634 rows), `p2_class_level.csv`, `p2_macro_level.csv`,
  `p2_summary_class.csv`, `p2_summary_macro.csv`, `p2_errors.txt` (empty — **zero errors**,
  all 24 driver-weekends succeeded), all in the same `scratch/P2/` directory.
- Sample: 2023 Q, 4 rounds chosen for corner-type spread and enough causal history for
  `strictly_pre=True` ceilings — **Spain (R7), Austria (R9), Hungary (R11), Italy (R14)**
  — × 3 top constructors × 2 drivers each — **Red Bull (VER/PER), Ferrari (LEC/SAI),
  Mercedes (HAM/RUS)** = 6 drivers × 4 weekends = 24 driver-weekends.
- Runtime: ~11 min total (session load + ribbon build + 3× `build_car_ceiling`/
  `simulate_lap` + 6× `fit_best_lap_trace` per round).

## Binning (stated, as invited by the handoff)

`radius_m = 1 / |curvature|` at every ribbon grid point. This is **not** an
approximation of the `corner_descriptors.py` steady-state radius — on the same grid,
`a_lat = v_real**2 * |kappa|` (the identity `regime_utilization._build_regime_masks`
already uses), so `v**2 / a_lat` reduces algebraically to exactly `1/kappa`,
independent of speed. Points are gated to `|kappa| >= CURVATURE_THRESHOLD` (the same
corner gate the macro scheme uses), **pooling** what the macro scheme splits across
`slow_corner` + `fast_corner` and **ignoring the macro braking-priority carve-out**
(severity is a property of the corner's geometry, not of whether the driver happened
to still be braking there). Class edges are **quartiles of `log10(radius_m)`** —
log-space per `property_mixture.py`'s documented finding that radius is a heavy-tailed
multiplicative continuum — computed **once**, pooled over all 29,634 corner points
across every driver/weekend in the sample, so class1…class4 ("tight"→"very-fast") mean
the same physical severity everywhere. This mirrors the domain-capped k≤4 ceiling in
`property_mixture.fit_property_mixture` but is a **quantile-bin proxy, not an actual
GMM fit** — flagged explicitly since the handoff permitted this substitution.

Global edges (radius_m): **21.2 | 117.3 | 373.4 | 1518.3 | 9995.1** (class1 = tightest
hairpins/chicanes, class4 = fast sweepers/kinks).

## Results

| granularity | group | within-driver scatter | between-driver sep. | **noise ratio** | mean n_points/driver-weekend |
|---|---|---:|---:|---:|---:|
| macro (existing) | slow_corner | 2.35 | 1.01 | **2.32** | 785 |
| macro (existing) | fast_corner | 3.03 | 1.27 | **2.39** | 163 (min 70) |
| k=4 severity | class1 (tight) | 3.31 | 1.72 | **1.93** | 309 (min 153) |
| k=4 severity | class2 | 1.79 | 0.89 | **2.01** | 309 |
| k=4 severity | class3 | 2.36 | 0.98 | **2.40** | 309 |
| k=4 severity | class4 (fast) | 1.84 | 0.78 | **2.37** | 309 |

(`within-driver scatter` = mean over drivers of the std of that driver's per-round mean
deficit across weekends; `between-driver sep.` = mean over rounds of the std across
drivers' mean deficit that round; deficits in m/s, `g = v_ideal − v_real`.)

Two things stand out:

1. **The ratio doesn't degrade with granularity.** Splitting into 4 severity classes
   instead of 2 macro corner regimes does not inflate the noise-to-separation ratio —
   it's flat within measurement precision of this small sample (1.93–2.40 vs
   2.32–2.39).
2. **Point support per class is actually better than the thinnest macro regime.**
   Because the severity classes pool across the braking-priority carve-out, each class
   averages ~309 points/driver-weekend (min 153) — comfortably more than
   `fast_corner`'s ~163 average (min 70, well under `property_mixture`'s
   `MIN_COMPONENT_SUPPORT_COUNT=150` floor on a bad weekend). `fast_corner` is
   actually the *worse*-supported bucket of the two schemes being compared.

## Caveats (scoped nulls)

- **n=4 weekends, 6 drivers is small.** These ratios are informative, not a confirmed
  gate — treat this as "no red flag found," not "proven usable."
- **A large, class-independent weekend-to-weekend shift dominates the raw numbers.**
  Austria (R9) shows near-zero/negative deficits across *every* class and every driver
  (e.g. class-mean deficit −2.68 to +1.39 vs Hungary's +2.68 to +5.58 the very next
  round in the sample) — see the round×class pivot in `p2_class_level.csv`. This shift
  is common to all 4 severity classes within a weekend, so it doesn't erode
  *within-weekend* cross-driver or cross-class discrimination, but it means most of the
  "within-driver across-weekend scatter" in the table above is **causal-ceiling /
  circuit-character noise inherited from the macro scheme**, not new noise introduced
  by finer binning. The severity-class split doesn't add a new noise source on top —
  which is itself the reassuring finding — but it also doesn't remove the existing one.
- **This used quantile-bin edges as an explicit proxy for the real k≤4 GMM**
  (`property_mixture.fit_property_mixture`), not the mixture itself. The point-support
  numbers above (~309/driver-weekend, well past `MIN_COMPONENT_SUPPORT_COUNT=150` even
  for a single driver-weekend) suggest an actual GMM fit is affordable at this data
  scale, but that's a different, unrun test.
- **Circuit-composition stability of the class boundaries was not tested.**
  `property_mixture.py`'s own docstring flags this as the reason it fits in log-radius
  space and gates on an "F12 held-out-circuit stability" check; pooling quantile edges
  across all 4 circuits here sidesteps rather than tests that concern.
- Only top-3 constructors were sampled (cleanest/most complete store rows); midfield
  cars were not checked and may have thinner store coverage.
