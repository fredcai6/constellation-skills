# G2 M1 Spike Result — Model-shape Onset Anchor

**Date:** 2026-06-24
**Branch:** worktree off feat/physics-aware-estimator-496
**Prototype:** `spikes/m1/variant_m1.py` + `spikes/m1/run_m1_scoreboard.py`

---

## Mechanism Summary

M1 extends the #498 kind=3 plateau anchor by anchoring the **full braking arc** (not just plateau) with anchor values derived from a per-lap braking frontier model `a_model(v) = -(a_b + b_b * v^2)` fit from RAW `a_long_raw` samples. The model is fit via speed-binned upper-quantile (p=0.85) OLS. Two-cycle structure mirrors `refine_trajectory`: cycle-1 Student-t jerk prior (nu_proc=4.0) provides heading (vx, vy); cycle-2 applies an `AccelObs` (kind=3) over all brake-regime samples with the model-predicted decel as the anchor value. Three sigma variants tested: 0.5 (tight), 1.0 (moderate), 2.0 (loose).

---

## Scoreboard Table

All values in m/s^2. knee_gap: positive = shallower than raw (WORSE). ring_over: positive = above raw ceiling (WORSE).

| Circuit | Lap | n_brake | raw_knee | gaussian_knee | kind3_knee | m1_tight_knee | m1_mod_knee | m1_loose_knee |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bahrain | 14 | 18 | -52.13 | -39.50 | -39.42 | -37.69 | -36.94 | -36.86 |
| Monaco | 29 | 21 | -37.51 | -38.07 | -37.60 | -38.83 | -38.51 | -38.04 |
| Belgium | 21 | 22 | -38.84 | -34.93 | -37.41 | -34.92 | -33.55 | -36.74 |

### Ringing (non-throttle max a_long, m/s^2)

| Circuit | raw_ring | gaussian | kind3 | m1_tight | m1_mod | m1_loose |
| --- | --- | --- | --- | --- | --- | --- |
| Bahrain | -2.86 | +0.46 FAIL | +0.41 FAIL | -13.40 PASS | -14.91 PASS | -16.78 PASS |
| Monaco | +5.64 | +13.14 FAIL | +13.38 FAIL | +13.67 FAIL | +12.10 FAIL | -1.52 PASS |
| Belgium | +4.57 | +4.36 PASS | +4.44 PASS | -23.52 PASS* | -22.74 PASS* | -0.15 PASS |

(*) Belgium PASS on ringing is an artifact - see failure modes.

### Knee Gap (knee minus raw_knee; positive = under-reads decel)

| Circuit | gaussian | kind3 | m1_tight | m1_mod | m1_loose |
| --- | --- | --- | --- | --- | --- |
| Bahrain | +12.63 | +12.71 | +14.44 | +15.19 | +15.27 |
| Monaco | -0.56 | -0.09 | -1.32 | -0.99 | -0.53 |
| Belgium | +3.91 | +1.43 | +3.92 | +5.29 | +2.10 |

---

## Key Finding

**M1 fails the Bahrain target and regresses Belgium.** The frontier model A+Bv^2 anchors the braking arc to the AVERAGE capability shape (~37-39 m/s^2 at Bahrain mid-speeds), which is shallower than the raw knee (-52.13). Imposing this model over the full arc prevents the smoother from reaching the true peak: the model fit captures the bulk of the braking arc, not the deepest instance. The effect is a deconcentrating prior: it suppresses ringing (good) but also suppresses the genuine deep knee (bad).

**Ringing improvement (Monaco at sigma=2.0) is real** but is a side effect of smoother-state regularization via adjacent braking-zone anchors, not a direct fix to the coast-zone ringing defect.

---

## Sigma Sensitivity

- sigma=0.5 (tight): Strong pull to model. Bahrain -37.69 (worse than gaussian), Belgium -34.92. Monaco ringing still fails (+13.67).
- sigma=1.0 (moderate): Similar to tight. Bahrain -36.94. Monaco ringing +12.10 (still fails). Belgium -33.55 (significant regression vs kind3).
- sigma=2.0 (loose): Monaco ringing finally passes (-1.52). Bahrain -36.86 (shallower still). Belgium -36.74 (small regression vs kind3 -37.41).

There is no sigma value where M1 simultaneously deepens Bahrain AND fixes Monaco AND preserves Belgium.

---

## Failure Modes

