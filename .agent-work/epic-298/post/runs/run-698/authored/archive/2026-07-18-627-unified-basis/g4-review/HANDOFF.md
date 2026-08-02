# Reviewer Handoff

## Gate
g4 (σ-honesty wiring + explicit-unknown semantics — #506 + Tier-1 #3)

## Survey State Location
`.agent-work/627-unified-basis/g4-review/review.json`.

## What Was Implemented
- `estimate_store.py`: retired `SYSTEMATIC_FLOOR`/`_apply_floor`; wired G1 `systematic_budget()` per-session into
  each `{axis}_sigma`; added 9 `{axis}_shared_sigma` columns; real `{axis}_status` predicate
  (`_axis_statuses`, `normalize_axis_status`, `effective_axis_sigma`).
- `pooling.py`: `pool_random_effects` gained `shared_floor` (default 0.0, backward-identical).
- `pool_driver.py`: `pool_store` derives + non-optionally passes the shared floor from `{axis}_shared_sigma` at every call site.
- Tests extended in `test_estimate_store.py` / `test_pooling.py` / `test_pool_driver.py`.

## How to Inspect the Diff
UNCOMMITTED working tree in this worktree (C:/Programs/f1-627). `git status --porcelain` then `git diff` (3 source
files + tests). Result (has real numbers): `.agent-work/627-unified-basis/g4-implement/IMPLEMENTER_RESULT.md`.
Local-only characterization script `.agent-work/627-unified-basis/g4-implement/characterize_g4.py` (gitignored — not a defect).

## Task Statement
Wire the data-driven systematic (#506), floor the pooled σ_μ by the shared systematic, and make explicit-unknown
status real. Full task: `.agent-work/627-unified-basis/g4-implement/HANDOFF.md`.

## Close Criteria (each a review check)
- `SYSTEMATIC_FLOOR`/`_apply_floor` retired; `{axis}_sigma` now folds the per-session `systematic_budget` total
  (fit ⊕ systematic); `{axis}_shared_sigma` persisted; no dangling `SYSTEMATIC_FLOOR` import (grep). A0/A2 off the blind 4%.
- POOLED FLOOR (the #506 core): `pool_random_effects` floors σ_μ by `shared_floor`; `pool_store` passes it
  NON-OPTIONALLY at every call site (verify no silent-unfloored path). VERIFY the honesty on real numbers: pooled
  σ_μ for CdA/P_max plateaus at the shared systematic as n grows (does NOT shrink toward 0). Reproduce the
  before/after from the result if feasible.
- EXPLICIT-UNKNOWN: `theta_R` always `unresolved`; degenerate PowerDrag → `unresolved`; absent lateral/coast →
  A0/A2/coast `unresolved`; measured CdA → `resolved`. Unresolved carries the reserved wide σ (UNRESOLVED_AXIS_SIGMA_FRAC),
  numerically ≫ a resolved σ. NULL status treated as unresolved. Confirm the PROPERTY TEST asserts the numeric
  distinction (unknown vs confident-zero), not a comment.
- weekend_state DECISION STABILITY: no unintended gate-decision flips (implementer reports 0 flips on the full
  1562-row store, verdict unchanged PASS 9/11). Confirm this is characterized, not assumed.
- weekend_state + pooling + pool_driver + estimate_store tests GREEN (implementer: 835 passed).

## Allowed Scope
`estimate_store.py`, `pooling.py`, `pool_driver.py`, tests under `tests/unit/physics/layer2/`, a local-only script.

## Specific Exclusions
No production-default / pinning-CdA / circuits.yaml / gold change; no weekend_state SOURCE change (characterize only);
no data/*.db writes; no evo import. (A stale weekend_state comment referencing SYSTEMATIC_FLOOR is a known
out-of-scope doc-drift item tc6 — note, do NOT block on it.)

## Constraints the Implementation Must Respect
- Honest-wide σ; pooled σ_μ MUST carry the shared floor (pooling cannot average away a common-mode bias).
- `{axis}_sigma` column names unchanged (meaning tightens only). Additive migration only. `constraint:physics_region_no_evo_import`.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — estimate_store.py, pooling.py::pool_random_effects, pool_driver.py::pool_store.
- Capability: data-driven systematic (#506); pooled-σ_μ shared floor; explicit-unknown status.
- Constraint: pooling cannot average away a shared bias.
- Evidence: pooled σ_μ(CdA/P_max) floored (before/after); unresolved distinguishable from confident-zero (property test).

## Evidence Produced
`py -m pytest tests/unit/physics/layer2/ tests/unit/physics/weekend_state/ -q` → 835 passed (Commander re-ran a
71-test targeted subset green; full suite is slow under contention — re-run it yourself). Result has the
pooled-floor before/after + the weekend_state 0-flip characterization.

## Suggested Model Tier
stronger — the pooled-floor honesty (must not shrink below the shared systematic) and the interlocking
status/σ semantics are the crux; scrutinize whether the floor is genuinely wired non-optionally and whether the
property test truly distinguishes unknown from confident-zero.

## Stop Conditions
BLOCK if: a call site pools without the floor (silent-unfloored path); the pooled σ_μ can still shrink below the
shared systematic; the property test does not numerically distinguish unresolved from resolved; a dangling
SYSTEMATIC_FLOOR import remains; a production default changed; a weekend_state decision flipped unintentionally; or data/*.db was written.

## Return Format
Return REVIEW_RESULT (APPROVE or BLOCK + per-check findings + workflow feedback). WRITE to
`.agent-work/627-unified-basis/g4-review/REVIEW_RESULT.md` AND deliver a summary with the literal verdict token to
ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn.
