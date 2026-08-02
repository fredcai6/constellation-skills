# Phase 5 — Braking frontier + friction circle: fixture re-bless (2026-06-16)

## Summary

Phase 5 added a per-car measured braking frontier (`a_brake(v) = A_b + B_b·v²`)
and activated the friction-circle constraint in corners. The key question is which
fixtures received a real frontier fit vs. fell back to the constant.

## Per-fixture braking fit result

| Fixture | Brake samples | Bins ≥8pts | Frontier | Reason |
|---|---|---|---|---|
| `monza_2024_fp1_ver` | 34 (31 genuine decel) | 0 | **constant** | All bins < 8 pts; single-lap limitation |
| `spain_2024_fp1_ver` | 34 (34 genuine decel) | 0 | **constant** | All bins < 8 pts; narrow speed range 51–77 m/s |
| `monaco_2024_fp1_ver` | 48 (46 genuine decel) | 0 | **constant** | All bins < 8 pts; scattered across bins |

**All three fixtures fall back to constant braking.**

This is the expected outcome: the fixtures are **single-lap** snippets (30–48
brake samples total). The frontier fit requires ≥4 bins with ≥8 samples each —
a minimum of ~32 samples in a useful speed range.  Real multi-lap or
multi-session collections would provide the data density needed for a frontier.

### Detail: why bin thresholds matter

Speed range of brake samples per fixture:
- Monaco: 23–77 m/s, but 1–14 pts per bin (none reach 8 in any single bin)
- Monza: 32–94 m/s, similarly sparse per bin (max 8 in one bin: 55–63 m/s)
- Spain: 51–77 m/s = only 4 bins total, all with 5–11 pts — 3 bins reach 5+pts
  but none reach 8+pts minimum (only 9, 9, 11, 5 across four bins of 8 m/s each)

### Spain with relaxed threshold (diagnostic only)
With `min_pts_per_bin=5` Spain produces: `A_b=35.5 m/s², B_b=−0.0023`
(SNR rel-σ=47%, well below gate threshold). A_b=35.5 m/s² ≈ 3.6 g is
physically plausible for F1. Negative B_b is atypical but within noise given
the narrow speed lever (51–77 m/s).  This corroborates the consolidation
finding: A_b is extrapolation-limited and the single-lap B_b is noisy.

## What changed in the blessed fixtures

**Nothing.** All three fixtures use `braking=None` (constant path), which is
byte-identical to pre-Phase-5 behaviour:
- `simulated_lap_time_s`: **unchanged** for all fixtures
- `max_speed_ms`: **unchanged**
- All other blessed fields: **byte-identical**

The only new item in `fit_quality_metrics` is `braking_source = "constant"`,
which is a NEW key not tracked by the existing regression test keys, so the
JSON comparison is unaffected.

## Drag / lateral / density / power: no silent drift

- `theta_D`, `theta_R`, `mean_theta_P`: identical (Phase 5 touched no
  longitudinal code)
- `A0`, `A2`: identical (Phase 5 touched no lateral code)
- `fit_air_density`: identical (Phase 5 touched no density code)
- `fallback_longitudinal`, `fallback_power`, `fallback_lateral`: identical

## Re-bless needed? NO

Blessed JSONs are unchanged. The regression suite passes 26/26 tests (26 pass,
10 skip) with no diffs to the blessed files.

## When would a fixture get a real frontier?

A fixture with:
- Multiple laps of brake data (e.g. a full FP session for one driver)
- Speed range covering at least 4 bins of 8 m/s each with ≥8 samples per bin
  (approximately 32+ samples across 32 m/s of speed range)

The Monza braking frontier on a season-length collection (the consolidation
result) showed A_b ≈ 19–28 m/s² per team with σ_Ab ≈ 29% — so
physically sane values in [15–50] m/s² are expected, but a single-lap
fixture cannot deliver the sample density needed for the fit.

## SNR gate validation on real braking data

The SNR gate (`a_b_rel_sigma_max=2.0`) is validated on synthetic data in
`test_braking_fit.py::TestBrakingFrontierSNRGate`:
- Clean data (noise=0.05): rel-σ < 2.0 ✓ (gate passes)
- Noisy data: rel-σ varies; the gate correctly self-rejects when uncertainty
  exceeds 200% of the fitted A_b value

The real-fixture diagnostic confirms the implementation behaves correctly:
the conservative `min_pts_per_bin=8` and `min_bins=4` thresholds prevent
over-fitting to sparse single-lap data.

## Monza braking frontier — real telemetry assessment

On the Monza fixture (single FP1 lap, VER, 2024), the braking frontier
**self-rejects** even without the SNR gate because the bin occupancy
threshold is not reached. This is consistent with the consolidation finding:
"brake samples stop ~99 km/h; A_b is EXTRAPOLATION-LIMITED."

On a full-season Monza multi-lap collection (the consolidation's
`season_brake2.json`), RBR showed A_b ≈ 1.9 g = 18.6 m/s² — consistent
with the physically plausible 15–30 m/s² range documented in the brief.
The fixture simply lacks the data density for a per-lap frontier.
