# C1 Re-evaluation Verdict — Driver Utilization on the FIXED (physical) Ideal-Lap Simulator

**Issue #518, Gate G6 (HEADLINE gate, re-planned). Epic super-#509 / C1 #510 re-eval.**
Date: 2026-06-25 · Author: g6 implementer crew · Branch: `feat/518-braking-ceiling-reeval`

> **G6 supersedes the G4 verdict.** G4 was run against an **aphysical** ideal lap
> (745 km/h top speed). The G5 units fix (`car_prior` theta_P watts→W/kg, commit
> `df46d840`) made the ideal lap **physical** (top speed now ~333 km/h, drag-limited),
> and this gate re-runs C1 on that fixed sim — the real test of #518's premise. The G4
> verdict is preserved verbatim at `.agent-work/518-braking-ceiling-reeval/VERDICT_G4_prefix.md`;
> its numbers are reproduced below as the pre-fix reference.

---

## TL;DR (per-regime readiness, ON THE FIXED SIM)

| Regime | Verdict (G6, fixed sim) | One-line reason |
|---|---|---|
| **Straight** | **CONTEXTUAL → trending NO-GO** | Now **physical at the source** (ideal top speed 333 km/h, not 745), but the fixed (lower) ideal lap **mildly under-calls** straight speed → `U` rose above 1.0 on all 4 cases (Italy 0.71→**1.07**, GB 0.83→**1.23**). Responds to the fix, but no longer cleanly `<1`. |
| **Slow corner** | **NO-GO** | `U≈1.56–1.89` in both stores; barely moves on recalibration; not separating, not physical. (Slightly **higher** than G4 — the slower ideal lap carries marginally less corner speed.) |
| **Braking** | **NO-GO** | **Still pinned at `U_CLIP_MAX=2.0` in all 4 RBR cases — Δ vs G4 = 0.000.** Raw (unclipped) mean ratio is **~3.3**, essentially unchanged by the top-speed fix. Root cause is the longitudinal **phase/envelope misalignment**, not ceiling height — confirmed unchanged on the physical sim. |
| **Fast corner** | **NO-GO** | **Still pinned at `2.0` in all 4 RBR cases — Δ vs G4 = 0.000.** Raw ratio **~3.8** (`frac≥2.0 = 1.0`). Same structural blocker, the worst-affected regime. |

**Headline answer to the gate's central question (did braking/fast un-clip on the fixed sim?):**
**No.** Making the ideal lap physical (the G5 top-speed fix) did **not** un-clip `u_braking`
or `u_fast_corner`. They remain bit-for-bit at `2.000` (Δ = 0.000 vs the G4 pre-fix run) on
**both** the OLD and the WIRED store. The probe (below) shows why: the clip is driven by a
**~3.3–3.8× longitudinal phase offset** between the ideal and real laps at the shared progress
grid, which the top-speed fix leaves untouched. The #518 G3 braking recalibration **does not
matter** for `u_braking` on the fixed sim (it is clipped) and shifts nothing else materially.

**This confirms — now on a physically correct ideal lap — the G4 diagnosis:** the binding
constraint is the **ideal-lap shape/alignment**, not the braking-frontier depth and not the
sim top speed. The #510 NO-GO on braking/fast-corner **stands**.

This is a **verdict-producing** gate (user-accepted, not GO-guaranteed). The honest call is reported; no GO is forced.

---

## What the G5 fix DID change (and did not)

The G5 fix was real and correct for its target — the **straight / longitudinal** channel:

| Quantity (Italy/VER, WIRED) | G4 pre-fix | G6 post-fix | Change |
|---|---|---|---|
| Ideal-lap top speed | **206.9 m/s (745 km/h)** — aphysical | **92.5 m/s (333 km/h)** — physical | fixed ✔ |
| Ideal-lap min speed | 7.5 m/s | 7.5 m/s | unchanged |
| Straight raw ratio (mean v_real/v_ideal) | <1 (ideal too fast) | **1.080** (ideal mildly too slow) | crossed 1.0 |
| Braking raw ratio | ~3.2 | **3.32** | unchanged |
| Fast-corner raw ratio | ~3.7 | **3.79** | unchanged |

So the fix moved the **straight** regime (the only progress-aligned regime) but left the
**corner-limited** regimes — where the misalignment lives — essentially where they were.

---

## Apples-to-apples three-way comparison (4 RBR/VER cases, both stores, mc_samples=50, seed=42)

