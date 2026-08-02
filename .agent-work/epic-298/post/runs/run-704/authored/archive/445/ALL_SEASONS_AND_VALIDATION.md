# #445 — All-seasons drag source + Phase 3 validation gap (2026-06-16)

Two issues surfaced at Phase 3 (drag-source swap). Both are "go back once we're happy" items per the
user; capturing the design + rationale now so the rework is grounded.

## 1. ALL-SEASONS drag source (user requirement)
Phase 3's full-throttle DRS-split drag fit only works in the **DRS era (2011+)** and is only *necessary*
in the **hybrid era (2014+)**. It must not silently fall back (→ default drag) for older seasons.

**Key insight: coast-drag is CLEAN and degeneracy-free PRE-2014.** The reason coast failed (Phase 0)
is the **MGU-K regenerative braking** of the 2014+ hybrid power unit, which harvests aggressively
off-throttle and dominates the coast deceleration. Before 2014 there is no MGU-K: KERS (2009, 2011–13)
harvested under BRAKING, not coasting, so the coast regime (off-throttle, off-brake) is essentially
pure aero + engine braking — exactly what `fit_drag_rolling` assumes. And coast drag is *power-free*,
so it has no P↔CdA degeneracy at all (the reason the engine chose it originally).

**Design = era-aware drag-source selection:**
| era | MGU-K? | DRS? | drag source |
|---|---|---|---|
| ≥ 2014 (hybrid) | yes (coast = regen-junk) | yes | **full-throttle DRS-split** (`fit_drag_throttle`, Phase 3) |
| 2011–2013 (KERS+DRS) | no harvest-on-coast | yes | **coast-drag** (cleaner: power-free, no degeneracy) |
| ≤ 2010 | no hybrid | no DRS | **coast-drag** (the engine's original `fit_drag_rolling`) |

So the coast fit we relegated to "theta_R only" is **NOT dead** — it is the pre-hybrid `theta_D` path.
The rework: add an era/regime selector in `ParameterEstimator` (year-driven, with a graceful fallback
chain: full-throttle-DRS → coast → default), and a sanity cross-check that the chosen source is
physically plausible. The DRS-decode fix (FastF1 code 8 = "available/closed", only 10/12/14 = open),
found in Phase 3, is required for the DRS path in all DRS-era seasons. Validate at the 2013/2014 boundary.

## 2. Phase 3 VALIDATION GAP — blocked on calibrated telemetry
The 3 blessed fixtures (Spain/Monza/Monaco 2024 FP1) **stayed on FALLBACK** under the new drag source —
not because the fit is wrong, but because their `processed_telemetry` is **uncalibrated/corrupted at
high speed** (speeds to 529 km/h, |ax| to 236 m/s²). The joint fit correctly returns negative CdA on
that garbage and the plausibility gate discards it. So `fit_drag_throttle` is **synthetic-validated
only** (recovers known CdA→theta_D to <3%, power <5%); it has had NO real-data validation.

**Implication for sequencing:** the engine's force fits cannot be validated on real sessions until the
**calibrated trajectory smoother** (the envelope's per-session calibration — χ²≈1, Matérn-7/2) feeds the
engine. That is stage 1 of the target pathway and currently absent from the fixtures' input. So:
- The calibration port likely needs to come BEFORE real force-fit validation (consider promoting it).
- The blessed fixtures must be **regenerated from calibrated telemetry** and re-blessed once that lands;
  the current fixtures bless fallback behavior on bad input, which is weak coverage.

## Status of Phase 3
Implemented + unit-tested on synthetic; coast retained for `theta_R`; DRS-decode bug fixed; no fixture
re-bless was needed (all stayed fallback). NOT real-validated. Two follow-ups above before "done".
