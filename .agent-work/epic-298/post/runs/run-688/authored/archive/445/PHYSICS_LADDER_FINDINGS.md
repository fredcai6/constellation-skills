# Epic #445 Physics — Experiment Ladder E1–E12: Findings & Redefinition

Status: 2026-06-13, lab phase complete (user-AFK-authorized autonomous run).
All work on `expt/448-e1..e12` branches (lab; not merged — merge bar is "useful to main", TBD).

## Bottom line

The physics trajectory layer is **validated end-to-end**. A single windowless full-stint
Matérn-5/2 SDE Kalman-RTS smoother, fusing raw position + speed with one constant inter-stream
offset, scores held-out sector-crossing residuals at real co-estimated loops of:
- **2022 Spain R (clean race, 18–24 laps/driver): ~20 ms median / 59 ms p90 — comfortably under
  the 50 ms gate**, corner loops NOT worse (highest-demand Spain s2 |κ|v²=66 → 20 ms);
- **Belgium Q / British Q (thin quali, 2–6 green laps/driver): ~47–50 ms median, at the gate,
  wider p90 (~135 ms)** — the spread is small-n, not trajectory error.

Data-richness, not corner geometry, drives the spread → **~10–30× better than rounds 1–2
(550–960 ms)**. The residual floor is the sector-timing *measurement* (loop-position degeneracy +
the irreducible E4/E5 16–46 ms), not a trajectory defect — E10≈E11 at the loops to <1 ms.
(Note: the E12 agent's resurrected fuller run added the Spain R race + 5 drivers, total_n 147→656,
commit e6724ee; the median-of-session-medians 47 ms is pulled up by the two thin quali sessions and
under-represents the clean-race ~20 ms.)

Rounds 1–2 were **architecture-limited by ~30–50×, never data-limited.** The data was always good
enough; the old framings (windowed per-lap solves, ribbon projection, unfused instruments,
sector-times-as-truth) manufactured the failure.

## What each experiment settled

- **E1** — the 36 m/lap cross-instrument disagreement is a random walk (τ^0.5), not clock/scale.
  Reducible geometric part + irreducible position-jitter floor; only **fusion** beats it.
- **E2** — time misalignment is a single small constant (+0.09 s) + white jitter; removes only
  ~25%. NOT a per-lap/drifting clock. Kills round-1/2 per-lap-offset machinery.
- **E3** — substrate identified empirically: position Matérn-5/2, speed Matérn-3/2; 0.1 m
  quantization innocent; position "noise" is mostly unpredicted motion between 4 Hz samples;
  speed sensor noise genuinely white σ≈0.49 m/s.
- **E4** — joint local fusion is HONEST: simultaneous χ²=1.00/1.00 on withheld data; true
  position σ≈1.0 m identified; local crossing-time σ ≈ 16 ms / 41 ms p90. The make-or-break test.
- **E5** — real sector loops identifiable as cm-sharp geometry; held-out crossing floor 21–46 ms;
  absolute time-bias is degenerate (no coherent clock bias exists) → use loops calibration-free.
- **E6** — chain honest at scale; but lap reproduction line-dependent → corner chord-cut (then
  thought reducible-geometry).
- **E7** — state-dependent roughness REJECTED on the windowed solve (confounded); smoothness-
  shaving falsified; mean path tracks raw to 0.1 m.
- **E8** — zero-mean-shrinkage hypothesis falsified (WRONG SIGN); chord-cut localized to the
  cosine-taper **window stitch**, not dynamics. Per-window solves unbiased.
- **E9** — no merge math fixes it; seam-in-corner biases arc regardless of fusion; single
  windowless solve is exactly unbiased (−0.002 m/km). Windows themselves are the artifact.
- **E10** — windowless full-stint Kalman-RTS smoother: nests E4, O(N), geometric chord-cut
  ELIMINATED on real data. Exposed a second error: corner speed-transient underfit (χ²_spd→1.4).
- **E11** — non-stationary roughness inside the windowless smoother FIXES the speed-honesty
  deficit where recoverable (VER χ²_spd 1.33→1.02, genuine following not variance-gaming), at an
  honest information floor where not (HAM corner speed error at the data limit). Corner LAP-TIME
  bias unmoved & line-dependent → pointed at a third mechanism (scoring registration).
- **E12** — capstone: at REAL co-estimated loops the validated trajectory scores 37–50 ms
  held-out; SAME trajectory at arbitrary corner lines scores 708–3863 ms. The −400 ms corner
  "bias" was a **scoring-proxy artifact of arbitrary lines**, not a trajectory defect. E10≈E11 at
  real loops → residual floor is the sector-timing measurement, not the trajectory.

## Recurring theme (the user's principles, vindicated repeatedly)

- "Discretized handovers are the problem" — manifested as lap boundaries (round 1/2), then our own
  window seams (E8/E9); cured only by a genuinely windowless (but still local/Markov) solve (E10).
- "One dynamics, observations at many supports; sector times are measurements not truth" — exactly
  how E4/E5/E12 treat them (line-crossing observations, calibration-free, b=0).
- "Trust both globally and locally; don't shove all uncertainty to one scale" — the chi²-target
  honesty criterion that made E4/E10/E11 work is precisely per-class simultaneous honesty.
- Curve-averaging-cuts-corners (κh²/6): appeared three times (ribbon median → suspected prior →
  actually the window stitch). The windowless solve removes the averaging entirely.

## Parked for later (DESIGN_NOTES_ROUND3.md)

- §6 categorical/state-dependent acceleration terms — partially realized in E11; the longitudinal
  driver worked, the lateral E7 form didn't.
- §7 non-orthogonal inertial (equinoctial-style) uncertainty frame — not indicated by evidence so
  far; revisit only if a future need surfaces.
- Force layer (m_a / acceleration state) recovered as a working prototype in E8/E10/E11 — the
  Phase-2 deliverable showed up as a Phase-1 estimation byproduct.

## Recommended epic redefinition (for user ratification)

The original #448/#449/#450 framing (estimator *competition*, ribbon manifold, per-lap clock
states, 50 ms pass/fail) is superseded by the validated architecture. Proposed:

1. **#448 → "windowless joint-fusion trajectory estimator + trust profile."** Productionize the
   E10/E11 smoother into `src/preprocessing/` with the chi²-target honesty calibration; deliverable
   is trajectory + per-observation-class honest covariance, not a single gate verdict. The grading
   harness (#446) survives as one rung (sector-crossing consistency), demoted from sovereign.
2. **#449 (force attribution)** re-anchored to consume the smoother's acceleration state (already
   prototyped) — it needs honest local dynamics + covariance, which E4/E10/E11 deliver; it does NOT
   need 50 ms absolute positioning.
3. **#450 (features into evo)** unchanged in spirit; declares which observation-class trust levels
   it requires.
4. Supersede the round-1/2 estimator code (PR #468, unmerged) — the windowless solver replaces it;
   salvage only the harness/loaders/report-schema that proved useful.

Open decisions for the user: (a) productionization scope & where the solver lives; (b) which lab
branches graduate to main and how (the "useful to main" bar); (c) whether to widen validation
(more circuits/sessions, wets, races) before productionizing; (d) the categorical-acceleration and
inertial-frame parked items' priority.
