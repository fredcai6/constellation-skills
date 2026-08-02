# Reviewer Handoff

## Gate
g2 (store schema: cross-view covariance + explicit-unknown status)

## Survey State Location
`.agent-work/627-unified-basis/g2-review/review.json`.

## What Was Implemented
`estimate_store.py`: added `cross_view_covariance` (JSON blob, sparse dict shape
`{cov_cda_a_b, cov_cda_b_b, cov_cda_a_t, cov_cda_b_t, fused_cda:{mu,sigma}}`, in `_JSON_COLUMNS`, default None);
per-axis `{axis}_status` (resolved|unresolved, default unresolved) for cda,p_max,a_b,b_b,a_t,b_t,A0,A2,theta_R
(`AXIS_STATUS_NAMES`); `UNRESOLVED_AXIS_SIGMA_FRAC=1.0` reserved wide-σ sentinel. Migration is the existing generic
`_migrate_missing_columns` (unchanged, verified). Tests extended in `test_estimate_store.py`.

## How to Inspect the Diff
UNCOMMITTED working tree in this worktree (C:/Programs/f1-627). `git status --porcelain` then `git diff` (files:
`src/physics/layer2/estimate_store.py`, `tests/unit/physics/layer2/test_estimate_store.py`). Result:
`.agent-work/627-unified-basis/g2-implement/IMPLEMENTER_RESULT.md`.

## Task Statement
Add SCHEMA + defaults + migration + round-trip for the cross-view covariance blob and per-axis status columns +
reserved-σ sentinel — WITHOUT populating values or resolving statuses (G3/G4 do that). Full task:
`.agent-work/627-unified-basis/g2-implement/HANDOFF.md`.

## Close Criteria (each a review check)
- New fields all NULLABLE + defaulted; `cross_view_covariance` in `_JSON_COLUMNS` and round-trips through JSON.
- `{axis}_status` columns for all 9 named axes, default `unresolved`; NO real status computed here.
- Reserved wide-σ sentinel constant documented (≥100% relative; follows the power_drag_view sentinel pattern).
- BACKWARD-READ: an old-schema DB (missing the new columns) loads via `_migrate_missing_columns` (ALTER-add) with
  no "no such column"; migration test present. VERIFY the honest finding: SQLite bare `ADD COLUMN` backfills
  legacy rows with NULL (not the dataclass default) — confirm the test asserts this correctly and that a NULL
  status is a benign legacy state (G4 will treat NULL as unresolved; that is a G4 concern, not a G2 blocker).
- `error_record(...)` sets sane defaults for the new fields.
- weekend_state consumer tests stay green.

## Allowed Scope
`estimate_store.py` + `test_estimate_store.py` only. Schema/defaults/migration ONLY (no value population, no status resolution).

## Specific Exclusions
No pooling/view/weekend_state edits; no production-default/circuits.yaml/gold change; no data/*.db writes; no evo import.

## Constraints the Implementation Must Respect
- Additive migration ONLY (never drop/rename); backward-readable.
- Cross-view covariance representation = TARGETED SPARSE (dict), NOT a dense matrix (PLAN_ALTERNATIVES A1).
- `constraint:physics_region_no_evo_import`.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — `estimate_store.py::EstimateRecord/_migrate_missing_columns/_JSON_COLUMNS`.
- Constraint: backward-readable store.
- Evidence: old-schema DB reloads after ADD COLUMN migration; weekend_state consumers green.

## Evidence Produced
`py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/weekend_state/ -q` → 122 passed
(Commander re-ran: green).

## Suggested Model Tier
simple-bounded to stronger — schema, but backward-read/migration correctness is load-bearing.

## Stop Conditions
BLOCK if: a new field is non-nullable/undefaulted; the sentinel is undocumented or <100% relative; the migration
does not actually self-heal an old-schema DB; a value is populated / a status is resolved here (that is G3/G4); or
a weekend_state consumer breaks.

## Return Format
Return REVIEW_RESULT (APPROVE or BLOCK + per-check findings + workflow feedback). WRITE to
`.agent-work/627-unified-basis/g2-review/REVIEW_RESULT.md` AND deliver a summary to ShipF-627 (route to team-lead
if unaddressable) via SendMessage before ending your turn. Include the literal token APPROVE or BLOCK.
