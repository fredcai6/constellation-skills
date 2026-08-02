# Implementer Handoff — G3 default decision + downstream statement + §7.6.4 (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`. Read `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`.

## Gate
`g3` — document the verdict, the downstream-impact assessment, the (decided)
default, and write the new §7.6.4. Mostly prose + one tiny config-comment fix.

## DECIDED BY COMMANDER (document; do NOT re-decide)
1. **VERDICT: the production path REPRODUCES §7.6.3.** Numbers (from the G2
   harness `scripts/accept_quali_anchor_420.py`, independently re-derived by review):
   - Headline 2018-2024 LOSO, shared pairs, α=0.5: overall **0.7499** / EASY(gap>=9)
     **0.8736** (vs §7.6.3 0.7452 / 0.8691; delta +0.005 / +0.004; data ceiling
     ~0.806/0.94). Recovered fraction ~0.70.
   - α=0 reproduces the baseline (overall ~0.6155 / EASY ~0.692, vs §7.6.3
     0.6153/0.6926) — the control confirming the same trained head.
   - OOS-2025 α=0.5: overall **0.7094** / EASY **0.8426** (vs §7.6.3 0.7097/0.8451).
   - The pinned numbers in `g2_accept_output.txt` / `g2_accept_numbers.json` are
     authoritative; cite those exact values (read the JSON for precision).
2. **ANCHOR = `min(qs_best_raw, lr_best_raw)`** (NaN/None-safe min-sector practice
   pace across BOTH the short-stint quali-sim and long-stint long-run buckets).
   This reconstructs the §7.6.3 prototype's `best_across_fp` (all-FP min-sector)
   signal IN-MACHINERY (the production feature build splits all-FP clean laps into
   the qs/lr buckets; the min across both recovers the all-laps min-sector
   ordering). The first production attempt used `qs_best_raw` ALONE and only
   PARTIALLY reproduced (α=0.5 overall 0.6624, ceiling 0.678) — the long-run bucket
   carries general-pace ordering and must be included. (Document this as the
   measured reason for the anchor choice.)
3. **α = 0.5** (the measured, checkpoint-2-ratified value). No train-season fit
   clearly beats it: the sweep is monotone (higher α recovers more sign-acc) but
   α->1 discards the head's own signal entirely and more aggressively rescales pi
   (worse downstream), so 0.5 — the value the §7.6.3 measurement and ratification
   rest on — stays. Document this reasoning.
4. **DEFAULT: OFF** (pre-authorized override of ruling 4 per the brief's ruling 6
   last sentence). The case (this is the REQUIRED downstream rationale):

