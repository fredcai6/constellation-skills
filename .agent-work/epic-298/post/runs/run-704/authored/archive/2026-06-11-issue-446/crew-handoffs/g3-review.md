# Reviewer Handoff

## Gate
g3 — Multi-session strawman run + verdict (review)

## What Was Implemented
`scripts/run_trajectory_grading_strawman.py` ran the g2 harness over 3 cached sessions (2023
Belgium Q, 2023 Belgium R, 2022 Spain R), writing 3 JSON reports to
`.agent-work/issue-446/evidence/`. `.agent-work/issue-446/VERDICT.md` reports per-session numbers
and concludes the harness DISCRIMINATES (sector-anchor gate rejects the strawman in all 3;
covariance band too loose to discriminate — a Phase 0b finding). Commit 8e27031.

## How to Inspect
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-446
git show 8e27031 -- scripts/
cat .agent-work/issue-446/VERDICT.md
py -c "import json,glob;[print(f) for f in glob.glob('.agent-work/issue-446/evidence/*grading*.json')]"
```
Implementer report: `.agent-work/issue-446/crew-handoffs/g3-implement-RESULT.md`.

## Task Statement
Run the harness over ≥3 sessions (≥1 race, ≥1 quali, 2022-2025), emit machine-readable reports,
and write a verdict (discrimination or honest null) with per-session key numbers traceable to the
reports. Full task: `.agent-work/issue-446/crew-handoffs/g3-implement.md`.

## Close Criteria (each a review check)
- ≥3 JSON reports exist under `.agent-work/issue-446/evidence/` (≥1 race + ≥1 quali, 2022-2025),
  each schema-valid per the g1 report schema.
- **Traceability (highest value):** the per-session numbers in VERDICT.md (anchor residual
  summary + 50ms verdict, reduced chi-square, fitted inter-stream offset range) MATCH what is
  actually in the JSON reports. Open at least one report and recompute/confirm 2-3 of the quoted
  numbers. A number in the verdict that is NOT in the reports is a BLOCK.
- **Conclusion soundness:** the "discriminates" claim is supported — the sector-anchor gate FAILs
  the strawman with residuals well above 50ms in each session, and the stated reason (free-anchor
  co-estimation absorbs mean bias but not per-lap variance) is consistent with the numbers. The
  honest secondary finding (covariance band [0.01,100] too loose → all pass despite chi-squares
  0.6-11) is correctly framed as a Phase 0b calibration item, NOT hidden. Confirm nothing is
  overclaimed and no null is buried.
- The run was offline (no re-pull) and wrote no canonical DB.
- No harness (src/) modules were modified in this gate (only scripts/ + .agent-work). Confirm via
  the diff.
- Bulky JSON reports were NOT committed as durable data.

## Allowed Scope
`scripts/` driver, `.agent-work/issue-446/` (verdict + evidence).

## Specific Exclusions
No src/ harness changes in this gate; no re-pull; no canonical-DB writes; no evo imports. Flag if
the diff shows otherwise.

## Map Anchors (inbound)
- **Structural:** `scripts/` driver; `struct:preprocessing.trajectory_grading` exercised.
- **Capability:** trajectory grading — discrimination evidence.
- **Constraints/assumptions:** honest-null clause; evidence stays out of git.
- **Evidence expectations:** harness discriminates OR documented honest null at 50ms — ≥3-session
  numbers traceable to reports.

## Evidence Produced
3 JSON reports + VERDICT.md + IMPLEMENTER_RESULT. Headline: anchor gate FAILs all 3 (max residual
0.30-1.51s vs 50ms); covariance gate PASSes all 3 (chi-sq 0.60-11.14, band too loose); offsets
range ~[-0.23,+0.41]s.

## Suggested Model Tier
stronger — reason: this is the analytical verdict of Phase 0a; traceability + conclusion soundness
must be independently confirmed.

## Stop Conditions
Return BLOCK if: <3 valid reports; a verdict number is not traceable to the reports; the
discrimination conclusion is overclaimed or a null is buried; src/ harness was modified; the run
wasn't offline. Otherwise APPROVE.

## Return Format
Return REVIEW_RESULT to `.agent-work/issue-446/crew-handoffs/g3-review-RESULT.md`: VERDICT (exactly
APPROVE or BLOCK), per-check findings (include which report numbers you independently confirmed),
blockers, out-of-scope observations, workflow feedback.
