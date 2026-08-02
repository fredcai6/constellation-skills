# G2 Spike Comparison — #496/#507 Filter-Rebuild Portfolio

**Date:** 2026-06-24 · 5 parallel worktree spikes (Sonnet) on the common G1 scoreboard
(Bahrain T1 heavy stop / Monaco short-straight ringing / Belgium-Spa control, 2023 Q VER).
Raw-sensor targets: Bahrain knee **−52.13**, Monaco ring ceiling **+5.64**, Belgium knee **−38.84**.

## Headline finding: the defect is TWO different problems with two different root causes

| Problem | Root cause (spike-confirmed) | What fixes it | What does NOT |
|---|---|---|---|
| **Bahrain heavy-braking under-read** (knee −39 vs raw −52) | the real ~5.3 g peak is a sub-grid transient: it lives in the raw speed sensor (~18 Hz) but is averaged below the 4 Hz position-grid bandwidth. ANY mechanism on the gridded `inp.v` loses it. | **M7** — TV-denoise the RAW `a_long` and anchor the ONSET SAMPLE via kind=3 (the raw value carries the peak). | M3, M4 (gridded-speed bandwidth limit); M1 (anchors an AVERAGE model → shallower); M8 (degenerate fit). |
| **Monaco non-throttle ringing** (+13 vs +5.6 ceiling) | a 2D position-coupling artifact: corner-entry bleeds into braking transitions in the Matérn position smoother. | **M3** — a decoupled 1D speed filter has no 2D coupling to ring (13.1 → 2.97, ring_ok YES). | M7 (no leverage — ringing is not in the braking arc); M4 (process-noise gating worsens it). |

**These two compose.** A **decoupled 1D physics-constrained longitudinal filter (M3) fed by the
TV-denoised raw-onset anchor (M7)** gives, in ONE estimator: no 2D ringing (Monaco) + deep-knee
recovery (Bahrain). That is the synthesis candidate for G3.

## Per-spike scoreboard (knee m/s²; gap = knee − raw_knee, toward 0 is better)

| Mechanism | Bahrain knee (gap) | Monaco ring (roc) | Belgium knee (gap) | Verdict |
|---|---|---|---|---|
| **baseline gaussian** | −39.50 (+12.63) | +13.14 (+7.50) ✗ | −34.93 (+3.91) ✓ | — |
| **baseline kind3** | −39.42 (+12.71) | +13.38 (+7.73) ✗ | −37.41 (+1.43) ✓ | the bar to beat |
| **M7** raw-denoise→onset anchor | **−50.27 (+1.86)**; lam=0.1 → **+0.31** | +6.38 (+0.74) ✗ | −36.79 (+2.05) ~ | **PROMISING (Bahrain win)** |
| **M3** decoupled 1D filter | −39.49 (+12.6, no change) | **+2.97 ring_ok ✓** | −37.32 (matches kind3) ✓ | **PROMISING (Monaco win)** |
| **M4** regime-gated proc-noise | −39.52 (+12.61, no change) | +13.38 (no help/worse) | −36.98 (+1.86) | WEAK |
| **M1** model-shape onset anchor | −36.86…−37.69 (WORSE) | only loose passes (incidental) | artifact (−22, impossible) | WEAK |
| **M8** semi-parametric onset mean | −73.72 (degenerate over-deepen) | −3.43 (ring_ok via min()-clip) | −64.78 (artifact) | WEAK |

### Why the three weak ones failed (useful negative results)
- **M1** anchors to a frontier MODEL `a_b+b_b·v²` = average braking capability (~37–39), so it pulls
  the trajectory AWAY from the −52 peak. Lesson: the Bahrain anchor VALUE must be the raw-sample
  peak, not a model. (Confirms M7's design.) Full-arc placement over-anchors.
- **M4** process-noise inflation cannot beat the RTS backward pass rounding a 1–2-sample knee; it is
  a forward-step knob on a smoothing problem. Best config only avoids Monaco regression, no Bahrain gain.
- **M8** sigmoid mean is under-determined on ~3 GPS samples/event at 4 Hz (`curve_fit` covariance
  could not be estimated; knee = −73…−80 artifacts). Conceptually sound but needs ≥10 Hz car
  telemetry — that is a different data path, out of this evolutionary scope.

## Reusable minor levers (ride-alongs for synthesis, not standalone)
- **M8's `min()` positive-accel safety clip** — validly clips spurious positive `a_long` in
  non-throttle (a cheap ringing guard; genuine, not the artifact part).
- **M4's onset detection** (regime-transition ∪ `dv/dt` threshold) — a clean onset locator the
  anchor placement can reuse.
- **M7's edge=0 onset-sample rule** — the raw −52 peak is the FIRST sample of each braking run; any
  trim margin > 0 discards it. Critical implementation detail for G3.

## Invariant-extension surface (decision:two_cycle_external_anchor_design)
- **M7** is the most invariant-faithful: anchor derived from RAW speed (TV-denoised, edge-preserving),
  never from a smoothed trajectory; extends placement (onset sample, not plateau-only). Justified.
- **M1** extends anchor VALUE to a model — and that is exactly why it fails. Argues AGAINST model anchors.
- The synthesis (M7+M3) keeps the anchor raw-derived and moves the longitudinal estimate to a 1D
  decoupled filter → a NEW decision candidate: **"longitudinal `a_long` comes from a decoupled 1D
  physics filter fed by the raw-onset anchor, not the 2D position smoother"** (aligns with
  `decision:smoother_rounds_braking_knee`: speed is the only good longitudinal observable).

## Recommendation to the human (g2-integrate decision)
- **Advance M7 + M3 as the synthesis pair** — they solve the two distinct problems and compose into
  one decoupled-longitudinal estimator with a raw-onset anchor. G3 builds this combination.
- **Carry M8's positive-accel clip + M4's onset detector** as minor ride-along levers.
- **Drop M1, M4, M8 as standalone** (kept as documented negative results; M8 revival needs ≥10 Hz
  telemetry — a separate future path, not this evolutionary step).
- Honest caveat: M7 alone leaves Monaco ringing at roc +0.74 (still just over ceiling); M3 alone
  can't deepen Bahrain. Neither single mechanism passes BOTH #507 acceptance circuits — the
  COMBINATION is the bet, and G3 must prove M7+M3 actually composes (the synthesis risk).

Spike prototype code preserved: `.agent-work/496-physics-aware-estimator/spikes/{m1,m3,m4,m7,m8}/`.
Per-spike detail: `crew-handoffs/g2-{m1,m3,m4,m7,m8}-result.md`.
