# Implementer Handoff

## Gate
g3-implement

## Task
Insert a new §7.6.2 section into `docs/evo/prediction_ceiling_and_priorities.md`
(between §7.6.1's end and the §7.7 header) carrying the #381 same-pairs result:
the apples-to-apples numbers table (model vs best_across_fp vs blend_rank; headline
2018-2024 + OOS 2025; shared pairs; events+pairs n), the localized gap, the 3-axis
attribution with numbers, and the WRITTEN ROUTING RECOMMENDATION incl. the
rank-blend triage FIRE/HOLD verdict.

## Protected Intent
The doc tells the truth measured in g2 and closes the loop §7.6.1 opened ("the
remaining quali gap is model-side and is #381's to localize"). Numbers verbatim
from `evidence/same_pairs_numbers.json`. Zero production behaviour change (docs only).

## Test Mode
inspection-only — documentation; numbers cross-checked against the g2 JSON.

## Close Criteria
- §7.6.2 inserted after §7.6.1, before §7.7; §7.6/§7.6.1/§7.7 untouched.
- Numbers table: rw + rh model vs best_across_fp vs blend_rank, headline + OOS,
  with events n and pairs n — matching the JSON exactly.
- 3-axis attribution with numbers: (i) recent-history drag (STANDALONE per-channel,
  honest direction: recent_history is the stronger standalone channel; fusion delta
  declined); (ii) gap/midfield concentration (the monotone widening of the
  race_weekend gap-vs-ceiling); (iii) evidence-weighting residual.
- Written routing recommendation: route remainder to #375 vs cheaper targeted fix,
  with the rank-blend FIRE/HOLD verdict justified by the blend-prod slice
  (+0.0017 head / +0.0066 OOS) vs the ~19pp model-side gap.
- Consistent with §7.6.1's deferred-#379/#375 framing.

## Allowed Scope
- `docs/evo/prediction_ceiling_and_priorities.md` — INSERT §7.6.2 only.

## Specific Exclusions
- No rewrite of §7.6 / §7.6.1 / §7.7 or any other section.
- No production/src/param change. Do NOT file the rank-blend issue here (triage step).
- Do NOT build Piece 2 / #375 (R3 boundary).

## Constraints
- Numbers verbatim from `evidence/same_pairs_numbers.json`; no hand-edited figures.
- The rank-blend verdict is a RECOMMENDATION for the Admiral (triage candidate).
- Markdown style consistent with the surrounding §7.6.x prose.

## Required Evidence
- The inserted §7.6.2 text; a diff confirming only an insertion (no deletions in
  §7.6/§7.6.1/§7.7).

## Verification Commands
```bash
git diff --stat docs/evo/prediction_ceiling_and_priorities.md
git diff docs/evo/prediction_ceiling_and_priorities.md
```

## Suggested Model Tier
simple bounded — synthesis of already-computed numbers into prose.

## Authority
Admiral Q5: dual ceiling; rank-blend triage gated on the verdict the numbers imply.
The verdict follows the numbers (slice vs model gap); the implementer states it, the
Admiral decides whether to file.

## Stop Conditions
Stop if: the numbers in the JSON contradict the planned narrative, or an append
cannot be done without touching existing sections.

## Return Format
Return IMPLEMENTER_RESULT: section inserted, files changed, evidence (diff), the
routing recommendation + fire/hold verdict, assumptions, stop conditions, out-of-scope.
