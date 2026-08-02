# Implementer Handoff

## Gate
g2 (store schema: cross-view covariance + explicit-unknown status — Tier-1 #1 + #3 schema)

## Task
Extend `src/physics/layer2/estimate_store.py`'s `EstimateRecord` (and schema) with the new persisted slots that
G3 (cross-view covariance) and G4 (status/σ) will populate. THIS gate only adds the SCHEMA + defaults + migration
+ round-trip — it does NOT compute cross-view terms or resolve statuses (that is G3/G4).

## Protected Intent
The store must stay BACKWARD-READABLE: an old-schema DB (built before these columns) must still load via the
existing additive `_migrate_missing_columns`, and the Phase-2 `weekend_state` consumers (which read value/`{axis}_sigma`
columns by name) must stay green. New columns are all NULLABLE with defaults.

## Test Mode
test-after allowed (schema + round-trip + migration are directly testable).

## Close Criteria
- `EstimateRecord` gains (all NULLABLE, defaulted):
  - `cross_view_covariance` — a JSON blob column (added to `_JSON_COLUMNS`) that will hold, populated in G3:
    `cov(CdA,a_b)`, `cov(CdA,b_b)`, `cov(CdA,a_t)`, `cov(CdA,b_t)`, and a fused-CdA `(mu, sigma)` slot. For THIS
    gate, define its shape (e.g. a dict) and default it to None; a helper to read/write it round-trips through JSON.
  - Per-axis status columns `{axis}_status` (TEXT, one of `resolved` | `unresolved`) for axes:
    `cda, p_max, a_b, b_b, a_t, b_t, A0, A2, theta_R`. Default `unresolved` (a later gate flips genuinely-measured
    axes to `resolved`). Do NOT compute the real status here — just the columns + default.
- Reserved high-σ sentinel: define a DOCUMENTED module-level constant (or small helper) for the reserved wide
  sigma an `unresolved` axis carries, magnitude ≥ 100% relative — FOLLOW the existing power_drag_view sentinels
  (`_CDA_UNKNOWN_SIGMA=0.4`, `_PMAX_UNKNOWN_FRAC=0.15`) as the pattern — so an unresolved axis down-weights to ~0
  in any inverse-variance consumer. The numeric wide-σ AND the explicit status TOGETHER carry the "unknown vs
  confident-zero" distinction. (G4 applies it; here just define + document the mechanism and unit-test it exists.)
- `_migrate_missing_columns` ALTER-adds every new column to an OLD-schema DB (it already iterates
  `EstimateRecord` fields — confirm the new fields flow through). Never drop/rename.
- Tests in `tests/unit/physics/layer2/test_estimate_store.py` (extend it): (a) a record with the new fields
  round-trips (upsert → load → equal); (b) build a DB with an OLD `EstimateRecord` field set (simulate by creating
  a table WITHOUT the new columns, or reuse the existing migration test pattern), then open it with the current
  `EstimateStore` and confirm `_migrate_missing_columns` adds the columns and `load()` succeeds (no "no such
  column"); (c) the reserved-σ sentinel constant exists and is ≥100% relative / matches the documented pattern.

## Allowed Scope
- EDIT `src/physics/layer2/estimate_store.py` (EstimateRecord fields, `_JSON_COLUMNS`, helpers, `error_record`
  defaults for the new fields).
- EDIT `tests/unit/physics/layer2/test_estimate_store.py`.
- READ-ONLY: `src/physics/layer2/power_drag_view.py` (the sentinel pattern), `src/physics/weekend_state/layer1_physics.py`
  (to confirm consumers read columns by name — do not change them).

## Specific Exclusions
- Do NOT populate cross-view covariance values (G3) or resolve statuses (G4) — schema + defaults ONLY.
- Do NOT modify `pooling.py`/`pool_driver.py`/views/weekend_state.
- Do NOT change production defaults, circuits.yaml, gold. No data/*.db writes.

## Constraints
- Additive migration ONLY (never drop/rename); backward-readable.
- `constraint:physics_region_no_evo_import`. ASCII; `py` launcher.
- `error_record(...)` must set sane defaults for the new fields (status='unresolved' fits an error row).

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — `estimate_store.py::EstimateRecord/_migrate_missing_columns/_JSON_COLUMNS`.
- Capability: per-session estimate store schema.
- Constraints: backward-readable store (pre-ruling #4).
- Decision anchor: cross-view covariance representation = TARGETED SPARSE cross-terms (a dict of the recoverable
  CdA↔{braking,traction} terms + fused-CdA), NOT a dense full-basis matrix (see PLAN_ALTERNATIVES A1). Persist the
  sparse shape.
- Evidence: old-schema DB reloads after ADD COLUMN migration; weekend_state consumers green.

## Deliverable Path Check
- Committed — `src/physics/layer2/estimate_store.py` (edit, tracked). `tests/unit/physics/layer2/test_estimate_store.py` (edit, tracked).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/weekend_state/ -q` — full pass; paste tail.
- The migration test output showing an old-schema DB loads after the columns are ALTER-added.

## Verification Commands
```bash
cd /c/Programs/f1-627
py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/weekend_state/ -q
```

## Suggested Model Tier
simple-bounded to stronger — schema work, but the backward-read/migration correctness is load-bearing.

## Authority
Tier/scope frozen by the launch order. You decide the exact field names + the cross_view_covariance dict shape
(document it so G3 can populate it). You must NOT populate values, resolve statuses, or touch anything outside scope.

## Worktree Isolation (CRITICAL)
cwd MUST be `C:/Programs/f1-627`. Before any run assert
`py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"` prints under `C:\Programs\f1-627`.
Tests are cwd-safe. No untracked data needed for this gate (pure schema/round-trip on temp DBs).

## Stop Conditions
Stop and return if: scope must be exceeded, a consumer would break and cannot be kept green with additive-only
changes, or a decision beyond field-naming/shape is needed.

## Return Format
Write `IMPLEMENTER_RESULT` to `.agent-work/627-unified-basis/g2-implement/IMPLEMENTER_RESULT.md` AND deliver a
summary to ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn: completed
slice, files changed, the cross_view_covariance dict shape you chose, test tail, migration evidence, assumptions,
stop conditions, out-of-scope observations, workflow feedback.
