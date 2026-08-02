# Reviewer Handoff

## Gate
g1 (systematic-budget module)

## Survey State Location
Create your review survey at `.agent-work/627-unified-basis/g1-review/review.json`.

## What Was Implemented
New `src/physics/layer2/systematic_budget.py`: `systematic_budget(...) -> {axis: (shared_rel, session_varying_rel)}`
for axes cda, p_max, a_b, b_b, a_t, b_t, A0, A2 — analytic (no re-fit) per-session nuisance systematic split into
a SHARED (common-mode, un-poolable) and a SESSION-VARYING component. Plus unit tests
`tests/unit/physics/layer2/test_systematic_budget.py` (18 synthetic tests) and a Monza validation test.

## How to Inspect the Diff
Review the UNCOMMITTED working tree in this worktree (C:/Programs/f1-627), NOT `git diff main...HEAD`.
`git status --porcelain` then `git diff` (untracked-safe). The two/three new files appear only in `git status`
(untracked). Full result: `.agent-work/627-unified-basis/g1-implement/IMPLEMENTER_RESULT.md`.

## Task Statement
Build the reusable per-session systematic-budget engine (analytic sensitivities; shared/session-varying split)
that G4 will later wire into the store + pooling. See `.agent-work/627-unified-basis/g1-implement/HANDOFF.md` for
the full task.

## Close Criteria (each becomes a review check)
- Module exists with the documented public function + 8 axes; analytic sensitivities (CdA/P_max ~1:1 with mass;
  d ln CdA/d ln rho ≈ −1); A0 AND A2 do NOT carry the mass/rho systematic (they cancel — not the blind 4%).
- SHARED = common-mode (`quali_mass(year)` model bias + `theta_R=0.15` literal); SESSION-VARYING = per-session
  rho error + fuel variation. Split allocation documented with rationale (mass mostly SHARED).
- TOTAL systematic (shared ⊕ session-varying) reproduces `scripts/nuisance_sensitivity.py`'s budget
  (~4.3% CdA, ~3.7% P_max; braking/traction fit-sigma-dominated) within a documented tolerance. NOTE: the
  implementer reports the LIVE perturbation re-run stalled (concurrent-agent contention on shared main-checkout
  files) and used the handoff-sanctioned fallback: algebraic derivation reproducing the documented reference
  (4.3%/3.7%) exactly using the real measured Monza rho + quali_mass(2023). Judge whether that fallback is
  adequate evidence for the reproduction claim — it is acceptable IF the analytic form is independently
  unit-tested against its closed form (confirm the unit tests do this), NOT merely asserted equal to the constant.
- Unit tests SYNTHETIC + FastF1-free; suite green; telemetry-dependent validation SKIPs cleanly when DB absent.

## Allowed Scope
CREATE systematic_budget.py + its tests only. No changes to estimate_store/pooling/pool_driver/views (that is G4).

## Specific Exclusions
No production-default / circuits.yaml / gold change; no data/*.db writes; no evo import.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`.
- Honest-wide over optimistic; the SHARED component is the un-poolable common-mode (the #506 core) — verify it is
  computed and non-trivial (mass-driven), not a re-labelled copy of the total.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — new systematic_budget.py.
- Evidence: total systematic matches nuisance_sensitivity ~4.3% CdA / ~3.7% P_max on Monza RBR 2023 Q.
- Decision anchor: the shared-vs-session-varying split boundary is a load-bearing choice — flag if undocumented.

## Evidence Produced
`py -m pytest tests/unit/physics/layer2/ -q -k systematic` → 20 passed (Commander re-ran: green). The
IMPLEMENTER_RESULT carries the analytic derivations + the fallback-validation note.

## Suggested Model Tier
stronger — the review must judge the analytic-sensitivity correctness and whether the fallback validation
adequately substitutes for the stalled live perturbation.

## Stop Conditions
BLOCK if: the diff cannot be accessed; the split is a re-labelled total (shared not genuinely computed); A0/A2
carry a mass/rho systematic they physically shouldn't; or the reproduction claim rests ONLY on asserting equality
to the hard-coded constant with no independent closed-form check.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK, per-check findings, blockers, out-of-scope observations, workflow
feedback). WRITE it to `.agent-work/627-unified-basis/g1-review/REVIEW_RESULT.md` AND deliver a summary to
ShipF-627 (route to team-lead if ShipF-627 is unaddressable) via SendMessage before ending your turn.
