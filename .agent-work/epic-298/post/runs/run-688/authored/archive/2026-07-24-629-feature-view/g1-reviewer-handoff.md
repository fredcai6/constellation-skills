# Reviewer Handoff — G1

## Gate
`g1`

## Survey State Location
Create your review survey checklist at
`.agent-work/629-feature-view/g1-review/review.json`.

## What Was Implemented
A new component `src/physics/feature_view/` (`__init__.py`, `records.py`, `store.py`) — the
Phase-5 feature-view store foundation for issue #629 — plus
`tests/unit/physics/feature_view/` (`test_records.py`, `test_store.py`,
`test_append_only_contract.py`, `test_as_of_leakage.py`, 27 tests total). `records.py` defines
four frozen dataclasses (`WeekendStateRecord`, `CarBasisPosteriorRecord`, `LapEvidenceRecord`,
`FeatureViewRow`) plus `SESSION_ORDER`/`session_ordinal`. `store.py` defines `FeatureViewStore`
(SQLite-backed, `data/feature_view.db` default) with append-only insert methods and a
`load_as_of` method that is the by-construction as-of-leakage-prevention surface.

## How to Inspect the Diff
Uncommitted working tree in `C:/Programs/f1-629` (branch `feat/629-feature-view`) — use
`git status --porcelain` then `git diff` / read the new files directly (all files are new,
untracked; `git diff` alone won't show untracked additions). Read:
`src/physics/feature_view/records.py`, `src/physics/feature_view/store.py`,
`tests/unit/physics/feature_view/test_append_only_contract.py`,
`tests/unit/physics/feature_view/test_as_of_leakage.py`.

## Task Statement
Build the Phase-5 store foundation: 4 record dataclasses (MODEL_VERSION-keyed), a
SQLite-backed `FeatureViewStore` that is APPEND-ONLY (plain INSERT, never INSERT OR REPLACE —
a deliberate divergence from the existing `EstimateStore.upsert` idiom in
`src/physics/layer2/estimate_store.py`), and the two load-bearing gate tests using synthetic
fixtures: (1) append-only contract-freeze (a MODEL_VERSION bump never mutates a prior row,
proven via a real `sqlite3.IntegrityError` on duplicate-key insert) and (2) as-of leakage
prevention BY CONSTRUCTION (a query "as of post-FP1" cannot see FP2/FP3/Q — proven by
inspecting the actual SQL WHERE-clause text every as-of read issues, not just by checking the
returned rows or the bound parameters, plus a negative-control broken query the check must
correctly reject). Full task detail: `.agent-work/629-feature-view/g1-implementer-handoff.md`.
Full implementer evidence: `.agent-work/629-feature-view/g1-implementer-result.md`.

## Close Criteria
- `src/physics/feature_view/{__init__,records,store}.py` exist; grep confirms zero
  `evo_predictor` import anywhere in the package.
- The append-only test genuinely proves append-only: re-derive whether a lazier
  implementation (e.g. `INSERT OR REPLACE`, or a UNIQUE constraint missing `model_version`
  from its key) would still pass this test — it must NOT.
- The as-of leakage test genuinely proves by-construction, not happy-path luck: construct (or
  confirm the implementer's own negative control constitutes) a case where a buggy
  implementation WOULD leak a later session's data, and confirm the test's check would catch
  it. Specifically verify: does the WHERE-clause-structure assertion actually inspect SQL TEXT
  (not just bound params)? Would a `SELECT * FROM weekend_state_records WHERE constructor=?`
  query (session-unfiltered, filtered in Python afterward) pass or fail the check?
- `py -m pytest tests/unit/physics/feature_view -q` passes (27 tests expected — reproduce the
  count, don't take it on faith).
- The three reserved-slot fields (`process_noise_link`, `parc_ferme_step` on
  `CarBasisPosteriorRecord`; `unit_class_residuals` on `LapEvidenceRecord`) are never
  computable to a non-None value anywhere in this gate's code — confirm the `__post_init__`
  guards the implementer added actually raise on a non-None attempt (read the test coverage or
  try it yourself).
- `git check-ignore src/physics/feature_view/store.py` exits 1 (not ignored — committable).
- No file outside `src/physics/feature_view/` or `tests/unit/physics/feature_view/` was
  touched (this gate's exclusive scope this run).

## Allowed Scope
New directory `src/physics/feature_view/` (all files); new directory
`tests/unit/physics/feature_view/` (all files). Nothing else.

## Specific Exclusions
No edits to `src/physics/layer2/`, `src/physics/weekend_state/`, or any existing file. No new
data written to `data/physics_estimates.db` or any committed DB path (tests must use `tmp_path`).

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import` — no `src.evo_predictor` import anywhere in the
  new package.
- Append-only: plain INSERT enforced by a real `UNIQUE` constraint + `sqlite3.IntegrityError`,
  not a docstring-only claim.
- Reuse (import, not reimplement) `effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC`/
  `normalize_axis_status` from `src.physics.layer2.estimate_store_fields`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.feature_view` (new component).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** new-component-vs-layer2-module-leaf — already resolved at plan; not
  this gate's decision to revisit, but flag if the implementation quietly drifts toward
  reimplementing layer2 machinery instead of importing it.
- **Evidence expectations:** the two gate tests ARE the append-only + as-of-leakage claims.

## Evidence Produced
See `.agent-work/629-feature-view/g1-implementer-result.md` for the implementer's full pasted
evidence (pytest output, IntegrityError traceback, captured SQL statement list, git
check-ignore exit codes, simplification_limits attempt). The commander independently re-ran
`py -m pytest tests/unit/physics/feature_view -q` and confirmed 27 passed, and independently
read `records.py`/`store.py` source. Attach your REVIEW_RESULT to `g1-review` (and it will
also be referenced at `g1-integrate.c2`).

## Suggested Model Tier
Stronger (Sonnet) — the by-construction claim needs adversarial verification, not a surface
read.

## Stop Conditions
Stop and return BLOCK if: the leakage test can be shown to pass under a bypass you can
construct; the append-only guarantee is not actually enforced by a real DB constraint;
evidence is absent or unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
