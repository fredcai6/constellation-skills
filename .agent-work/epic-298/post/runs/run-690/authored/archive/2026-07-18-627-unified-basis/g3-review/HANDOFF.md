# Reviewer Handoff

## Gate
g3 (cross-view covariance population + redundancy demonstration — NON-DEFERRABLE)

## Survey State Location
`.agent-work/627-unified-basis/g3-review/review.json`.

## What Was Implemented
- `braking_view.py` / `traction_view.py`: `*ViewResult` gains `cda_jacobian` (the already-computed
  `cda_frontier_jacobian` J, previously discarded).
- NEW `src/physics/layer2/cross_view.py`: `fuse_dual_cda` (honest cov-aware GLS fusion of PowerDrag-CdA + Coast-CdA
  with a falsifiable agreement z; refuses when z>=5 or Σ non-PSD) + `propagate_shared_param_variance` (persisted-term-only).
- `estimate_store.py::record_from_estimate`: populates `cross_view_covariance` (`cov(CdA,[a_b,b_b])`,
  `cov(CdA,[a_t,b_t])` = σ_CdA²·J; `fused_cda` (mu,sigma)) via `_cda_jacobian_cross_terms`, `_fused_cda_inputs`,
  `_fused_cda_fields`, `_cross_view_covariance_fields`.
- Tests: NEW `test_cross_view.py` (9) + extensions to `test_braking_view.py`, `test_traction_view.py`, `test_estimate_store.py`.

## How to Inspect the Diff
UNCOMMITTED working tree in this worktree (C:/Programs/f1-627). `git status --porcelain` then `git diff`
(`cross_view.py` is untracked — shows in `git status`, not `git diff`). Result:
`.agent-work/627-unified-basis/g3-implement/IMPLEMENTER_RESULT.md` (has the before/after tables). A local-only demo
script `.agent-work/627-unified-basis/g3-implement/monza_finalize.py` is intentionally gitignored — not a defect.

## Task Statement
Persist REAL cross-view covariance and DEMONSTRATE non-tautologically that multi-view redundancy tightens a shared
param's σ, connecting the two. Full task: `.agent-work/627-unified-basis/g3-implement/HANDOFF.md`.

## Close Criteria (each a review check)
- `cda_jacobian` exposed + populated on both view results (the real J, not a re-computation).
- `cross_view_covariance` persists `cov(CdA,[a_b,b_b])` / `cov(CdA,[a_t,b_t])` = σ_CdA²·J; non-trivial + reloads.
- Fusion is HONEST cov-aware GLS (NOT naive-independent); shares the within-session mass/ρ correlation (from G1
  systematic_budget); reports falsifiable agreement z; REFUSES (fused_cda None + reason) when z>=5 or Σ non-PSD.
  VERIFY the honesty: the implementer found the raw fit-only σ makes Σ non-physical on real data and switched to
  the honest TOTAL σ before fusion (documented decision candidate tc4) — confirm this is a genuine correctness
  fix, not a way to force a pass. Confirm a NAIVE fuse would have looked falsely tighter (σ≈0.0146 vs honest ≈0.046).
- NON-TAUTOLOGICAL demo on Monza RBR 2023 Q: the honest fused CdA propagated through the PERSISTED cov(CdA,b_b/b_t)
  tightens b_b,b_t vs the single-view pin (before/after, real numbers). RBR's own pair correctly REFUSED (z=6.80);
  a legitimately-agreeing pair (z=2.03) shows the tightening. Confirm the demo USES the persisted terms (connected),
  not a disjoint inverse-variance restatement.
- Production pinning CdA UNCHANGED (fused is additive-only). No data/*.db writes. Tests green.

## Allowed Scope
`braking_view.py`, `traction_view.py`, `estimate_store.py`, new `cross_view.py`, tests under
`tests/unit/physics/layer2/`, a local-only demo script.

## Specific Exclusions
No production-default / pinning-CdA / circuits.yaml / gold change; no status resolution or SYSTEMATIC_FLOOR
replacement (that is G4); no data/*.db writes; no evo import.

## Constraints the Implementation Must Respect
- Honest-wide cov-aware fusion (naive-independent forbidden). `constraint:physics_region_no_evo_import`.
- Frozen dataclasses: new field defaulted.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — braking_view/traction_view result; power_drag_view/coast_view (read);
  estimate_store::record_from_estimate; new cross_view.py.
- Capability: cross-view covariance persistence + redundancy tightening (NON-DEFERRABLE).
- Evidence: honest fused CdA propagated through persisted cov tightens b_b,b_t on Monza (before/after); agreement z
  falsifiable (RBR refused at z=6.80).
- Map confidence flag: worktree editable-.pth trap — assert __file__ under worktree.

## Evidence Produced
`py -m pytest tests/unit/physics/layer2/test_estimate_store.py test_braking_view.py test_cross_view.py
test_traction_view.py -q` → 70 passed (Commander re-ran: green). data/ clean (Commander confirmed).

## Suggested Model Tier
stronger — the non-tautological demonstration + fusion-honesty judgment is the crux of the whole phase; scrutinize
whether the tightening is genuinely carried by the persisted covariance and whether the honest-σ switch is sound.

## Stop Conditions
BLOCK if: cross-view terms are trivial/not persisted; the demo is a tautology disconnected from the persisted
covariance; the fusion is naive-independent (understating σ) or the honest-σ switch is a pass-forcing hack rather
than a correctness fix; the production pinning CdA changed; or data/*.db was written.

## Return Format
Return REVIEW_RESULT (APPROVE or BLOCK + per-check findings + workflow feedback). WRITE to
`.agent-work/627-unified-basis/g3-review/REVIEW_RESULT.md` AND deliver a summary with the literal verdict token to
ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn.
