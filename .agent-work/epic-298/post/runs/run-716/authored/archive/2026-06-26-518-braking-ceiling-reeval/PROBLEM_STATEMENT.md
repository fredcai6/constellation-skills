# #518 — Problem Statement (consolidated understanding)

**Issue:** Re-evaluate C1 braking/fast-corner driver utilization after ceiling
recalibration. Parent: super-epic #509 (the F→C bridge). Unblocked by #496/#507
(the decoupled longitudinal estimator landed, MEASURED-not-wired).

## Capability being added/changed

The decoupled 1-D longitudinal estimator (`src/physics/layer2/decoupled_longitudinal.py`)
becomes the **canonical longitudinal source** for the physics capability views,
replacing the two legacy longitudinal inputs (`braking_view.clean_longitudinal_from_raw`
raw-speed read for braking; the 2-D smoothed-trajectory `a_long` for the throttle/coast
views). Its deeper, knee-correct braking frontier recalibrates the car-capability ceiling,
which unblocks the C1 driver-utilization re-eval on the braking + fast-corner regimes that
were NO-GO (`U` clipped at the 2.0 ceiling under-call).

## Key technical finding (from map-first recon)

The estimator's natural braking-frontier input is **`F_vehicle/m`** (gravity-free vehicle
force ÷ mass). It replaces BOTH `clean_longitudinal_from_raw`'s `a_long` AND the `−g·sinθ`
gravity term that `BrakingView.fit` currently subtracts by hand (`y = −a_long − drag − θ_R
− g·sinθ`). So "wire the estimator" (comment item 1) and "gravity-corrected F_vehicle
frontier metric" (comment item 3) are ONE piece of work: feeding the gravity-free force IS
the wiring, and it makes the terrain correction fall out for free + carries per-sample
`sigma_a` into the frontier's `sigma_kin`.

## Resolved scope (full program — user-directed, bigger than the focused-core recommendation)

1. **Full-season HP recalibration.** Calibrate the estimator HPs (`tv_lambda`,
   `sig_a_soft_brake`, etc.) across the full 2023-Q season (whole season, per user), not the
   3-circuit VER defaults. HPs are the filter's noise model.
2. **Side-by-side, FIRST substantive gate, gates the wiring.** Fit BrakingView on synthesis
   `F_vehicle` vs `clean_longitudinal_from_raw` `a_long`; compare `(a_b, b_b)` + covariance +
   resulting ceiling. The numbers decide retire/keep. No production wiring on an unratified
   input; no dual-input flag carried forward (one canonical path).
3. **Wire braking canonically** into the braking frontier → capability ceiling (the gravity-free
   F_vehicle input + per-sample σ). Retire `clean_longitudinal_from_raw` if the side-by-side
   ratifies.
4. **Terrain handle on the `CaseInputs` scoreboard seam** (comment item 4): let the scoreboard's
   own self-test exercise the terrain/total-energy path (currently FLAT-only on the scoreboard;
   real terrain is only exercised by the proof driver).
5. **Re-run C1 + verdict + lap-sampling σ.** Run `scripts/driver_utilization_dashboard.py` on
   the recalibrated ceiling; confirm `U_braking`/`U_fast_corner` behaviour; add the deferred
   (#510 G2) lap-sampling σ term to the utilization covariance; produce an updated
   GO/CONTEXTUAL/NO-GO verdict. **Verdict-producing, NOT GO-guaranteed** (user-accepted): the
   deeper knee raises the ceiling (U should fall), but whether U lands ≤1 and separates
   team/driver is empirical.
6. **Characterize the wider views** (Traction / PowerDrag / Coast) on the decoupled `a_long`:
   re-fit each and report how `(CdA, P_max, traction A/B, rolling)` shift vs today — a
   blast-radius report. (#509 characterize-one-at-a-time.)
7. **Full productization (closing step, user-directed).** Wire the wider views onto the
   decoupled `a_long` as the canonical longitudinal source; retire MEASURED-not-wired. **Any
   view the characterization shows REGRESSING is surfaced as a fix-or-hold decision, not blindly
   wired.**

## Protected intent / invariants

- Anchor-source discipline (`decision:two_cycle_external_anchor_design`): the soft-force
  anchor is the TV-denoised RAW `a_long`, never re-read from a smoothed trajectory.
- `constraint:physics_region_no_evo_import` — no evo-region imports.
- Honest covariance first-class (per-sample `sigma_a` propagated, not dropped).
- One canonical execution path (no dual longitudinal inputs left behind).
- Physics evidence at the highest applicable L1–L4 for any model change.
- Decision anchors `decision:decoupled_1d_longitudinal` and `decision:smoother_rounds_braking_knee`
  update from MEASURED-not-wired → wired at the wiring gates.

## Out of scope

- Race-state ideal lap (C2 #511), regime-vector (C3 #512), FP-session fits (C4 #513) — later C children.
- Full process-model replacement (M2/M6) — rejected; only if the 1-D filter fails validation.
- Multi-year calibration — 2023-Q only this run.
