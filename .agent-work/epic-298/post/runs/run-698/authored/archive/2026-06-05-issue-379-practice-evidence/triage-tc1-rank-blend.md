# Triage Recommendation: Adopt rank-blend cross-session aggregation on min-sectors for normal-weekend quali evidence (GATED on #381)

## Classification
`research hardening` (model-input change gated on a prior diagnostic; secondarily `performance/resource` — a measured ordinal-accuracy ceiling gain)

## Source checklist/artifact
- `.agent-work/issue-379-practice-evidence/execute.json` triage_candidates (`tc1`)
- Admiral ruling Q2(b) on issue #379
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6 / §7.6.1

## Structural anchor
`path: src/evo_predictor/practice_preprocessor/_lap_pipeline.py` (`_compute_sector_features` cross-session pooling at the `groupby("driver_id")` → min-sectors step)

## Cartographer mismatch class
`none` (no structural map mismatch; this is a model-input recipe change, not a structure change)

## Problem
Production combines FP1/FP2/FP3 evidence by **pooling** all clean laps per driver and
taking min-sectors over the pool — the `best_across_fp` recipe, measured data-only
ceiling **≈0.7968**. The best-known data-only recipe is a per-session **rank-blend** on
min-sectors (`blend_rank`), measured **≈0.8029**. There is a genuine **~0.6pp**
ordinal-accuracy ceiling left on the table for normal weekends.

## Current truth
- Cross-session aggregation = pooled-min-sectors (`best_across_fp` ≈0.7968), pinned by
  `tests/unit/evo_predictor/test_practice_preprocessor.py::TestSectorFeatures::test_cross_session_theoretical_best_is_pooled_min_sectors_not_rank_blend`.
- `best_across_fp` already beats FP3-only (≈0.7896) and any single-session feed — there
  is **no** time-averaging dilution to undo (the original §7.6 "dilution" premise was
  dissolved by the #379 reconciliation; see §7.6.1).
- #379 shipped **no production model-input change** by Admiral ruling.

## Desired/future concern
Switch the normal-weekend cross-session combination from pooled-min-sectors to a
per-session rank-blend on min-sectors, capturing the ~0.6pp ceiling gain — but only
once it is safe and attributed.

## Evidence
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6 (blend_rank 0.8029 vs
  best_across_fp 0.7968 vs FP3-only 0.7896) and the new §7.6.1 reconciliation note.
- Harness `scripts/diagnose_quali_evidence.py` (deterministic; reproduces the numbers).
- Production recipe location: `src/evo_predictor/practice_preprocessor/_lap_pipeline.py`.

## Impact
Quali is the dominant ordinal-value stage (epic #378); a ~0.6pp evidence-ceiling lift
propagates downstream. Small but real. Crucially, it is a **model-input change** — it
reshapes the `qs_*` / sector evidence the trained quali module ingests.

## Suggested scope
Land as **conditioning for the context-conditioned net (#375)**, per epic #378's note
that the Step-1 cheap fixes are "exactly what Piece 2 would otherwise learn as
context-weighting." I.e. let the conditioned net learn the per-session rank weighting
rather than hand-coding a separate preprocessor rank-blend pass.

## Non-goals
- Do NOT change production model inputs before **#381** completes its same-pairs
  attribution. Changing the evidence inputs first would shift the quali module's input
  distribution and defeat #381's like-for-like measurement of the *current* model.
- Not a standalone preprocessor edit divorced from #375.

## Acceptance criteria
- [ ] #381's same-pairs attribution verdict is in hand (this issue is **blocked** until then).
- [ ] Rank-blend-on-min-sectors cross-session combination implemented as #375 conditioning (or, if #381 redirects, wherever #381 localizes the gain).
- [ ] Calibrated baseline evidence per ORCHESTRATOR_CONTEXT (evo model-input change ⇒ Evo unit suite + calibrated metric vs stable baseline; Brier primary for gold) showing the edge over the current pooled-min-sectors baseline.
- [ ] The pinning test `test_cross_session_theoretical_best_is_pooled_min_sectors_not_rank_blend` is deliberately updated to reflect the new recipe.

## Recommended priority
`low`

**Reason:** Small measured edge (~0.6pp ceiling; single-session pooling already
captures most of the signal), and hard-gated behind #381 + routed into #375. Not on the
critical path until those land.

## Related artifacts
- Epic #378 (Thrust A); #381 (same-pairs attribution — the gate); #375 (context-conditioned net — the landing point).
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6 / §7.6.1.
- Pinning test: `tests/unit/evo_predictor/test_practice_preprocessor.py::TestSectorFeatures::test_cross_session_theoretical_best_is_pooled_min_sectors_not_rank_blend`.

## Issue creation authority
`ask user` — the Admiral commissioned the candidate *text* (Q2b); spine triage requires human approval before filing. Recommendation: do NOT file a standalone issue now — fold this into #375's problem statement (or attach as a comment on #381/#375) when #381 reports, to avoid premature backlog. Awaiting Admiral's filing decision.
