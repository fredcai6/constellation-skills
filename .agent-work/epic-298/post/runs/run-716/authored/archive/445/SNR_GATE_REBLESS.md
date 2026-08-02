# #445 — SNR gate + foundation hardening re-bless (2026-06-16)

Implements the identifiability gate for the drag fit, fixes the `_compute_a_long_series`
docstring, and resolves two Phase-3 nits.  Monaco reverts to fallback (correct); Monza
and Spain are byte-identical to the previous bless.

---

## SNR gate: threshold chosen

| fixture | theta_D | theta_D_std | rel-sigma | gate result |
|---|---|---|---|---|
| **Monza** | 0.000627 | 0.000172 | **0.274** | PASS (fit kept) |
| **Monaco** | 0.000148 | 0.000493 | **3.34** | FAIL (fallback triggered) |
| Spain | 0.001 (default) | 0.001 (default) | 1.00 | PASS (already fallback, gate not reached) |

Threshold chosen: **`theta_D_rel_sigma_max = 2.0`**.

Justification: Monza's rel-sigma (0.274) is well below the threshold.  Monaco's
(3.34) is well above it.  The gap is a decade: there is no plausible threshold in
[0.274, 3.34] that would wrongly reject Monza or wrongly keep Monaco.  The default
of 2.0 is conservative on the "reject too aggressively" side (it allows fits with
up to 2x relative uncertainty), while ensuring any fit where 1-sigma spans negative
CdA (rel-sigma > 1) with meaningful margin is rejected.

---

## Monaco `blessed_params.json` — changed fields

All changed fields revert to the pre-a_long-fix (fallback) values.

| field | old (a_long PR bless) | new (SNR gate bless) | why |
|---|---|---|---|
| `theta_D` | 0.0001477 (fitted) | **0.001** (default) | SNR gate rejected (rel-sigma = 3.34 > 2.0) |
| `theta_R` | 0.5 | 0.5 | unchanged (prior) |
| `fallback_longitudinal` | 0.0 | **1.0** | drag fit self-rejected → fallback |
| `fallback_power` | 0.0 | **1.0** | power requires successful drag; falls back too |
| `mean_theta_P` | 531.42 | **300.0** | default (power fallback) |
| `theta_D_std` | 0.000493 (fit σ) | **0.001** (fallback default) | fallback uncertainty |
| `theta_R_std` | 1.0 | 1.0 | unchanged |
| `simulated_lap_time_s` | 100.93 | **112.56** | default drag (0.001 > fitted 0.000148) → slower sim |
| `max_speed_ms` | 84.97 | **58.81** | lower speed cap from lower power + fallback drag |

### Unchanged fields (unchanged from a_long bless)
- `A0`, `A2`, `fallback_lateral`, covariance std fields, `raw_vs_smooth_*` — all
  unaffected by the longitudinal change.

---

## Monza and Spain — byte-identical

Monza: `theta_D = 0.000627`, `theta_D_std = 0.000172`, rel-sigma = 0.274 — well below
the 2.0 threshold.  Monza's fit is kept.  No change to Monza's `blessed_params.json`.

Spain: already on `fallback_longitudinal = 1.0` (no DRS lever).  The SNR gate is not
reached for Spain.  No change.

---

## Stability test skip count

Monaco's 3 stability tests (`test_theta_D_stable`, `test_theta_R_stable`,
`test_mean_theta_P_stable`) skip again because `fallback_longitudinal = 1.0`.  This is
correct: comparing the fallback 0.001 against itself on each run is not a stability
test.  Monza's 3 stability tests continue to run (fitted).

Guardrail suite counts:
- **Before (a_long bless):** 313 passed, 7 skipped
- **After (SNR gate bless):** 314 passed, 10 skipped

Delta: +1 passed (4 new SNR TDD tests), +3 skipped (Monaco stability tests re-skipped).

---

## Other changes in this pass

### a_long docstring fix (segment_classifier.py)

The docstring on `_compute_a_long_series` stated "the caller will use the per-sample
`a·v̂` approximation instead."  The code does NOT do this — it returns zeros.  Corrected
to accurately state: "returns a **zeros array** — `a_longitudinal` will be 0.0 for every
sample" and explains why the old `a·v̂` path was not reinstated (Matérn stationary
variance swamps the signal).  No behavior change.

### Phase-3 nit: DragThrottleFit docstring

Removed the dead `drag_rolling_covariance` attribute entry from `DragThrottleFit`'s
docstring (the field was described but never existed on this dataclass — it lives on
`LongitudinalParameters`).  Added a clarifying Note explaining that the caller
(`ParameterEstimator`) assembles the 2×2 `drag_rolling_covariance` across regimes.

### Phase-3 nit: fallback reason disambiguation

`fit_drag_throttle` now distinguishes two None-returning conditions:
- `"no_drs_lever"` — zero DRS-open frontier bins (the speed lever is genuinely absent).
- `"insufficient_throttle_bins"` — some DRS-open bins exist but total bins < 5 (not
  enough to identify P, CdA_closed, CdA_open jointly).

Previously both mapped to `"no_drs_lever"`.  The distinction is surfaced via an optional
`_out_reason` list parameter (non-breaking; `parameter_estimator.py` passes it and reads
the populated reason).
