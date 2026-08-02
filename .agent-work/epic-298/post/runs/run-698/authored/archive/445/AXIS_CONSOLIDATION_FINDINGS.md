# #445 — Per-team capability axes: consolidation (2026-06-16)

How independent are the per-car axes built this epic, and which predict quali pace? Spearman across
the 10 teams (`consolidate.py`). Caveat: n=10 → SE≈0.33; treat <~0.5 as within noise.

## Cross-axis Spearman (independence)
```
            apex_pace corner_B   CdA   power brake_Ab brake_Bb
  apex_pace    1.00    0.26    0.31    0.35    0.09    0.20
  corner_B     0.26    1.00    0.10   -0.22   -0.24   -0.28
  CdA          0.31    0.10    1.00    0.55   -0.72    0.41
  power        0.35   -0.22    0.55    1.00   -0.27    0.31
  brake_Ab     0.09   -0.24   -0.72   -0.27    1.00   -0.43
  brake_Bb     0.20   -0.28    0.41    0.31   -0.43    1.00
```
Only strong pair: CdA ~ brake_Ab −0.72 (and brake_Ab isn't pace-relevant). apex_pace is largely
INDEPENDENT of all longitudinal/braking axes (0.09–0.35) — its own dimension. power↔CdA +0.55 is the
known degeneracy leak.

## Vs quali pace
```
  apex_pace  -0.89   ← dominant (leave-one-out validated)
  CdA        -0.50   ← second real axis (straight-line), n=10-marginal but sensible
  power      -0.36   (confounded with drag)
  corner_B   -0.15   character, not pace
  brake_Bb   -0.13   character
  brake_Ab   +0.04   not a quali differentiator
```

## Takeaways
- **Efficient pace core = apex-pace + drag (CdA)** — only +0.31 correlated, so complementary
  (cornering pace ⟂ straight-line). Everything else adds little to PACE.
- **"Capability ceilings aren't pace" — generalized.** Cornering downforce (corner_B), mechanical
  braking (brake_Ab), and downforce-braking (brake_Bb) are real per-car descriptors but ~0 with quali
  pace. The HAA grippy-but-slow paradox is the rule, not the exception: ceilings ≠ pace. Pace = how
  fast you actually take the corner (apex speed) + straight-line drag.
- **Keep the character axes as descriptors, not pace predictors.** Useful for explaining/segmenting
  ("efficient platform", "strong braker") and for the outlier detector, not for the pace model.

## Braking frontier (this session) — `season_brake2.json`, honest covariance σ
- A_b (mechanical braking grip) is poorly identified: braking pts only reach ~99 km/h so the v→0
  intercept is EXTRAPOLATED — covariance σ_Ab ≈ 29% (bootstrap hid it, same lesson as drag), per-fit
  A_b↔B_b corr −0.85. Neither A_b nor B_b resolved per-team (between/SE 1.9, 1.7). One clear signal:
  **FER best braker (1.91 g vs 1.55–1.76 g pack, +2σ)**.
- A_b ⊥ B_b cross-team (−0.17): the −0.85 per-fit degeneracy averages out (direction varies per
  weekend — unlike the consistent power↔drag leak).
- **B_b braking-downforce vs CdA drag +0.29 = distinct aero axes** (downforce-for-braking ≠ drag).

Files: `consolidate.py`, `brake_frontier.py`, `season_brake2_collect.py`, `brake_analysis.py`.

## Ideal lap with uncertainty + the NEXT-LEVEL covariance refinement (2026-06-16)
`ideal_lap_uncertainty.py` — reapply the honest-σ lesson to the capability ceiling: each force carries
its identifiability σ (grip A from `fit_grip_clean` covariance, longitudinal σ_P/P from the joint DRS
fit, real density), JOINT Monte-Carlo the ideal-lap sim so nonlinear coupling (friction circle,
forward-backward speed) shows up, report joint σ vs quadrature σ (gap = interaction). Guards: physical
multiplicative factors + divergence filter (additive grip draws blew the Suzuka sim to σ≈979 s).
Qualitative: cornering-grip σ dominates the ideal-lap band (it's the biggest pace lever).

**NEXT LEVEL (user, to do): sample from the fit COVARIANCE, not independent marginals.** The current
MC perturbs each force independently — which ignores the very degeneracies we measured (P↔CdA +0.78,
A_b↔B_b −0.85, grip A↔B). Fix: draw parameters via multivariate-normal from each fit's full covariance
(we already persist corr_PCc, corrAB; extend to grip A–B and store the cov matrices). WHY it matters:
collinear params co-vary along the degenerate direction, so a joint draw stays on the WELL-DETERMINED
manifold — e.g. a high-P draw is paired with a high-CdA draw, keeping v_max³=2P/ρCdA (top speed, hence
straight-line time) fixed. Independent sampling allows off-manifold draws (high P + low CdA ⇒ impossible
top speed) that SPURIOUSLY inflate the predictive σ. Net: covariance sampling **abates the collinearity
in practice (the observable/ideal-lap is tightly determined) though not in principle (the power/drag
split stays unidentifiable)** — the uncertainty band then reflects what we actually know (the lap), not
the parameter degeneracy. Also model the cross-force physical correlation (lateral grip = braking grip
via the friction circle) as a shared draw rather than independent corner/brake factors.

### DONE — covariance-aware sampling implemented (2026-06-16)
`fit_grip_clean(with_cov=True)` now returns the 2×2 `pcov`; `ideal_lap_uncertainty.py` draws grip
(A,B) jointly via multivariate-normal from it, ties cornering+braking to the same grip draw (friction
circle), longitudinal marginal σ_K. RESULT — **σ_cov is 3–4× tighter than σ_indep** (cov/ind ratio
0.21–0.40, ~16× less variance) at every track, because grip **corrAB ≈ −0.92 to −0.97**: joint
sampling cancels A,B along the degenerate direction and keeps G(v) pinned where measured; independent
sampling lets both wander and balloons G(v). Collinearity abated in practice, not in principle.
- Hungary σ_cov 0.3–0.7 s (was 1.3–3.2), Monza 0.6–1.7 s (was 1.8–7.0), Suzuka 1.5–5.6 s (was 8.9–13.9).
- **OVERTURNS the earlier "σ exceeds team spread → can't rank teams" read — that was an independent-
  sampling artifact.** With covariance draws the band drops BELOW the between-team spread at Hungary
  (σ 0.3–0.7 vs ~1.5 s spread) & Monza → the capability ceiling is RESOLVABLE per-team there. Suzuka
  stays genuinely grip-uncertain (σ≤5.6 s, p5–p95 ~73–91 s) — a real track property, not sampling.
- Still TODO if pushed further: persist per-fit cov matrices to a cache; extend covariance sampling to
  the per-race drag/braking rebuilds (P↔CdA +0.78, A_b↔B_b −0.85) the same way.
