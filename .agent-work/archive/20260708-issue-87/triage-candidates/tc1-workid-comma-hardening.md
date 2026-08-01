# Triage Recommendation: Harden validate_delta against comma/whitespace work-ids

## Classification
research hardening (latent robustness; no current defect)

## Source checklist/artifact
- execute.json tc1 (g1 implementer out-of-scope observation + reviewer tc1, both non-blocking)

## Structural anchor
scripts/apply_lessons_delta.py — `ticked-work-ids` header ring / `validate_delta`

## Cartographer mismatch class
none

## Problem
The new `ticked-work-ids` playbook-state header stores seen work-ids comma-joined. A future work-id containing a comma (or whitespace) would mis-split on round-trip, silently corrupting the dedupe ring.

## Current truth
No such work-id exists: every observed work-id in the repo is identifier-like (`issue-NN`, `2026NNNN-slug`). Malformed field state (empty comma entry) already raises `LessonsDeltaError` on load.

## Desired/future concern
If work-id shape ever loosens (spaces, arbitrary strings), `validate_delta` should reject comma/whitespace work-ids at the delta boundary (fail-visible), or the header should encode entries.

## Evidence
- IMPLEMENTER_RESULT.md "Out-of-scope observations" (.agent-work/issue-87/crew-handoffs/g1-implement/)
- REVIEW_RESULT.md tc1 (.agent-work/issue-87/crew-handoffs/g1-review/)

## Impact
Low today (no producer of such work-ids). Guards the dormancy dedupe mechanism's integrity against a future caller-contract drift.

## Suggested scope
One validation clause in `validate_delta` rejecting work-ids matching `[,\s]`, plus one test.

## Non-goals
Encoding scheme for arbitrary work-ids; changing work-id conventions.

## Acceptance criteria
- [ ] A delta whose work_id contains a comma or whitespace is rejected with LessonsDeltaError
- [ ] Test covers the rejection; suite green

## Recommended priority
low

**Reason:** theoretical until work-id shape loosens; cheap insurance.

## Related artifacts
- .agent-work/issue-87/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md
- .agent-work/issue-87/crew-handoffs/g1-review/REVIEW_RESULT.md

## Disposition
fixed-now

**Detail:** fix commit 794bb76 (validate_delta rejects work-ids matching [,\s]; test test_work_id_with_comma_or_whitespace_rejected; suite 385 passed). Human directed fix-now at the issue-87 triage step.

## Issue creation authority
ask user