## DOWNSTREAM-IMPACT ASSESSMENT (write this as a §7.6.4 subsection; it drives the OFF default)
Consumers of the race_weekend quali `pi`, all fit/trained against the UN-anchored
pi distribution:
- **Fusion** (`fuse_module_fields_ordered`, READ-ONLY for us — sister #375 owns it):
  it is a Bayesian precision-weighted update where, per module step,
  `obs_mean = mean_scale * pi` and `obs_cov = covariance_scale * sigma_pi + ...`
  (read fusion.py lines ~217-229 to confirm). The fused output depends on the
  ABSOLUTE SCALE of pi relative to sigma_pi, mediated by the TRAINED per-module
  `mean_scale` / `covariance_scale`. The anchor blend
  `(1-α)·z(pi) + α·z(-anchor)` Z-STANDARDIZES pi — it changes pi's MAGNITUDE/SCALE
  (to ~unit variance), not just its ordering — while leaving `sigma_pi` UNCHANGED
  (G1 deliberately did not touch sigma_pi). So `mean_scale * z(blended_pi)` has a
  different magnitude than `mean_scale * original_pi`: the race_weekend head's
  EFFECTIVE WEIGHT in the fusion shifts in an uncalibrated way. This is the core
  risk: the STANDALONE head's ordering provably improves, but the FUSED, calibrated
  production output impact is UNMEASURED and plausibly degraded, because the fusion
  weights were fit to the un-anchored pi scale.
- **Quali gap-scale** (`quali_gap_scale.py`, #391): maps pi differences to gap
  magnitudes; a pi rescale shifts magnitudes. (Note §9.6: the shipped s_hat_e is a
  global constant; still, the magnitude basis changes.)
- **Calibration** (`src/calibration/`) and **gold artifacts**: fit against the
  un-anchored predictive distribution; an anchored pi changes what they calibrate.
- **Why this forbids default-ON now:** Orchestrator Context requires "calibrated
  baseline evidence when behaviour quality changes; Brier primary for gold
  comparison." We measured SIGN-ACCURACY of the STANDALONE head (reproduced), but
  NOT the fused/Brier impact (a gold retrain is out of this issue's scope). Shipping
  ON would change production behaviour quality without that evidence — and the
  §7.6.2 evidence shows the FUSED quali output (~0.71-0.745) already sits well above
  the standalone race_weekend head (0.615) because fusion leans on the near-ceiling
  recent_history head; anchoring the race_weekend head pre-fusion while keeping
  un-retrained fusion weights risks double-counting / mis-weighting the general-pace
  signal.
- **SAFE ACTIVATION STORY (document):** ship the capability behind the flag, default
  OFF. To enable: run a gold cycle that (a) re-fits the fusion `mean_scale`/
  `covariance_scale` and the calibration params against the ANCHORED race_weekend
  pi distribution (i.e. with `quali_pace_anchor_enabled=true` during training-time
  field assembly / fusion-training), and (b) validates the FUSED quali Brier vs the
  current gold baseline (Brier primary). If fused Brier is non-worse and ordering
  improves, flip the default ON in a follow-up. Until then OFF is the calibrated-
  evidence-respecting, reversible posture (this is the fleet's first production-
  behaviour change).
- **Retrain indicated?** YES, before enabling — specifically a fusion + calibration
  re-fit against the anchored distribution. NOT done in this issue (scope).
- Note the #375 (stage-2) relationship: the conditioned net is where the anchor
  folds into the principled fused/calibrated path with per-context weighting; this
  global-α stage-1 anchor is the cheap banked majority, shipped OFF pending the
  retrain (or pending #375 subsuming it).

## Tasks

### A) Write §7.6.4 in `docs/evo/prediction_ceiling_and_priorities.md`
Append a new `### 7.6.4 Production anchor (#420): reproduced through the production
path; shipped behind a flag, default OFF pending a fusion/calibration retrain`
section AFTER §7.6.3 (before §7.7). It MUST contain:
- The production attach point: the race_weekend quali head's per-module pi inside
  `sampled_runtime._run_stage`, BEFORE fusion (NOT at the fusion layer), gated on
  `task=="quali"` + `driver_quali_power_from_race_weekend` + the config flag.
- The anchor = `min(qs_best_raw, lr_best_raw)` and WHY (the qs-only partial result
  -> the both-buckets full result; reconstructs best_across_fp in-machinery).
- The acceptance reproduction table (headline + OOS, α=0/0.5, overall+EASY, vs
  §7.6.3, recovered fraction) with the exact numbers from g2_accept_numbers.json,
  and the honest delta-vs-prototype explanation (bucket-split coverage; α=0 control
  reproduces).
- Chosen α=0.5 + why (no train-season fit clearly beats the ratified value).
- The DOWNSTREAM-IMPACT ASSESSMENT above (the magnitude/precision-weighting concern
  is the heart of it).
- The DEFAULT = OFF decision + the safe-activation (retrain-first) story.
- The config keys (`quali_pace_anchor_enabled`, `quali_pace_anchor_alpha` in
  `configs/evo/gold_defaults.toml`, carried in the runtime stage of the sampled-
  runtime manifest) and how to toggle (set enabled=true; note absent-manifest-key
  defaults to OFF for old bundles).
- Keep it consistent with §7.6.3 (do NOT contradict it; this is the stage-1
  productionization §7.6.3 recommended).

### B) Fix the gold_defaults.toml comment (minimal)
The current comment says "blend the fused quali pi" — that is INACCURATE (the
attach is the per-module race_weekend pi PRE-fusion). Correct the comment to say
the per-module race_weekend quali head's pi before fusion. Keep
`quali_pace_anchor_enabled = false` and `quali_pace_anchor_alpha = 0.5` AS-IS
(default OFF, decided). Minimal localized edit only (sister #375 also edits this
file).

## Close Criteria
- §7.6.4 written, accurate, cites the exact g2 numbers, documents attach point /
  anchor / α / downstream assessment / default-OFF + safe-activation / config
  toggle; does not contradict §7.6.3.
- gold_defaults.toml comment corrected; flag stays OFF, α stays 0.5.
- No other production code changed (G1/G2 are done & approved).
- If you touch any src/, run simplification_limits (you should NOT need to).

## Allowed Scope
`docs/evo/prediction_ceiling_and_priorities.md` (NEW §7.6.4 only — do NOT alter
§7.6.3 or other sections beyond adding 7.6.4), `configs/evo/gold_defaults.toml`
(comment + keep values).

## Specific Exclusions
- Do NOT touch `docs/evo/fusion_rework_findings.md`, `fusion.py`,
  `fusion_training/`, `scripts/fusion_replay/` (sister #375).
- Do NOT change the default to ON. Do NOT change α from 0.5.
- Do NOT run a gold retrain. Do NOT modify the harness or G1 code.
- Do NOT rewrite §7.6.3 or earlier sections.

## Constraints
Docs = current truth, valid commands, the toggle documented, consistent with the
code. Cite measured numbers, not invented ones (read g2_accept_numbers.json).

## Required Evidence
- The §7.6.4 text (it IS the deliverable).
- Confirmation gold_defaults still has enabled=false / alpha=0.5 with corrected
  comment.
- The exact numbers you pulled from g2_accept_numbers.json (so the Commander can
  verify against the harness output).

## Verification Commands
```bash
py -c "import json; d=json.load(open('.agent-work/issue-420-quali-anchor-production/g2_accept_numbers.json')); import pprint; pprint.pprint({k:(v['baseline_acc'],v['baseline_easy_acc'],v['alphas']['0.5']['acc'],v['alphas']['0.5']['easy_acc'],v['ceiling_overall']) for k,v in d.items()})"
# (no code tests needed — docs + config comment only)
```

## Suggested Model Tier
Stronger — the downstream assessment is technically subtle (the
magnitude/precision-weighting argument) and the doc is the Commander's sole-writer
deliverable; precision matters.

## Authority
Commander decided: REPRODUCES verdict, anchor=min(qs,lr), α=0.5, default OFF +
retrain-first activation. You document and justify these; you do NOT change them.

## Stop Conditions
Stop if the g2 numbers JSON is missing/unreadable, or if writing an accurate
downstream assessment would require touching a forbidden (fusion) file.

## Return Format
IMPLEMENTER_RESULT: the §7.6.4 text (or confirm it's written + the file/line
range), the config-comment fix, the cited numbers, assumptions, stop conditions,
out-of-scope observations.
