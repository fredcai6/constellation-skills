# Reviewer Handoff — G4 (bounded validation fit + acceptance demonstration on real data)

## Gate
g4-review (issue #666, epic #659)

## Survey State Location
`.agent-work/666-driver-fingerprint/g4-review/review.json` (NOT the worktree root).

## What Was Implemented
`tests/unit/physics/fingerprint/test_bounded_validation.py` (13 tests) + `scripts/fingerprint_bounded_validation.py`
(runnable harness) + `bounded_fit_summary.json` — runs the G3 fit on the REAL bounded slice and asserts all
acceptance invariants on real data. 96/96 fingerprint suite green (implementer + commander re-run).

## How to Inspect the Diff
UNCOMMITTED working tree of `C:/Programs/f1brainz-wt/epic659-666` (NOT `git diff main...HEAD`). `git status
--porcelain` then `git diff`. Implementer result at
`.agent-work/666-driver-fingerprint/crew-handoffs/g4-implement-result.md`; summary artifact (Local-only) at
`.agent-work/666-driver-fingerprint/artifacts/bounded_fit_summary.json`.

## Task Statement
Demonstrate every acceptance invariant on REAL data (bounded slice), populate a temp store, emit an honest
support+shrinkage summary. A measured-null is a complete deliverable.

## Close Criteria (each a review check — REPRODUCE on the real slice)
- **Cutoff-leakage on real rounds:** the test proves `fit(as_of_round=7)` on the full slice is byte-identical to
  the fit on a rounds<=7 truncation (real future rounds 10/12 excluded), and `fit(12)` differs. This must run the
  REAL fit on the REAL slice, not a mock. Reproduce it.
- **Exactly k=4 cells + unresolved-not-missing** on real data; the thin c1 cell reported per (driver, cutoff) as
  resolved or unresolved, never missing.
- **Thin-cell σ-widening priced once** (idempotent replace-on-rerun on the real thin cell).
- **Class-axis shared_floor = sqrt(var_circuit) non-zero**, driver-overall NOT floored (the driver axis / var_team
  is structurally never drawn on for the floor).
- **Both channels** present.
- **ClassVocabulary F12 verdict sourced with PROVENANCE, NOT silent PASS** — confirm it derives from a real source
  (the implementer used `docs/physics/625-f12-holdout-stability.json`, PASS 5/5) with the honest Belgium caveat, OR
  an explicit UNVERIFIED+override. A silent hardcoded PASS is a BLOCK.
- The `honest_statement` in `bounded_fit_summary.json` matches the numbers (a measured-null reported AS a
  measured-null, not dressed up).
- Full `tests/unit/physics/fingerprint/` green; no G2/G3 module edited; no data/.agent-work blob staged.

## Allowed Scope
`tests/unit/physics/fingerprint/test_bounded_validation.py` + `scripts/fingerprint_bounded_validation.py`.
Read-only consumption of the fit/store/vocabulary + the slice DB + f12 provenance artifact.

## Specific Exclusions
No G2/G3 edit expected. The vocab verdict sourcing path is implementer-authorized (check it is NOT a silent PASS).

## Constraints the Implementation Must Respect
- Real fit on real slice; temp store; slice read-only. measured-null = complete. No silent PASS. No blob staged.

## Map Anchors (inbound)
- **Decision anchors:** `decision:c1_driver_utilization_design` — strictly_pre. `@grade: settled/measured · leans g4-implement`
- **Evidence expectations:** `claim: cutoff-leakage`, `claim: k-cells-populated`, `claim: sigma-priced-once`, `claim: #675-coverage recorded`.

## Evidence Produced
Implementer result (path above) with bounded_fit_summary.json + real-data assertions + 96/96 suite; commander
re-ran 96/96, confirmed no G2/G3 edits + honest summary + #625 provenance real. Verify against `g4-integrate.c1`
(full fingerprint suite) and `g4-integrate.c2` (APPROVE verdict).

## Suggested Model Tier
Simple-to-moderate — verifying real-data honesty + the no-silent-PASS vocab sourcing.

## Stop Conditions
BLOCK if: the validation mocks the fit instead of running it on the real slice; a silent hardcoded PASS verdict;
an invariant not actually asserted on real data; the honest_statement misrepresents the numbers.

## Return Format
REVIEW_RESULT: verdict APPROVE/BLOCK, per-check findings, blockers, out-of-scope, workflow feedback. Write to
`.agent-work/666-driver-fingerprint/crew-handoffs/g4-review-result.md` AND SendMessage a concise summary to
`cmdr-666` before ending your turn.
