# Phase 3 — Blessed Fixture Re-bless Proposal (#445, D1)

**Date:** 2026-06-16
**Scope:** Drag-source swap (D1) — `theta_D` now from the full-throttle joint DRS
fit instead of the regen-junk coast fit.
**Decision being implemented:** PHASE0_DRAG_DENSITY_VALIDATION.md §4 / PLAN D1.

## TL;DR — NO RE-BLESS REQUIRED

**None of the three blessed fixtures changed.** All three already used the
longitudinal *fallback* (coast drag was failing the plausibility gate), and they
**continue to use the fallback** under the new throttle drag source — so every
field in all three `blessed_params.json` files is byte-for-byte identical. The
regression suite is green with the untouched blessed files.

This document still exists per the Phase 3 instructions: it records *why* the
fixtures did not move, what the new drag source produces on them, and the
caveat that the swap could not be *validated as an improvement* on these
particular fixtures.

## Per-fixture outcome (old → new)

| Fixture | Old `theta_D` (source) | New `theta_D` (source) | Δ | Changed? |
|---|---|---|---|---|
| spain_2024_fp1_ver | 0.001 (fallback) | 0.001 (fallback) | 0 | **No** |
| monza_2024_fp1_ver | 0.001 (fallback) | 0.001 (fallback) | 0 | **No** |
| monaco_2024_fp1_ver | 0.001 (fallback) | 0.001 (fallback) | 0 | **No** |

`theta_R`, `mean_theta_P`, `A0`, `A2`, lap time, max speed, all uncertainty-budget
fields: **unchanged** in every fixture (fallback path is byte-identical to before).

### Why each fixture stays on fallback under the NEW throttle drag source

The throttle joint DRS fit *runs* (or is correctly declined) on each fixture, but
its result is rejected by the existing post-fit plausibility gate, sending the
fixture back to the fallback `theta_D = 0.001` it already used:

| Fixture | New throttle-fit result | Fallback reason |
|---|---|---|
| spain  | `None` — VER never opened DRS on the captured lap (0 DRS-open samples → no high-speed lever to pin P) | `no_drs_lever` |
| monza  | CdA_closed = **−7.51 m²** (theta_D = −0.00465), P = 2.0 MW | `negative_theta_D` |
| monaco | CdA_closed = **−11.17 m²** (theta_D = −0.00691), P = 1.0 MW | `negative_theta_D` |

A physical F1 CdA is ≈ 1.0–1.5 m² (→ `theta_D ≈ CdA/(2·808) ≈ 0.0006–0.0009`).
The Monza/Monaco fits return *negative* drag area — physically impossible — so the
plausibility gate (`theta_D < 0 → fallback`) correctly discards them.

## ⚠️ Why the negative CdA — flag for human review

The negative-drag fits are **not** a bug in the new joint fit. They are a symptom
of the fixtures' **uncalibrated preprocessor kinematics**. The
`processed_telemetry.parquet` in these regression fixtures contains physically
impossible values at the extremes:

| Fixture | speed p99 / max (km/h) | \|ax\| p99 / max (m/s²) | frac \|ax\|>20 m/s² |
|---|---|---|---|
| spain  | 403 / 454 | 82 / 116 | 37% |
| monza  | 470 / 529 | 141 / 236 | 23% |
| monaco | 381 / 453 | 96 / 156 | 20% |

(F1 reality: top speed ≈ 360 km/h, peak accel ≈ 15 m/s².) The p90 upper-edge
frontier the joint fit uses then latches onto these noise spikes, and the
shared-power term over-explains them, driving the drag coefficient negative.

This is the **calibrated trajectory smoother gap** already noted in the
integration plan (the smoother is a separate, not-yet-integrated piece). The
coast fit *already* fell back on all three fixtures for the same root cause —
junk high-speed kinematics — which is exactly why these fixtures were on fallback
before this change.

### Consequence for D1 validation

- **The drag-source swap is correct and is proven on clean synthetic data** (unit
  tests recover a known CdA → theta_D to <3%, recover power to <5%, and the
  estimator demonstrably takes theta_D from the throttle path, not an inflated
  regen-contaminated coast value).
- **The swap cannot be *demonstrated as an improvement* on these three real
  fixtures** because their preprocessor output is corrupted at exactly the
  high-speed full-throttle region the drag fit relies on. On real, *calibrated*
  telemetry (as produced by the envelope's smoother) the joint fit returns the
  trusted positive CdA — that is the whole basis of D1.
- **Net effect on the blessed snapshots: zero.** The fixtures were on fallback
  before and remain on fallback. No behavior regression; no re-bless.

## What this means going forward

When the calibrated smoother is wired into the `src/physics` pathway (a later
phase), these fixtures should be **regenerated** from calibrated telemetry and
re-blessed *then* — at which point the throttle drag source is expected to
produce a positive, physical `theta_D` and the fixtures will move from fallback
to a real fitted drag. That re-bless is out of scope for Phase 3 (which only
swaps the drag *source*, not the preprocessor).
