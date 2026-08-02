# Reviewer Handoff — G2 Portfolio Exploration (5 spikes)

## Gate
g2-review (work-id 496-physics-aware-estimator, MAIN checkout, branch feat/physics-aware-estimator-496)

## What Was Implemented
Five exploratory worktree spikes (M1/M3/M4/M7/M8), each prototyping one evolutionary mechanism
to recover the sharp braking knee / transients, all measured on the committed G1 scoreboard
(`src/physics/layer2/scoreboard.py`). Consolidated into `SPIKE_COMPARISON.md`. Prototype code
preserved (self-contained) under `.agent-work/496-physics-aware-estimator/spikes/{mX}/`; per-spike
detail in `crew-handoffs/g2-{mX}-result.md`.

## Task Statement
Determine which mechanism(s) actually recover the defect, measured head-to-head on Bahrain (heavy
knee), Monaco (ringing), Belgium (control), and recommend which advance to synthesis. The spikes
are throwaway prototypes; the DELIVERABLE is an honest, reproducible comparison + recommendation.

## The consolidated finding to validate
`SPIKE_COMPARISON.md` claims the defect is TWO distinct problems:
1. **Bahrain knee** = raw-sensor sub-grid bandwidth (the ~5.3 g peak is below the 4 Hz position
   grid). Only **M7** (TV-denoise raw `a_long` → kind=3 onset-sample anchor) recovers it:
   knee −50.27 (gap +1.86; lam=0.1 → +0.31) vs baselines −39.4 (gap +12.7).
2. **Monaco ringing** = 2D position-coupling artifact. Only **M3** (decoupled 1D speed filter)
   fixes it structurally: ring 13.1 → 2.97 (ring_ok). M7 has no leverage there (roc +0.74).
3. **M1/M4/M8 are WEAK** (documented negative results): M1 anchors an AVERAGE model (shallower);
   M4 can't beat the RTS backward-pass rounding of a sub-grid transient; M8 sigmoid fits are
   under-determined on ~3 GPS samples/event (knee −73 artifact).
Recommendation: advance **M7 + M3** as a composing pair; carry M8's positive-accel clip + M4's
onset detector as minor levers; drop M1/M4/M8 standalone.

## Close Criteria (each a review check)
- **Reproduce the two winners' headline numbers.** Run the preserved spike scripts from the MAIN
  checkout (they are self-contained — import the committed scoreboard + their own copied module):
  - `py .agent-work/496-physics-aware-estimator/spikes/m7/run_m7_final.py` (or `run_m7_spike.py`)
    → confirm Bahrain knee ≈ −50 (gap ~+1.9 or better) and that it does NOT regress Belgium badly.
  - `py .agent-work/496-physics-aware-estimator/spikes/m3/run_m3_scoreboard.py`
    → confirm Monaco ring ≈ 3 (ring_ok) and Bahrain unchanged (~−39).
  (Each run loads real sessions — minutes. Spot-checking the two WINNERS is sufficient; you need
  not re-run all five.)
- **The two-problem framing is sound**, not a post-hoc rationalization: the bandwidth argument
  (Bahrain) and the 2D-coupling argument (Monaco) are each corroborated by MORE THAN ONE spike
  (M3+M4 both hit the bandwidth wall; M3's 1D structurally removing ringing). Confirm the logic holds.
- **The weak-mechanism dismissals are FAIR** — read g2-m1/m4/m8-result.md; confirm they failed for
  the stated reasons (not a botched prototype that a fair attempt would rescue). M8 in particular:
  confirm the knee numbers are degenerate-fit artifacts (curve_fit covariance failure), not real.
- **The recommendation is HONEST about the synthesis risk:** neither M7 nor M3 alone passes BOTH
  acceptance circuits; the M7+M3 composition is a HYPOTHESIS G3 must prove. Confirm the comparison
  says this plainly (it should — do not let it oversell).
- **No cherry-picking:** all three circuits reported for every mechanism; failure modes surfaced.

## Allowed Scope
Read the comparison + per-spike results + preserved spike code; re-run the two winners' scripts.
Do NOT modify src/ or land anything — this is a review of an exploration.

## Constraints
`py` launcher; cache at `C:/Programs/f1Brainz/data/telemetry`; no evo import in any spike (spot-check).

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (scoreboard + spike prototypes); `struct:preprocessing.trajectory` (smoother).
- **Decision:** `decision:two_cycle_external_anchor_design` (verify M7's anchor stays raw-derived/un-biased; M1's model-anchor extension is correctly judged the cause of its failure); `decision:smoother_rounds_braking_knee` (the root cause the framing rests on).
- **Evidence:** the two winners' scoreboard numbers reproduce from the preserved code.

## Evidence Produced
Per-spike result files (g2-{mX}-result.md) with scoreboard tables + sweeps; SPIKE_COMPARISON.md.
Re-run the two winners yourself; do not trust the pasted numbers alone.

## Suggested Model Tier
simple-bounded (Sonnet) — verification + targeted re-runs + soundness judgment on a well-documented
exploration.

## Stop Conditions
BLOCK if: a winner's headline number does NOT reproduce (e.g. M7 Bahrain is not actually deepened,
or M3 Monaco ring is not actually fixed); the two-problem framing is contradicted by the data; a
weak mechanism was dismissed unfairly (a fair fix would rescue it); or the recommendation oversells
the unproven synthesis. Otherwise APPROVE.

## Return Format
Return REVIEW_RESULT to `.agent-work/496-physics-aware-estimator/crew-handoffs/g2-review-result.md`
with `verdict: APPROVE` or `verdict: BLOCK`, per-check findings (incl. your re-run numbers for M7
and M3), blockers, out-of-scope observations, and Workflow Feedback.
