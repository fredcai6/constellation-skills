# Triage Recommendation: Rank-blend production aggregation switch (best_across_fp → blend_rank) — HOLD / fold into #375

## Classification
unresolved decision (deferred model-input change)

## Source checklist/artifact
- `execute.json` triage_candidate `tc1` (flagged at g3-integrate)
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6.2 (rank-blend verdict) and §7.6.1 (original deferral)
- `.agent-work/issue-381-same-pairs/evidence/same_pairs_numbers.json`

## Structural anchor
`struct:evo` — `src/evo_predictor/practice_preprocessor/` (the cross-session aggregation that
would change); pinned today by
`tests/unit/evo_predictor/test_practice_preprocessor.py::TestSectorFeatures::test_cross_session_theoretical_best_is_pooled_min_sectors_not_rank_blend`.

## Cartographer mismatch class
none (no structural drift; a deferred input-recipe decision)

## Problem
§7.6.1 identified that switching the production quali aggregation from `best_across_fp`
(pooled min-sectors) to `blend_rank` (mean per-session rank, min-sectors) raises the
data-only ceiling by ~0.6pp, and deferred it to #375. #381 was tasked (Admiral Q5) with
deciding whether that deferred candidate should fire NOW as a standalone cheap fix, based on
where the trained model actually sits relative to that slice.

## Current truth
- Production uses `best_across_fp` (pooled min-sectors over FP1/2/3); recipe is test-pinned.
- #381 measured the trained quali model on the IDENTICAL shared pairs as the ceiling:
  - `blend_rank − best_across_fp` ceiling slice = **+0.0017** (headline 2018–2024) /
    **+0.0066** (OOS 2025) — ~0.2–0.7pp.
  - Model-side gap below the *current* `best_across_fp` ceiling = **~19pp** on the standalone
    `race_weekend` channel (model 0.6149 vs ceiling 0.8061, headline).

## Desired/future concern
Whether to ever switch to rank-blend, and if so, to do it inside #375 (the
context-conditioned net) rather than as a standalone change — so the input distribution shift
is co-designed with the model rework, not slipped in before/independently of it.

## Evidence
- §7.6.2 numbers table + slice figures (verbatim from `same_pairs_numbers.json`).
- §7.6.1: the slice is "a model-input change… deferred to #375"; changing inputs before #381
  measured the model would have defeated #381's attribution.
- The standalone `race_weekend` deficit is concentrated on coarse far-apart pairs
  (gap≥9: model 0.687 vs ceiling 0.937) — a model-side ordering problem, not an input-recipe
  ceiling problem.

## Impact
Routing decision for the remaining quali gap. Firing the rank-blend switch standalone would
spend effort lifting the ceiling ~0.6pp while the model captures only ~76% of the ceiling it
already has — low leverage and it would disturb #381's measured baseline. Folding it into #375
keeps the lever where the gap actually is (model-side).

## Suggested scope
**HOLD as a standalone issue.** Do not file a separate rank-blend switch issue. If the Admiral
wants it tracked, add it as a sub-item / acceptance note inside **#375** (context-conditioned
quali net): "evaluate rank-blend vs pooled-min-sectors inputs as part of the conditioned-net
input design," so the input change is co-designed with the model.

## Non-goals
- Not a standalone production aggregation change now.
- Not a model retrain in this issue.
- Does not change the existing recipe pin test (that pin stays until #375 deliberately moves it).

## Acceptance criteria
- [ ] Admiral decision recorded: HOLD standalone vs file vs fold-into-#375.
- [ ] If fold-into-#375: a note/sub-item added to #375 referencing §7.6.2's slice-vs-gap numbers.

## Recommended priority
low

**Reason:** The lever is ~0.6pp of ceiling vs a ~19pp model-side gap; the high-value work is
the model-side routing already recommended to #375. This candidate exists only to close the
Q5 loop explicitly, not because it is itself worth near-term effort.

## Related artifacts
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6.1, §7.6.2
- `.agent-work/issue-381-same-pairs/evidence/same_pairs_numbers.json`
- `scripts/diagnose_quali_same_pairs.py`

## Issue creation authority
ask user — Admiral decides (binding standing order: "do not file the issue here"). Default
recommendation: HOLD standalone, fold into #375.
