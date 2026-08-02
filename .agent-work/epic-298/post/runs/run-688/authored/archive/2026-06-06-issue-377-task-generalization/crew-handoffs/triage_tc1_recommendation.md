# Triage recommendation — tc1 (issue #377 close-out)

**Status: RECORDED, not filed.** Background job could not reach the human for the
spine's "explicit approval to file" checkpoint. Surfaced instead in the #377 issue
comment as a noted follow-up. Authority note: issue creation is autonomous per
ORCHESTRATOR_CONTEXT, but the triage spine step requires per-issue human approval,
and this candidate touches a doc owned by another effort — so "produce recommendation
and ask" is the correct fallback.

## What
Stale fusion-correlation figures in `docs/evo/prediction_ceiling_and_priorities.md`
§1.4. It states "Fusion correlations stay high (race-start 0.99 / 0.87, race 0.87,
quali 0.71–0.74)." The **race-start 0.99** figure conflicts with the #373 replay
scorecard, which is the definitive measurement.

## Labels
missing doc / stale generated map (documentation-currency fix)

## Evidence
- [SC] `.agent-work/archive/2026-06-06-issue-373-correlated-fusion/evidence/scorecard.json`:
  race_start `R_estimated_offdiag` range is **0.830–0.895** (max 0.8949); race is
  0.789–0.874; quali is 0.712–0.869.
- The quali "0.71–0.74" in §1.4 is consistent with [SC]; the race "0.87" is roughly
  consistent (max 0.874). Only the **race-start 0.99** is clearly wrong — it appears
  to be from an older/pre-shrinkage or differently-defined measurement.
- Independently flagged by this run's reviewer crew (review_result.txt, r5).

## Why it matters (low–medium)
`prediction_ceiling_and_priorities.md` is a heavily-cited reference doc. A wrong
correlation figure invites future readers to mis-rank race-start redundancy. The new
`fusion_task_generalization.md` is **unaffected** (it cites [SC] directly for every
correlation), so this is not urgent — it is hygiene on the upstream reference.

## Acceptance criteria
- §1.4's race-start fusion-correlation figure is reconciled to the [SC] value
  (0.83–0.895 range, or the specific block the sentence intends) or the sentence is
  re-sourced/removed.
- No other §1.4 figure changes unless [SC] contradicts it.

## Out of scope
- Any change to `fusion_task_generalization.md` (already correct).
- Re-deriving the whole §1.4 — only the one stale figure.
- This run does NOT own `prediction_ceiling_and_priorities.md`; the fix belongs to
  that doc's owner.
