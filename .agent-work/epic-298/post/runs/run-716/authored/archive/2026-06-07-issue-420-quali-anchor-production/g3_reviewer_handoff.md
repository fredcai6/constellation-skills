# Reviewer Handoff — G3 docs + default decision (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`. Read `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`.

## Gate
`g3` — verify the new §7.6.4, the downstream-impact assessment, the default-OFF
decision, and the config-comment fix.

## What Was Implemented
- New `### 7.6.4` in `docs/evo/prediction_ceiling_and_priorities.md` (between §7.6.3
  and §7.7): production attach point, anchor = min(qs_best_raw,lr_best_raw),
  acceptance reproduction tables, α=0.5 rationale, downstream-impact assessment,
  default-OFF + retrain-first activation, config keys.
- `configs/evo/gold_defaults.toml`: corrected the anchor comment; kept
  `quali_pace_anchor_enabled=false`, `quali_pace_anchor_alpha=0.5`.

## How to Inspect
```bash
git diff docs/evo/prediction_ceiling_and_priorities.md
git diff configs/evo/gold_defaults.toml
```
Read §7.6.4 fully (the doc). Cross-check numbers against
`.agent-work/issue-420-quali-anchor-production/g2_accept_numbers.json`.

## Close Criteria (each a check)
1. **Numbers accurate vs JSON:** every figure in §7.6.4's reproduction tables
   matches `g2_accept_numbers.json` (headline baseline 0.6163/0.6924, α=0.5
   0.7499/0.8736, α=1.0 0.8136/0.9423, ceiling_overall 0.8053; OOS α=0.5
   0.7094/0.8426). Verify by reading the JSON. Flag ANY mismatch.
2. **Reproduction verdict supported:** §7.6.4 states the production path REPRODUCES
   §7.6.3, with the α=0 control reproducing the baseline and α=0.5 within ~0.5pp.
   This is consistent with the numbers.
3. **Anchor explanation correct:** anchor = min across qs (short-stint) + lr
   (long-stint) buckets; the qs-only partial result and the both-buckets full
   result are both described; "reconstructs best_across_fp in-machinery" is
   accurate.
4. **Downstream-impact assessment technically correct (the heart of the gate):**
   the fusion argument must be right — fusion (`fuse_module_fields_ordered`) is a
   precision-weighted update with `obs_mean=mean_scale*pi`,
   `obs_cov=covariance_scale*sigma_pi+...`; the blend z-standardizes pi (changes
   SCALE not just ordering) while sigma_pi is unchanged, so the head's effective
   fusion weight shifts in an uncalibrated way -> fused/Brier impact unmeasured.
   Read `src/evo_predictor/fusion.py` ~lines 217-229 yourself to CONFIRM the cited
   mechanism is accurate (READ-ONLY; do not edit fusion.py). Also: gap-scale +
   calibration consumers noted.
5. **Default-OFF decision consistent:** §7.6.4 ships default OFF with the
   retrain-first safe-activation story (re-fit fusion mean_scale/covariance_scale +
   calibration against the anchored distribution, validate fused Brier). This is a
   pre-authorized override of "default ON" and the rationale (no fused-Brier
   evidence; behaviour-quality change needs calibrated baseline) is sound and
   logged. `gold_defaults.toml` actually has enabled=false + alpha=0.5.
6. **Config comment accurate:** the TOML comment now says per-module race_weekend
   pi BEFORE fusion + anchor=min(qs,lr) + default OFF/retrain note. No longer says
   "fused quali pi".
7. **§7.6.3 and other sections unchanged:** the doc diff is purely additive (only
   §7.6.4 added). §7.6.4 does not contradict §7.6.3.
8. **No forbidden files:** no edits to `fusion.py`, `fusion_training/`,
   `scripts/fusion_replay/`, `docs/evo/fusion_rework_findings.md`. No production
   code changed in this gate (docs + config comment only).

## Allowed Scope (what impl was permitted)
`docs/evo/prediction_ceiling_and_priorities.md` (§7.6.4 only),
`configs/evo/gold_defaults.toml` (comment + keep values).

## Specific Exclusions (flag if touched)
fusion files, fusion_rework_findings.md, §7.6.3/earlier sections, src/ code,
default value, alpha value.

## Suggested Model Tier
Stronger — verifying the downstream technical argument + numeric accuracy of a
sole-writer findings doc.

## Stop Conditions
BLOCK if: a number is wrong vs the JSON, the fusion downstream argument is
technically incorrect, the default is not OFF (or the config doesn't match the
doc), §7.6.3 was altered, or a forbidden file was touched.

## Return Format
REVIEW_RESULT: verdict (APPROVE/BLOCK), per-check findings (1-8), confirmation you
re-read fusion.py and the argument holds, any numeric mismatches, blockers,
out-of-scope observations.
