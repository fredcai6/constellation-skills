# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g4` — findings-doc correction.

## What Was Implemented
Edited `docs/evo/prediction_ceiling_and_priorities.md` (§1.3, §3 Thrust B, §4, §5
table) to replace the overstated race-start σ "mis-level / anti-signal" framing with
the statistically honest finding (decomposition + insignificance at n=24 + level
coverage-aligned), and to reflect what the run did (honest n-aware diagnostic; re-level
declined; fused-Brier confirmation deferred). 49 insertions / 13 deletions.

## How to Inspect the Diff
`git diff -- docs/evo/prediction_ceiling_and_priorities.md`

## Task Statement
Make the doc describe current truth without over-correcting; keep durable facts intact.

## Close Criteria (each a review check)
- §1.3 race-start σ bullet now states: decomposition (recent_history driver −0.119,
  constructor −0.092; race_weekend +0.108 / +0.206); n=24 insignificance (`r_crit≈0.40`,
  all |r|≤0.206, p>0.33, CIs span 0 → indistinguishable from zero); level
  coverage-aligned (NOT "too high/too flat"). The old "too high/too flat / leaving
  predictability on the table" claim is gone/retracted.
- §3/§4: "bounded first win" reframed as the honest diagnostic (n-aware significance
  gate); re-level declined; post-hoc level lever distinguished from training-time
  `lambda_sigma_nll` (#142) lever.
- §5 table: race-start `sigma_corr` row updated to "insignificant at n=24" (stays
  model-bound), deferred Brier noted.
- NO over-correction: the doc must NOT claim race-start σ is perfectly/absolutely
  calibrated — only that there's no significant mis-level/wrong-sign at n=24 and the
  Brier confirm is deferred.
- DURABLE facts unchanged: persistence baselines 0.875 / 0.776 / 0.753; ~6.5% team-pace
  ceiling; retro CV≈0 (#325); near-memoryless reliability (0.123 / 0.142 / 0.119);
  retro order ≡ event order. Confirm these are NOT in the diff (except where 0.119 is
  reused).
- References valid: #325, #142 real; `scripts/diagnose_prediction_ceiling.py` exists;
  NO `.agent-work/...` path referenced.
- Reflects ACTUAL outcomes: G2 honest gate merged; G3 re-level skipped as verified
  no-op.
- Verification: `py -c "import pathlib,sys; t=pathlib.Path('docs/evo/prediction_ceiling_and_priorities.md').read_text(encoding='utf-8'); sys.exit(0 if '0.119' in t else 1)"` exits 0.

## Allowed Scope
`docs/evo/prediction_ceiling_and_priorities.md` only. (Other modified files in the tree
are from earlier gates of THIS run — not this gate's concern.)

## Specific Exclusions (flag if touched)
Any code, other docs, artifacts; durable-fact changes.

## Constraints
Docs = current truth; valid references; durable/model-bound split intact.

## Evidence Produced
49/13 line change; durable figures verified present/unchanged; `.agent-work` refs = 0;
verification exit 0 (0.119 appears twice — durable reliability fact + new decomposition).

## Suggested Model Tier
simple bounded — a scoped doc-accuracy review against a fixed fact list. Reason: facts
are pre-verified; the check is "does the doc match them and avoid over-correction."

## Stop Conditions
Return BLOCK if: a stated number contradicts the verified facts, the doc over-corrects
into an absolute-calibration claim, a durable fact was altered, an invalid reference or
`.agent-work` path appears, or the diff touches anything outside the doc.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers,
out-of-scope observations.