1. **Bahrain knee regression (primary failure):** The model a_b+b_b*v^2 at Bahrain fits to braking events across multiple corners; the average is well below the hardest stop at turn 1. Anchoring to the average prevents the smoother from following the actual sensor reading at the extreme. Root cause: the frontier model captures typical capability, not the peak-event transient.

2. **Belgium over-suppression artifact:** ringing=-22 to -23 m/s^2 in the non-throttle zone is physically implausible (bounded by traction circle). The kind=3 anchor propagates via the backward RTS smoother into adjacent coast segments, pulling the acceleration state toward a braking model even where no braking occurs. The margin=2 edge trimming is insufficient to contain temporal leakage.

3. **Monaco ringing only fixed at sigma=2.0:** Monaco's ringing defect is in the non-throttle SHORT-STRAIGHT COAST zone, not the braking zone. The M1 anchor only covers brake_mask samples, so it does not directly address the Monaco defect. The loose sigma helps indirectly.

4. **Model circularity risk:** The frontier fit aggregates all braking events on the lap. A corrupted or atypical event biases the model and propagates through all brake-arc anchor values. The plateau anchor (#498) uses per-sample raw values directly, avoiding this aggregation.

---

## Invariant Extension Statement

decision:two_cycle_external_anchor_design says: anchor is EXTERNAL and UN-BIASED (raw a_long, NEVER re-read from a smoothed trajectory), plateau-only placement, two cycles only, Student-t jerk foundation.

M1 extends this on two axes:

(a) Value source: Changed from raw per-sample a_long_raw to a MODEL value a_b + b_b * v_i^2 fit from raw samples. The model is fit ONLY from inp.a_long_raw, never from any smoothed trajectory output. This preserves the "external & un-biased" core: the model is computed before cycle 2 and does not depend on any smoothed state. Extension risk: the model imposes A+Bv^2 shape even when the real event deviates (model is a capability average, not a per-event observation).

(b) Placement: Changed from plateau-only to the full braking arc with a small edge margin (margin=2 samples). Onset placement was intended to capture the knee transient that plateau anchoring misses. In practice, full-arc placement anchors the entire phase to an average capability value shallower than the true peak, causing Bahrain knee regression.

Both extensions are explicit (not silent). Two-cycle structure and the "never re-read from smoothed" guard are preserved.

---

## Soundness Self-Assessment

The Monaco ringing improvement at sigma=2.0 is real but incidental. The Belgium ringing suppression (-22 to -23 m/s^2) is an artifact and physically implausible. The Bahrain knee regression is certain: A+Bv^2 averaged over a lap's braking events gives typical peak, not the maximum-effort stop transient. The mechanism is conceptually sound but applied to the wrong observable.

---

## Re-run Command

From worktree C:/Programs/f1Brainz/.claude/worktrees/agent-a184c3e7b582e228e:
```
py scripts/run_m1_scoreboard.py
```

Or directly from the spike archive (requires scoreboard.py on the Python path):
```
py C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/m1/run_m1_scoreboard.py
```

Note: scoreboard.py must be checked out from feat/physics-aware-estimator-496 into src/physics/layer2/ first.

---

## Recommendation

**WEAK.** M1 fails the Bahrain knee target (regresses vs both baselines across all sigma values), regresses Belgium knee vs kind3, and only fixes Monaco ringing at sigma=2.0 loose where the fix is a side effect, not a direct mechanism. The fundamental problem is that the A+Bv^2 model captures average braking capability, not the peak-event transient that IS the Bahrain defect. The full-arc placement also causes over-anchoring that leaks into coast segments.

For G3: the winning approach for Bahrain knee deepening should anchor ONSET directly with raw a_long_raw samples at the transition window (not a model), restricted to the onset transient (first N samples of each brake run), with a sigma that is looser than the plateau to allow more freedom at the transition. Monaco ringing needs a coast-zone specific fix (not a braking-zone anchor).

---

## Workflow Feedback

- Scoreboard.py was not in the worktree branch (worktree-agent-a184c3e7b582e228e). Required: git checkout feat/physics-aware-estimator-496 -- src/physics/layer2/scoreboard.py. Handoff should include this step.
- Handoff suggested reusing fit_braking_frontier from src/physics/braking_fit.py, but that function takes KinematicSample objects not available in CaseInputs. Implemented a direct numpy OLS equivalent. Future handoffs should note the API mismatch or provide a bridge.
- Belgium non-throttle ringing was not listed as a guard metric in the handoff (only knee). The M1 artifact of ringing=-23 m/s^2 on Belgium is a new failure mode. Recommend adding Belgium ringing as an explicit guard in future G2 handoffs.
