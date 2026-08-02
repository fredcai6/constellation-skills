# C1 Re-evaluation Verdict — Driver Utilization on the Recalibrated (Wired) Ceiling

**Issue #518, Gate G4 (headline gate). Epic super-#509 / C1 #510 re-eval.**
Date: 2026-06-25 · Author: g4 implementer crew · Branch: `feat/518-braking-ceiling-reeval`

---

## TL;DR (per-regime readiness)

| Regime | Verdict | One-line reason |
|---|---|---|
| **Straight** | **CONTEXTUAL** | Responds to recalibration, physical (`U<1` on power tracks), but Monaco still `>1` (short-straight/DRS lever-arm artifact). |
| **Slow corner** | **NO-GO** | `U≈1.4–1.8` in both stores; barely moves on recalibration; not separating, not physical. |
| **Braking** | **NO-GO** | **Still pinned at the `U_CLIP_MAX=2.0` clip in all 4 RBR cases — delta 0.000.** Root cause is structural (ideal-lap shape/alignment), not braking-frontier depth. The recalibration the gate was built to test does NOT un-clip it. |
| **Fast corner** | **NO-GO** | **Still pinned at `2.0` in all 4 RBR cases — delta 0.000.** Same structural blocker as braking. |

**Headline answer to the gate's central question:** No. On the recalibrated (G3 wired-braking)
ceiling, `u_braking` and `u_fast_corner` **do not un-clip** from `2.0` — they are bit-for-bit
unchanged (Δ = 0.000) versus the OLD #510 ceiling. The #510 NO-GO on those two regimes **stands**,
and the diagnosis below shows why a deeper braking ceiling alone could never have fixed it.

This is a **verdict-producing** gate (user-accepted, not GO-guaranteed). The honest call is reported.

---

## Wired scope (read this first)

Only **Red Bull Racing is fully wired** in the new store `data/physics_estimates_g3wired.db`
(rounds r1–r15, full causal history, `fitted_at ≥ 2026-06-25T10:13`). Verified:

- RBR: **15** rows `fitted_at ≥ 2026-06-25` (r1 Bahrain … r15 Singapore — covers all four dashboard circuits: Monaco r6, Great Britain r10, Italy r14, Singapore r15).
- Ferrari, Mercedes: **1** stray `2026-06-25` Bahrain row each (continuation repop did not finish). **Ignored** per Commander scope.
- The other 7 constructors carry only OLD-braking rows (`2026-06-20`).

**The verdict is therefore scoped to the 4 RBR/VER dashboard cases** — the primary C1 reference,
all four dashboard circuits. The other four C1 constructors (Ferrari/McLaren/Williams/Mercedes)
are a **documented continuation**: they must be wired (their r1–15 repopulated) before their cases
reflect the recalibration. Running them now would compare an OLD-braking ceiling and is omitted by
design. This scoping does **not** soften the headline: braking/fast un-clipping is a property of the
*method*, and RBR (fully wired) is sufficient to show the method still clips.

---

## Apples-to-apples comparison (4 RBR/VER cases, both stores, mc_samples=50, seed=42)

Both runs: `scripts/driver_utilization_dashboard.py --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42`, 4/4 ok, 0 errors, single canonical path
(`EstimateStore → car_prior.build_car_ceiling → CapabilityEnvelope → PhysicsSimulator.simulate_lap`),
`split_is_impure=True` on every row.

| Case | regime | OLD U | NEW U | Δ | clip? |
|---|---|---|---|---|---|
| **Monaco** | braking | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | slow_corner | 1.644 | 1.615 | −0.029 | >1 |
| | fast_corner | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | straight | 1.196 | 1.183 | −0.013 | >1 (DRS artifact) |
| **Italy** | braking | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | slow_corner | 1.439 | 1.486 | +0.047 | >1 |
| | fast_corner | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | straight | 0.578 | **0.712** | **+0.134** | physical (<1) |
| **Great Britain** | braking | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | slow_corner | 1.829 | 1.840 | +0.011 | >1 |
| | fast_corner | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | straight | 0.775 | 0.825 | +0.050 | physical (<1) |
| **Singapore** | braking | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | slow_corner | 1.489 | 1.530 | +0.041 | >1 |
| | fast_corner | 2.000 | 2.000 | +0.000 | **CLIPPED** |
| | straight | 0.831 | 0.888 | +0.058 | physical (<1) |

**Un-clip statement (the deciding fact):** `u_braking` = 2.000 and `u_fast_corner` = 2.000 in
**4/4** RBR cases on BOTH the OLD and the WIRED store. They did **not** un-clip; the per-case deltas
are exactly 0.000. The only regime that moves materially is **straight** (Italy +0.134, GB +0.050,
Singapore +0.058) — and it stays physical (`U<1`) on the three power/mixed tracks.

CSVs (gitignored): `reports/physics/driver_util_subset_2023.csv` (OLD),
`reports/physics/driver_util_subset_2023__physics_estimates_g3wired.csv` (WIRED).

---

## Why braking/fast_corner clip — root-cause diagnosis (not a depth problem)

