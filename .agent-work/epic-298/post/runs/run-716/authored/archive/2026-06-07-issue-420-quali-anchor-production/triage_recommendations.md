# Triage Recommendations — issue #420 run

Three issue-ready recommendations. NOT filed (background job; spine requires
per-issue human approval which I cannot obtain). Presented for the human to
approve/file. Authority note: ORCHESTRATOR_CONTEXT allows autonomous issue
creation for non-trivial tasks, but the spine triage step mandates explicit human
approval per issue before filing — so these are issue-ready only.

---

## Triage Recommendation: Activate the quali pace anchor via a gold retrain (stage-1 → ON)

### Classification
unresolved decision / research hardening / feature

### Source checklist/artifact
- #420 §7.6.4 (safe-activation story); g2 acceptance evidence; downstream-impact
  assessment.

### Structural anchor
`src/evo_predictor/quali_pace_anchor.py` + `struct:evo.sampled_runtime` + fusion/calibration

### Problem
The quali pace anchor is shipped (#420) and PROVEN to reproduce the §7.6.3
ordering improvement through the production path, but ships DEFAULT OFF. It cannot
be safely turned ON until the downstream consumers (fusion precision-weighting,
calibration) are re-fit against the anchored pi distribution and the FUSED quali
Brier is validated. That retrain was out of #420's scope.

### Current truth
`quali_pace_anchor_enabled = false` in `configs/evo/gold_defaults.toml`. The blend
z-standardizes the race_weekend head's pi (changing its scale), while fusion's
trained `mean_scale`/`covariance_scale` and the calibration params were fit on the
un-anchored scale. Standalone-head sign-acc improves (measured: headline α=0.5
0.7499 vs baseline 0.6163); fused/Brier impact is UNMEASURED.

### Desired/future concern
A gold cycle run with the anchor ACTIVE during training-time field assembly +
fusion-training, so fusion/calibration re-fit to the anchored distribution; then
validate fused quali Brier vs the current gold baseline. If non-worse and ordering
improves, flip the default ON.

### Evidence
- §7.6.4 downstream-impact assessment + safe-activation story.
- `fusion.py` lines 219-224: `obs_mean = mean_scale*pi`, `obs_cov = covariance_scale*sigma_pi+...`
- `.agent-work/issue-420-quali-anchor-production/g2_accept_numbers.json`

### Impact
This is the path that turns a measured, shipped-but-dormant capability into a live
production improvement. High value (it banks the §7.6.3 majority gap into the real
fused output) — but must be gated on calibrated Brier evidence.

### Suggested scope
Run a gold cycle with `quali_pace_anchor_enabled=true`; compare fused quali Brier
(primary) + ordering vs the current gold baseline on held-out seasons; decide
default ON/OFF from the evidence; if ON, flip `gold_defaults.toml` + re-promote.

### Non-goals
Per-context anchor weighting (that is #375). Changing α from 0.5 without a fresh
sweep. Touching race/race_start.

### Acceptance criteria
- [ ] Gold cycle trained with the anchor active (fusion + calibration re-fit).
- [ ] Fused quali Brier vs baseline reported (Brier primary).
- [ ] Default ON/OFF decision recorded with the evidence; config updated if ON.

### Recommended priority
high

**Reason:** It is the activation path for a shipped, measured, ratified capability;
without it the #420 work stays dormant.

### Related artifacts
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6.4; #420 PR; #375 (stage-2).

### Issue creation authority
issue-ready only (needs human approval per spine)

---

## Triage Recommendation: Split `predict_from_features` in sampled_runtime.py (pre-existing simplification violation)

### Classification
cleanup

### Source checklist/artifact
- #420 g1-review finding (tc1); simplification_limits output.

### Structural anchor
`src/evo_predictor/sampled_runtime.py`

### Problem
`predict_from_features` is 153 lines, over the project's <100-line function limit.
Pre-existing (predates #420; the #420 anchor wiring went into `_run_stage`, a
separate 44-line method, not this function).

### Current truth
`py -m src.utils.simplification_limits --paths src/evo_predictor/sampled_runtime.py`
reports exactly one violation: `predict_from_features: function_lines=153`.
Verified by the #420 baseline check (153 before #420; unchanged after).

### Desired/future concern
Decompose `predict_from_features` into well-named helpers to satisfy the limit.

### Evidence
- simplification_limits output (1 violation, this function).
- #420 g1-review + implementer both flagged it as pre-existing/out-of-scope.

### Impact
Maintenance erosion; the function is a central runtime entry point. Low urgency
(it is stable and tested) but tracked per project doctrine on simplification.

### Suggested scope
Extract cohesive blocks of `predict_from_features` into private helpers; no
behavior change; region tests stay green; the function drops under 100 lines.

### Non-goals
Any behavior change; touching the anchor logic; touching fusion.

### Acceptance criteria
- [ ] `predict_from_features` < 100 lines.
- [ ] `py -m src.utils.simplification_limits --paths src/evo_predictor/sampled_runtime.py` clean.
- [ ] evo unit suite green (byte-identical behavior).

### Recommended priority
low

**Reason:** Pre-existing, stable, tested; doctrine cleanup, not correctness.

### Related artifacts
- #420 PR (where it was re-confirmed).

### Issue creation authority
issue-ready only (needs human approval per spine)

---

## Triage Recommendation: Consider an explicit all-FP min-sector practice feature

### Classification
research hardening / feature

### Source checklist/artifact
- #420 anchor-variant probe (`probe_anchor_variants_420.py`); G2 finding.

### Structural anchor
`src/evo_predictor/practice_preprocessor/` + `models/_features.py` (DriverFeatures)

### Problem
The #420 anchor had to reconstruct the all-FP min-sector pace as
`min(qs_best_raw, lr_best_raw)` because the production feature build only exposes
the per-bucket (quali-sim / long-run) min-sectors, not a single all-FP min-sector.
The reconstruction works (reproduces best_across_fp in-machinery), but an explicit
`*_best_across_fp_raw` feature would be cleaner and reusable.

### Current truth
`DriverFeatures` has `qs_best_raw` (short-stint) and `lr_best_raw` (long-stint) but
no all-laps min-sector field. The probe confirmed `min(qs,lr)` ≈ DB `best_across_fp`
(α=1 ceilings 0.8163 vs 0.8101 on the probe years).

### Desired/future concern
A first-class all-FP min-sector practice feature, if other consumers want the
all-laps pace ordering without the min-of-two-buckets idiom.

### Evidence
- `.agent-work/issue-420-quali-anchor-production/probe_anchor_variants_420.py` output
  (A=qs-only ceiling 0.693; B=min(qs,lr) 0.816; C=best_across_fp 0.810).

### Impact
Low/medium — purely a cleanliness/reuse improvement; the current min-of-buckets
reconstruction is correct and tested. Only worth it if more consumers need it.

### Suggested scope
Add an all-FP min-sector feature to the practice_preprocessor + DriverFeatures;
migrate the #420 anchor to it; verify the anchor numbers are unchanged.

### Non-goals
Changing the #420 anchor result; any retrain (the feature is additive/raw).

### Acceptance criteria
- [ ] All-FP min-sector feature on DriverFeatures, populated from the preprocessor.
- [ ] #420 anchor uses it; acceptance numbers unchanged within tolerance.

### Recommended priority
low

**Reason:** Cleanliness only; the reconstruction is correct and the win is marginal.

### Related artifacts
- #420 PR; the anchor-variant probe.

### Issue creation authority
issue-ready only (needs human approval per spine)