Both G6 runs: `scripts/driver_utilization_dashboard.py --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42 --db <store>`,
4/4 ok, 0 errors, single canonical path (`EstimateStore → car_prior.build_car_ceiling →
CapabilityEnvelope → PhysicsSimulator.simulate_lap`), `split_is_impure=True` on every row.
**PRE-FIX columns are the G4 numbers** (aphysical sim), reproduced from `VERDICT_G4_prefix.md`.

| Case | regime | G4 PRE-FIX OLD | G4 PRE-FIX WIRED | **G6 POST-FIX OLD** | **G6 POST-FIX WIRED** | clip? (G6) |
|---|---|---|---|---|---|---|
| **Monaco** | braking | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | slow_corner | 1.644 | 1.615 | 1.675 | 1.645 | >1 |
| | fast_corner | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | straight | 1.196 | 1.183 | 1.288 | 1.276 | >1 |
| **Italy** | braking | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | slow_corner | 1.439 | 1.486 | 1.558 | 1.592 | >1 |
| | fast_corner | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | straight | 0.578 | 0.712 | **1.074** | **1.080** | >1 (was <1) |
| **Great Britain** | braking | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | slow_corner | 1.829 | 1.840 | 1.891 | 1.893 | >1 |
| | fast_corner | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | straight | 0.775 | 0.825 | **1.228** | **1.230** | >1 (was <1) |
| **Singapore** | braking | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | slow_corner | 1.489 | 1.530 | 1.625 | 1.631 | >1 |
| | fast_corner | 2.000 | 2.000 | **2.000** | **2.000** | **CLIPPED** |
| | straight | 0.831 | 0.888 | **1.173** | **1.179** | >1 (was <1) |

**Un-clip statement (the deciding fact):** `u_braking` = 2.000 and `u_fast_corner` = 2.000 in
**4/4** RBR cases on **both** stores, on the **physical** ideal lap. They did **not** un-clip;
the per-case Δ vs G4 is exactly **0.000**. The only regime that moves materially is **straight**
(Italy +0.50, GB +0.45, Singapore +0.34 vs G4-OLD) — but it moves the **wrong way for usability**:
it crosses from `<1` to `>1` (the fixed ideal lap now slightly *under*-calls straight speed).