The clip is **not** caused by the braking frontier being too shallow, so recalibrating its depth
(the whole premise of #518 G1–G3) cannot fix it. Probing Italy/VER per-point on the wired store:

- **The ideal lap is mis-shaped and mis-aligned vs the real lap.** Ideal-lap speed envelope = `[7.5,
  206.9] m/s` (745 km/h top speed is **aphysical**), vs real `[20.8, 95.3] m/s`. The simulator ideal
  lap brakes deeper/later and reaches impossible straight speeds.
- **In the real-braking mask, the ideal lap is already at the apex.** Mean `v_ideal ≈ 25.1 m/s` while
  mean `v_real ≈ 65.6 m/s` at the *same grid index* → per-point ratio `v_real/v_ideal ≈ 2.5–3.7`,
  with `frac(ratio ≥ 2.0) = 0.73–1.0`. The regime mean is pinned at the `U_CLIP_MAX=2.0` clip.
- **Fast corner is worse:** mean `v_ideal ≈ 16.7 m/s` vs `v_real ≈ 62.9 m/s` (ratio ≈ 3.7,
  `frac ≥ 2.0 = 1.0`).
- Recalibration moved the braking ceiling the *wrong* way for this metric here (braking-mask
  `v_ideal` 27.5 → 25.1 m/s) and is swamped by the ~2.5–3.7× structural offset.

**Mechanism:** a **longitudinal phase / envelope mismatch** between the canonical ideal lap and the
realised lap on the shared progress grid — the braking and corner points of the real lap line up
against ideal-lap samples that are deep in the apex. This is the same family of failure documented in
the trajectory-smoother-physics-blind and #496 physics-aware-estimator work (the braking-knee /
phase-lag problem). **The real unblock is fixing the ideal-lap shape/alignment (a physics-aware
ideal-lap or a phase-aligned regime comparison), NOT a deeper braking frontier.** Until then,
`u_braking`/`u_fast_corner` are not trustworthy regardless of ceiling recalibration.

The **straight** regime is correctly aligned (the real and ideal laps are both near-flat-out there),
which is why it is the only regime that responds to the recalibration and lands physical.

---

## Honest covariance (lap-sampling σ now first-class)

The deferred #510 G2 hook is resolved. Each regime now reports **two independent uncertainties** plus
their honest quadrature combination, all separately reportable:

- `sigma_u_*` — **envelope** σ (car-ceiling parameter covariance via MC), **unchanged** by this gate.
- `sigma_u_lapsampling_*` — **lap-sampling** σ = `std(ratio[mask]) / sqrt(n_points)` (the realised lap
  is a single best lap, so each U_r is a sample mean; this is its standard error). **New.**
- `sigma_u_total_*` = `sqrt(envelope² + lapsampling²)` (a `None` component counts as zero). **New.**

Straight-regime σ (WIRED): Monaco env 0.005 / lap 0.056 / **total 0.056**; Italy env 0.021 / lap 0.010
/ **total 0.023**; GB env 0.007 / lap 0.024 / **total 0.025**; Singapore env 0.011 / lap 0.029 /
**total 0.031**. Lap-sampling dominates on the short, point-poor straights (Monaco), envelope
dominates where MC spread is wide (Italy) — exactly the honest behaviour expected. None of these σ are
large enough to make any regime separate; **the U values themselves, not their uncertainty, drive the
verdict.**

---

## #509 done-done bar

| Criterion | Status |
|---|---|
| Full coverage | **Scoped** — 4 RBR/VER cases (only fully-wired constructor); other 4 = documented continuation. |
| Honest covariance | **Met** — envelope + lap-sampling σ, separately reportable, combined in quadrature. |
| Single canonical path | **Met** — `EstimateStore → car_prior → CapabilityEnvelope → PhysicsSimulator`; no second inline sim; `split_is_impure=True`. |
| Traceable data → dashboard | **Met** — `--db` selects store; per-store CSV; reproducible (seed=42, mc=50). |

---

## Caveats

- **Impure split (always):** the car ceiling was inferred from sessions that include the same driver;
  `split_is_impure=True`. No separation may be over-claimed — and none is observed here.
- **RBR-only scope:** the verdict's generality to other constructors is **unverified**; their cases
  need the wired repop first. Headline (braking/fast still clip) is a method property and holds on RBR.
- **Lap-sampling σ is additive, not a replacement:** envelope σ math is untouched and still reported.
- **Monaco straight `U>1`** is a known short-straight / DRS lever-arm artifact, not a real over-ceiling.

---

## Recommendation

**Overall: CONTEXTUAL, trending NO-GO for the corner/braking regimes.** Straight-line utilization is
usable today (physical, recalibration-responsive). Braking and fast-corner utilization are **not
ready** and are **not unblocked by ceiling recalibration** — the binding constraint is the ideal-lap
shape/alignment (aphysical top speed + longitudinal phase mismatch). Recommend a continuation issue to
make the ideal-lap comparison physics-aware / phase-aligned (or to compare against a per-regime
capability frontier rather than a point-aligned ideal-lap speed), and to wire the remaining four C1
constructors before a cross-constructor C1 verdict.
