# Reviewer Handoff

## Gate
g3 (g3-review)

## What Was Implemented
`docs/physics/measurement_model.md` (538 lines, doc-only) — the issue #447 deliverable: a
measurement model for the two raw FastF1 streams plus an operationalized GO/NO-GO decision brief
with a labeled GO recommendation, the F1 chi-square band recommendation, and the F3 s_finish
design decision. No `src/` changed.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
git status
git diff --stat
# doc is new+untracked:
py -c "print(open('docs/physics/measurement_model.md',encoding='utf-8').read()[:200])"
```
Implementer result: `.agent-work/issue-447/crew-handoffs/g3-implement-result.md`.
Evidence JSON: `.agent-work/issue-447/evidence/{char_summary,jitter_offset_summary}.json` + per-session.

## Task Statement
Author the deliverable doc from G1+G2 evidence: sampling distributions (two-grids), quantization,
Z verdict, white-jitter error model, per-channel noise, offset stability (F2), an operationalized
GO/NO-GO gate (both halves stated before applied), a LABELED recommendation, the F1 band, the F3
s_finish decision, Last-verified line, traceability. Recommend GO/NO-GO; do NOT decide it.

## Close Criteria (each a review check)
- Every NUMBER in the doc traces to the on-disk evidence JSON and MATCHES it. Spot-check at least
  5 numbers across §1–§5 against the JSON (sampling rate, an overlap fraction, a quantization step,
  a Z range, a per-session offset, a noise variance, the chi-square range).
- The doc does NOT say "shared grid" or "240/10 Hz" as fact (G1's corrected picture).
- The error model is stated as WHITE-JITTER with discriminators + the SG-artifact caveat.
- The GO/NO-GO gate is operationalized: criteria for BOTH halves stated BEFORE application, then
  applied per session with pass/fail. The criteria are reasonable and the pass/fail follows.
- The recommendation is CLEARLY LABELED as a recommendation (not a decision) and is honest about
  the large-chi-square caveat.
- F1: recommends a band WITH noise-model justification; correctly notes the gate already defaults
  to (0.5,2.0) and that the band must apply to an offset-removed residual. No unwarranted code edit.
- F3: a clear s_finish decision WITH evidence (the s3-pins-to-track-length finding).
- PROVENANCE HONESTY: the doc must NOT present the "95.9→63.9" figure or any reviewer-only number
  as on-disk evidence. Confirm it is flagged as the G2 reviewer's re-computation (it is, in §6/§7/
  §11). Confirm no number is fabricated — if the doc cites a figure, it's either in the JSON or
  flagged with its true provenance.
- Docs bar: valid commands (the reproduce commands run), existing references (overview.md,
  windowed_estimator.md, trajectory_grading_report.md, covariance_gate.py all exist), units/bounds
  explicit, `Last verified: 2026-06-11` present.

## Allowed Scope
`docs/physics/measurement_model.md`. (No src/ was changed; confirm that.) You may write throwaway
checks (not in scripts/; clean up) to verify numbers against the JSON.

## Specific Exclusions (flag if touched)
Any estimator; any GO/NO-GO DECISION (recommendation only); evo imports; 0a primitive behavior
changes; merging; closing issues.

## Constraints the Implementation Must Respect
Numbers traceable + matching; recommendation only; docs reviewer bar; `py` not `python`.

## Map Anchors (inbound)
- **Structural:** `docs/physics/measurement_model.md`; references covariance_gate.py + the report
  schema; physics region.
- **Capability:** measurement-model contract for Phase 1 estimators.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; recommendation-only.
- **Decision anchors:** F1 band, F3 s_finish, white-jitter error model. The doc becomes a durable
  physics contract (Cartographer reconciles).
- **Evidence expectations:** operationalized gate applied to measured values; labeled recommendation
  a non-specialist can follow; full traceability.

## Evidence Produced
The committed doc (538 lines) with a §11 number→source traceability table. Implementer flagged two
honesty findings: (1) the 95.9→63.9 figure is reviewer-only (cited as such); (2) it used the wider
JSON-traceable noise ranges (e.g. Z 0.018–8.121 m², São Paulo highest) rather than the handoff's
narrower headlines. Verify both were handled correctly.

## Suggested Model Tier
stronger — reason: this is the human's GO/NO-GO brief; verifying traceability + the soundness of
the operationalization/F1/F3 needs real independent checking of the numbers.

## Stop Conditions
BLOCK if: any doc number contradicts the JSON; a reviewer-only/fabricated number is passed off as
on-disk evidence; the recommendation is presented as a decision; the gate is not operationalized
before application; F1 or F3 is unsupported; a reference or command is broken.

## Return Format
Return REVIEW_RESULT to
`C:/Programs/f1Brainz-worktrees/cmdr-447/.agent-work/issue-447/crew-handoffs/g3-review-result.md`:
verdict (APPROVE or BLOCK), per-check findings INCLUDING your spot-checked numbers (doc value vs
JSON value), blockers, out-of-scope observations, workflow feedback. Then a concise final message
with the verdict.
