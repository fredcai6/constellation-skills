# Problem Statement — issue #447 (Phase 0b instrument characterization + GO/NO-GO)

## Protected intent (from Admiral launch order, the human's delegate)

Answer the epic's bounded question — **is the FastF1 telemetry correlatable enough to
support trajectory estimation?** — by empirically characterizing the raw instruments and
assembling the GO/NO-GO evidence for the epic's decision point. **Characterization only.
No estimator work.** The Commander RECOMMENDS GO/NO-GO; the human ratifies.

## The bounded question (operationalized at plan)

Over the already-collected FastF1 cache (offline, raw `car_data`/`pos_data` only, never
`get_telemetry()`), characterize per stream and assemble the gate evidence:

1. Sampling-interval distributions per stream (car_data ~240 Hz, pos_data ~10 Hz).
2. Position quantization step; Z-channel quality verdict.
3. Time-tag jitter magnitude + an explicit error model (bias vs random-walk vs per-batch).
4. Inter-stream clock-offset stability per lap / per session (estimable bias vs wander).
5. Per-channel noise covariances.

## Deliverable

`docs/physics/measurement_model.md` — explicit measured numbers, covariances, and an
explicit time-tag error model (the assumption the old estimator had to make). Every number
traceable to a script + session. This document is THE deliverable, not code.

## GO/NO-GO gate (epic decision point — spec's words)

- **GO**: inter-stream offsets estimable AND cross-residuals bounded → Phase 1 estimator
  competition opens.
- **NO-GO**: measurements not mutually constrainable → document why, close the epic's
  estimation phases, redirect to model-side quali gap. A designed outcome, not a failure.
- I operationalize both halves with measured thresholds, SHOW the operationalization
  before applying it, and present marginal as marginal (Honest-Null clause).

## Inherited constraints (pre-rulings, each overridable only with explicit evidence)

1. Never re-pull telemetry — offline cache `C:/Programs/f1Brainz/outputs/cache` only.
2. Raw streams only (`session.car_data[driver]` / `session.pos_data[driver]`).
3. pos_data is in DECIMETRES (confirmed 0a vs Spa length) — ×0.1 for metres everywhere.
4. Reuse the 0a harness (`src/preprocessing/trajectory_grading/`): offline_loader,
   db_truth_loader, cross_residual primitives are the starting point. Extend in place /
   alongside in the physics region; no private forks.
5. Code placement: characterization analysis in `scripts/`; anything shipping in
   `src/preprocessing/`. Never in evo modules.
6. ≥6 sessions, ≥2 seasons (2022–2025 deep cache), mixing race + quali + ≥1 wet/red-flag.
7. The measurement-model document with explicit numbers is the deliverable.
8. Gate framing: GO = offsets estimable AND cross-residuals bounded; operationalize both.
9. Honest NO-GO is a designed outcome; do not rescue a marginal result.

## Three findings from 0a (PR #458) feeding this run directly

- F1: covariance gate band [0.01, 100] too loose (chi-sq 0.60–11.14 all pass);
  tightening toward ~[0.5, 2.0] is the headline calibration task — my measured noise
  model justifies the band.
- F2: cross-residual fitted inter-stream offsets wander per lap (ranges [-0.20,+0.41],
  [-0.23,+0.03], [-0.08,+0.36] s) → quantify jitter vs stable bias, with distributions.
- F3: design call assigned to me — should `s_finish` be a free anchor for circuits with
  ambiguous start/finish-line positions? Decide from evidence and document.

## What is explicitly OUT of scope

- Any estimator / filter / smoother construction (that is Phase 1, gated behind this GO).
- Deciding GO/NO-GO (I recommend; human ratifies via Admiral).
- Crossing data/physics/evo boundaries; scope changes; merging; closing issues.

## Interrogation note (workflow misfit, surfaced per skill)

The spine's `understand` step prescribes loading the Interrogator to reach the human. In a
dispatched Constellation Commander run the only human-reachable party is the Admiral, who
has already resolved scope, framing, pre-rulings, and the three findings in an exhaustive
launch order. There is no open ambiguity that a live interrogation would settle — the
remaining judgment calls (session selection, chi-square band, `s_finish` design) are
explicitly delegated to my latitude and resolved from EVIDENCE, not from asking. Closest
compliant action: consolidate the launch order into this confirmed problem statement and
treat it as the protected intent. Genuinely scope-affecting discoveries will be floated
back as `user-decision` returns to the Admiral.