**OLD vs WIRED on the fixed sim (does #518's braking recalibration now matter?):** **No.**
Per-case OLD↔WIRED deltas are ≤0.04 on every regime, and **0.000** on braking/fast (both clipped).
The G3 wired-braking ceiling produces effectively the same utilization as the OLD #510 ceiling.

CSVs (gitignored): `reports/physics/driver_util_subset_2023.csv` (OLD, fixed sim),
`reports/physics/driver_util_subset_2023__physics_estimates_g3wired.csv` (WIRED, fixed sim).

---

## Why braking/fast still clip on the PHYSICAL sim — root-cause confirmed (probe)

Per-point probe, Italy/VER, fixed sim (raw, **unclipped** mean ratio + frac at-or-over the 2.0 clip):

| regime | n | v_ideal_mean (m/s) | v_real_mean (m/s) | raw ratio | frac(≥2.0) |
|---|---|---|---|---|---|
| braking | 209 | **25.1** | 65.6 | **3.32** | 0.76 |
| slow_corner | 735 | 52.1 | 73.7 | 1.59 | 0.20 |
| fast_corner | 73 | **16.7** | 62.9 | **3.79** | 1.00 |
| straight | 483 | 83.1 | 89.1 | **1.08** | 0.00 |

- **The ideal lap is now physical** (top speed 92.5 m/s / 333 km/h vs the G4 aphysical 206.9 m/s /
  745 km/h). The G5 fix is verified at the source.
- **But in the braking and fast-corner masks the ideal lap is deep in the apex** (`v_ideal ≈ 17–25
  m/s`) while the real lap at the *same grid index* is at `v_real ≈ 63–66 m/s` → a structural
  **3.3–3.8× offset**. The regime mean exceeds the `U_CLIP_MAX=2.0` clip, so `U` pins at 2.0.
- **These corner ratios are unchanged by the fix** (braking 3.23→3.32, fast 3.76→3.79 OLD→WIRED on
  the fixed sim; ~the same as G4). The top-speed fix only touched the longitudinal/straight channel.
- **The straight regime is correctly aligned** (`v_ideal 83 vs v_real 89`, ratio 1.08) — which is
  exactly why it is the only regime that responds to the fix and lands near-physical (just over 1.0).

**Mechanism (unchanged from G4, now confirmed on a physical ideal lap):** a **longitudinal phase /
envelope mismatch** between the canonical ideal lap and the realised lap on the shared progress
grid. The real lap's braking and fast-corner points line up against ideal-lap samples that are deep
in the apex. This is the same failure family documented in `trajectory-smoother-physics-blind` and
the #496 physics-aware-estimator work (braking-knee / phase-lag). **The real unblock is a
phase-aligned / physics-aware ideal-lap comparison (or a per-regime capability-frontier comparison
instead of a point-aligned ideal-lap speed), NOT a deeper braking frontier and NOT the top-speed
fix.** Until then `u_braking` / `u_fast_corner` are not trustworthy.

---

## Honest covariance (lap-sampling σ first-class, from G4 — unchanged)

Each regime reports **two independent uncertainties** plus their quadrature combination:
`sigma_u_*` (envelope σ, MC over car-ceiling params), `sigma_u_lapsampling_*`
(`std(ratio[mask])/sqrt(n)` — the realised lap is a single best lap), and
`sigma_u_total_* = sqrt(env² + lap²)`. Straight-regime total σ (WIRED, fixed sim): Monaco 0.051,
Italy 0.026, GB 0.017, Singapore 0.018 — lap-sampling dominates on short, point-poor straights
(Monaco), envelope dominates where MC spread is wide (Italy). **None of these σ are large enough to
make any regime separate or to lift braking/fast off the clip; the U values themselves drive the
verdict.**

---

## #509 done-done bar

| Criterion | Status |
|---|---|
| Full coverage | **Scoped** — 4 RBR/VER cases (only fully-wired constructor); other 4 = documented continuation (needs wired repop). |
| Honest covariance | **Met** — envelope + lap-sampling σ, separately reportable, combined in quadrature. |
| Single canonical path | **Met** — `EstimateStore → car_prior → CapabilityEnvelope → PhysicsSimulator`; no second inline sim; `split_is_impure=True`. |
| Traceable data → dashboard | **Met** — `--db` selects store; per-store CSV; reproducible (seed=42, mc=50). |
| Physical ideal lap | **Met (G5)** — top speed now drag-limited (333 km/h), verified at source by the probe. |

---

## Caveats

- **Impure split (always):** `split_is_impure=True`; the car ceiling was inferred from sessions
  including the same driver. No separation may be over-claimed — and none is observed.
- **RBR-only scope:** only Red Bull is fully wired in `physics_estimates_g3wired.db` (r1–r15,
  `fitted_at ≥ 2026-06-25`). The other four C1 constructors carry OLD-braking rows and are a
  **documented continuation** (wire their r1–15 before a cross-constructor verdict). The headline
  (braking/fast still clip) is a **method property** and RBR is sufficient to show it.
- **Straight now `>1` everywhere:** the fixed (lower) ideal lap mildly under-calls straight speed,
  pushing all four straight `U` just above 1.0 (1.07–1.29). This is a *new* artifact introduced by
  the fix — it is physical at the source but means straight `U` is no longer cleanly interpretable
  as "fraction of ceiling used." It is a softer issue than the corner clip (ratio 1.08, not 3.3).
- **Lap-sampling σ is additive, not a replacement:** envelope σ math is untouched.

---

## Recommendation

**Overall: NO-GO for the braking and fast-corner regimes; CONTEXTUAL (trending NO-GO) for straight
and slow-corner — on the fixed, physical sim.**

The G5 top-speed fix was **necessary and correct** (the ideal lap is now physical), but it is
**not sufficient** to make driver utilization usable. Braking and fast-corner utilization remain
pinned at the clip because the binding constraint is the **ideal-lap/real-lap longitudinal phase
alignment**, not the ceiling height or the braking-frontier depth — now proven against a physically
correct ideal lap. The #518 G3 braking recalibration **does not change** the C1 verdict on the
fixed sim (OLD ≈ WIRED everywhere; identical on the two clipped regimes).

**Continuation issue recommended:** make the ideal-lap comparison **phase-aligned / physics-aware**
(or compare against a per-regime **capability frontier** rather than a point-aligned ideal-lap
speed), and separately address the new straight-regime under-call (the fixed ideal lap is slightly
slow on straights → `U>1`). Wire the remaining four C1 constructors before any cross-constructor C1
verdict. Until the alignment is fixed, treat `u_braking` / `u_fast_corner` as not trustworthy and
`u_straight` / `u_slow_corner` as directional only.
