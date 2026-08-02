# Reviewer Handoff

## Gate
g5 (Tier-2 fracture quantification)

## Survey State Location
`.agent-work/627-unified-basis/g5-review/review.json`.

## What Was Implemented
`scripts/tier2_fracture_analysis.py` (ASCII, DB-guarded) + `docs/physics/627-tier2-fractures.md` quantifying the
four x7 fractures, each with a number:
1. DUAL-CdA — CLOSED (MER fused σ 0.0460 m² vs PowerDrag 0.0562, 18.1% tighter; RBR z=6.80 refused; reproduced
   live via cross_view.fuse_dual_cda).
2. GRIP-TRIPLET — bounded-defer ≤0.6% (circuit-controlled partial correlation, max |r|=0.107, n=216/22 circuits).
3. a_long — bounded-defer ≤13.4σ, structural HONEST-NULL (from #523/#546 Config-C tables), NOT re-merged.
4. SHARED-TRAJECTORY-NOISE — bounded-defer honest method-scoped null (≤0.0% by a conservative proxy; cites #644).

## How to Inspect the Diff
UNCOMMITTED working tree in this worktree (C:/Programs/f1-627). `git status --porcelain` then `git diff` (both
files untracked — show in `git status`). Result: `.agent-work/627-unified-basis/g5-implement/IMPLEMENTER_RESULT.md`.

## Task Statement
Quantify each of the four Tier-2 fractures with a number (close-with-number OR bounded-defer-with-quantified-bound)
— undecided or unbounded-deferral is a phase failure. Full task: `.agent-work/627-unified-basis/g5-implement/HANDOFF.md`.

## Close Criteria (each a review check)
- All FOUR fractures carry a NUMBER (closed or bounded-defer). No undecided, no unbounded deferral.
- dual-CdA CLOSED cites G3's real numbers (reproduce the script's dual-CdA line if feasible).
- grip-triplet: the correlation is the PARTIAL/circuit-controlled one (separating physical co-variation from
  measurement-error covariance), not the raw Pearson — confirm the method actually controls for circuit and the
  bound follows from it.
- a_long: BOUNDED-DEFER with a σ number, explicitly NOT re-merged; cites decision:decoupled_1d_longitudinal +
  #523/#546. Confirm no view/estimator was re-wired.
- shared-trajectory-noise: a real bound or an HONEST method-scoped null (states what was and wasn't tested; cites
  #644), not a bare "we couldn't."
- `py scripts/tier2_fracture_analysis.py` runs (exit 0), DB-guarded; data/ untouched.

## Allowed Scope
`scripts/tier2_fracture_analysis.py`, `docs/physics/627-tier2-fractures.md` (analysis only).

## Specific Exclusions
No view/estimator/a_long re-wiring; no production-default/store-schema change; no data/*.db writes; no evo import.
(Known out-of-scope finding tc8: main's physics_estimates.db has the new #627 columns unpopulated because it was
fitted pre-G2/G3/G4 — a store re-fit follow-on, NOT a g5 blocker.)

## Constraints the Implementation Must Respect
- Every fracture carries a number. a_long not re-merged (documented HONEST-NULL). `constraint:physics_region_no_evo_import`.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — new scripts/tier2_fracture_analysis.py, docs/physics/627-tier2-fractures.md.
- Decision anchor: `decision:decoupled_1d_longitudinal` (a_long — defer not re-merge).
- Evidence: each of 4 fractures carries a number.

## Evidence Produced
`py scripts/tier2_fracture_analysis.py` → prints the 4-fracture SUMMARY (Commander re-ran: all 4 numbers present,
exit 0; doc content-check passes with all 4 markers + numeric tokens). data/ clean.

## Suggested Model Tier
stronger — judging whether the partial-correlation method genuinely separates physical from measurement-error
covariance, and whether each deferral bound is defensible, needs statistical care.

## Stop Conditions
BLOCK if: any fracture lacks a number (undecided) or is an unbounded deferral; the grip-triplet correlation is the
raw (not circuit-controlled) one presented as the measurement-error bound; a_long was re-wired; the script doesn't
run or touches data/.

## Return Format
Return REVIEW_RESULT (APPROVE or BLOCK + per-check findings + workflow feedback). WRITE to
`.agent-work/627-unified-basis/g5-review/REVIEW_RESULT.md` AND deliver a summary with the literal verdict token to
ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn.
