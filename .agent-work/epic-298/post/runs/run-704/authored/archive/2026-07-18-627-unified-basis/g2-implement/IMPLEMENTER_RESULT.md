# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g2 (store schema: cross-view covariance + explicit-unknown status — Tier-1 #1 + #3 schema)

## Completed slice
Extended `EstimateRecord` + `EstimateStore` schema with the new NULLABLE persisted slots G3/G4
will populate: a `cross_view_covariance` sparse-dict JSON column, per-axis `{axis}_status`
columns (default `"unresolved"`) for the 9 named axes, and a documented reserved wide-sigma
sentinel constant. No cross-view values computed, no statuses resolved — schema + defaults +
migration + round-trip only, per the gate's Specific Exclusions.

## Scope
**Files changed:**
- `src/physics/layer2/estimate_store.py`
- `tests/unit/physics/layer2/test_estimate_store.py`

**Specific exclusions touched:** no. Did not compute cross-view covariance values, did not
resolve any axis status, did not touch `pooling.py`/`pool_driver.py`/views/weekend_state, no
`data/*.db` writes (all tests use `tmp_path`).

## Behavior changed
Yes, additively. `EstimateRecord` gained 10 new fields (all `Optional`, all defaulted):
- `cross_view_covariance: Optional[dict] = None`
- `cda_status`, `p_max_status`, `a_b_status`, `b_b_status`, `a_t_status`, `b_t_status`,
  `A0_status`, `A2_status`, `theta_R_status`: `Optional[str] = "unresolved"`

`_JSON_COLUMNS` gained `"cross_view_covariance"` so it (de)serializes through `upsert`/`load`
like the other covariance blobs. `error_record(...)` now explicitly sets `cross_view_covariance=None`
and every `{axis}_status="unresolved"`. `_migrate_missing_columns` already iterates
`EstimateRecord.__dataclass_fields__` generically, so the new columns ALTER-add on an old-schema
DB with zero code change to the migration loop itself — confirmed by test, not just inferred.

Two new module-level constants for downstream gates:
- `_CROSS_VIEW_COVARIANCE_KEYS` — documents the 5 sparse keys.
- `AXIS_STATUS_NAMES` — the 9 axis name strings (`("cda", "p_max", "a_b", "b_b", "a_t", "b_t",
  "A0", "A2", "theta_R")`), reused by tests and available for G4/consumers to iterate.
- `UNRESOLVED_AXIS_SIGMA_FRAC = 1.0` — the reserved wide-sigma sentinel (>= 100% relative).

## cross_view_covariance dict shape chosen

A sparse dict, decision-anchored to PLAN_ALTERNATIVES A1 (targeted sparse cross-terms, NOT a
dense full-basis matrix):

```python
{
    "cov_cda_a_b": <float | None>,   # cov(CdA, brake_decel_ms2)           -- braking frontier A
    "cov_cda_b_b": <float | None>,   # cov(CdA, brake_aero_decel_per_m)    -- braking frontier B
    "cov_cda_a_t": <float | None>,   # cov(CdA, traction_accel_ms2)        -- traction frontier A
    "cov_cda_b_t": <float | None>,   # cov(CdA, traction_aero_accel_per_m) -- traction frontier B
    "fused_cda": {"mu": <float | None>, "sigma": <float | None>},  # fused-CdA posterior
}
```

Rationale for field names: `cov_cda_{axis}` mirrors the handoff's literal list
(`cov(CdA,a_b)`, `cov(CdA,b_b)`, `cov(CdA,a_t)`, `cov(CdA,b_t)`) using the existing in-record
short names for the braking/traction frontier params (`a_b`≈`brake_decel_ms2`,
`b_b`≈`brake_aero_decel_per_m`, `a_t`≈`traction_accel_ms2`, `b_t`≈`traction_aero_accel_per_m` —
same short-name convention the handoff itself uses for the axis-status list). `fused_cda` is a
nested `{mu, sigma}` dict rather than a flat pair of top-level keys, matching the
`ParamPrior(mu, sigma)` shape already used elsewhere in this module (e.g. `cda_closed`). The
whole column defaults to `None` (no fusion attempted); when populated, individual keys MAY still
be `None` if a particular cross-term is unrecoverable for that session — this gate does not
enforce all-or-nothing completeness on the dict, only reserves the shape. Documented in a
module-level comment directly above `_JSON_COLUMNS` in `estimate_store.py` so G3 has the exact
contract without re-deriving it.

## Map Impact

- **Structural anchors touched:** `struct:physics.layer2` — `estimate_store.py::EstimateRecord`
  gained `cross_view_covariance` + 9 `{axis}_status` fields; `_JSON_COLUMNS` gained one entry;
  `_migrate_missing_columns` unchanged (already generic over `EstimateRecord` fields) but now
  provably covers the new columns (see migration test below); `error_record` unchanged in
  signature, extended in body.
- **Capabilities added/changed/affected:** none yet observable — the new columns are inert
  (always `None`/`"unresolved"` from this gate's own code paths); G3/G4 are what make them
  observable as real capability.
- **Constraints/assumptions touched:** backward-readable store (pre-ruling #4) — honored and
  now covered by a NEW explicit test (`test_migration_adds_cross_view_and_status_columns_backward_readable`)
  that a pre-#627 DB self-heals via `_migrate_missing_columns` and `load()` succeeds with no
  "no such column" error.
- **Decision candidates / resolved decisions:** the `cross_view_covariance` dict shape (above)
  and the `AXIS_STATUS_NAMES` short-name mapping are now the frozen contract G3/G4 build against
  — flag if a future gate wants different key names, since changing them here would be a
  backward-compat break for any G3/G4 work already coded against this shape.
- **Trust limitations / drift found:** none found; `weekend_state` consumers read columns by
  name only for the pre-existing value/`{axis}_sigma` columns (grep-confirmed, see Assumptions)
  and do not touch the new columns at all, so no coupling risk from this gate.
- **Triage candidates:** none raised — see Out-of-scope observations below for one minor
  observation that isn't a defect.

## Test mode
**Required:** test-after (per handoff: "schema + round-trip + migration are directly testable")
**Satisfied:** yes — 15 new tests added (3 for cross_view_covariance, 3 for axis status, 1 for
the sentinel constant, 1 migration test, plus supporting assertions), all green alongside the
full pre-existing suite.

## Evidence

```bash
cd /c/Programs/f1-627
py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/weekend_state/ -q
```

**Result:** PASS — tail:

```
tests\unit\physics\layer2\test_estimate_store.py ....................... [ 18%]
.........                                                                [ 26%]
tests\unit\physics\weekend_state\test_floor_reproduction.py ............ [ 36%]
                                                                         [ 36%]
tests\unit\physics\weekend_state\test_gate_f6.py .............           [ 46%]
tests\unit\physics\weekend_state\test_gate_spec.py .........             [ 54%]
tests\unit\physics\weekend_state\test_holdout_split.py ....              [ 57%]
tests\unit\physics\weekend_state\test_layer1_physics.py ................ [ 70%]
..                                                                       [ 72%]
tests\unit\physics\weekend_state\test_layer2_evolution.py ............   [ 81%]
tests\unit\physics\weekend_state\test_layer3_fieldcar.py .........       [ 89%]
tests\unit\physics\weekend_state\test_model.py .............             [100%]

============================ 122 passed in 36.17s =============================
```

(32 tests in `test_estimate_store.py`, up from 17 pre-existing + 15 new; 90 tests across the
`weekend_state` suite, unaffected.)

## Migration evidence

New test `test_migration_adds_cross_view_and_status_columns_backward_readable` (in
`tests/unit/physics/layer2/test_estimate_store.py`):
1. Builds a legacy `session_estimates` table with only 6 columns (`_make_legacy_table`, the
   existing pre-Task-6 fixture pattern), inserts one row (`year=2023, gp_name="Spa",
   constructor="RB"`).
2. Opens it via `EstimateStore(db)` — `_migrate_missing_columns` runs on `__init__`.
3. Confirms via `PRAGMA table_info` that `cross_view_covariance` and all 9 `{axis}_status`
   columns now exist on the table.
4. `store.load(year=2023)` succeeds (no `sqlite3.OperationalError: no such column`); the
   pre-existing legacy row's new columns read back as `None` — SQLite's bare `ALTER TABLE ADD
   COLUMN "{c}"` (no `DEFAULT` clause) backfills existing rows with `NULL`, not the Python
   dataclass default `"unresolved"`. Asserted explicitly rather than assumed, per the handoff's
   own framing of this nuance.
5. A row upserted AFTER migration (through `record_from_estimate`/`upsert`, which supplies the
   Python-side default at write time) DOES read back `"unresolved"` for every axis status and
   `None` for `cross_view_covariance` — confirming the schema is usable going forward even
   though pre-existing rows stay `NULL` until re-fit.

Full command output above (`122 passed`) is the required-evidence proof this doesn't regress
`weekend_state`.

## TDD evidence, if required
Test mode is test-after (handoff-declared), not TDD red/green. Each of the 4 plan steps wrote
its tests alongside/after the schema change and confirmed pass before advancing the engine gate
(engine-journaled `attest`/`advance` sequence in `.agent-work/627-unified-basis/g2-implement/PLAN.json`).

## Docs/contracts touched
- None outside the two changed files. The `cross_view_covariance` shape and
  `UNRESOLVED_AXIS_SIGMA_FRAC` mechanism are documented in-module (comments directly above the
  relevant code in `estimate_store.py`), following the file's existing convention (e.g.
  `SYSTEMATIC_FLOOR`, `_RHO_INFLATION` docstrings) rather than a separate doc file.

## Assumptions
- The axis short names (`a_b`, `b_b`, `a_t`, `b_t`, `A0`, `A2`, `cda`, `p_max`, `theta_R`) map
  onto existing `EstimateRecord` fields as: `cda`→`drag_area_closed_m2`/PowerDrag CdA,
  `p_max`→`max_power_w`, `a_b`→`brake_decel_ms2`, `b_b`→`brake_aero_decel_per_m`,
  `a_t`→`traction_accel_ms2`, `b_t`→`traction_aero_accel_per_m`, `A0`→`lateral_mech_grip_g`,
  `A2`→`lateral_aero_grip_g`, `theta_R`→ rolling-resistance/coast coefficient (no existing
  record field is literally named `theta_R`; `theta_R_status` is reserved for whatever gate
  wires the rolling-resistance nuisance's resolution state — this gate only reserves the status
  column, it does not assert which value column it eventually pairs with). This mapping is my
  documented interpretation of the handoff's axis list against the codebase's existing naming;
  flagged here in case G3/G4 need a different pairing.
- `UNRESOLVED_AXIS_SIGMA_FRAC = 1.0` (exactly 100% relative, not further above) — chosen as the
  minimum value satisfying "magnitude >= 100% relative" from the handoff, keeping headroom for
  a future gate to raise it if empirically needed, rather than picking an arbitrarily larger
  number now with no measurement backing it (mirrors the existing file's practice of citing a
  measured/reasoned number, e.g. `_RHO_INFLATION = 0.05` "half the ~4% measured systematic").
- Confirmed (grep) that `src/physics/weekend_state/layer1_physics.py` reads `{axis}_sigma` and
  value columns by name (e.g. `sigma_col = f"{axis}_sigma"`) and does NOT reference
  `cross_view_covariance` or any `{axis}_status` column — so this gate cannot have broken that
  consumer; the 90 passing `weekend_state` tests confirm it empirically too.

## Stop conditions hit
None. No scope exceeded, no consumer broken, no decision beyond field-naming/shape was needed.

## Out-of-scope observations
- `scripts/migrate_estimate_store_metadata.py` (a standalone migration script, referenced by
  `test_migration_adds_columns_and_is_idempotent` via its own `_NEW_COLUMNS` list) is a SEPARATE
  migration path from `EstimateStore._migrate_missing_columns` and does NOT include the new g2
  columns. It was out of the allowed scope (not `estimate_store.py` or the test file) and its
  own existing test still passes unaffected (it only asserts its own `_NEW_COLUMNS` list, which
  I did not touch). If that standalone script is meant to stay in sync with `EstimateRecord`
  going forward, a follow-on issue may be worth filing — flagging for Commander/Cartographer
  triage rather than acting on it.

## Workflow Feedback

- **Handoff gaps:** none blocking. One minor ambiguity: the handoff's axis list uses short names
  (`a_b`, `b_b`, `a_t`, `b_t`, `A0`, `A2`, `theta_R`) that aren't literal `EstimateRecord` field
  names today (the record uses `brake_decel_ms2`, `lateral_mech_grip_g`, etc.) — I inferred the
  mapping (documented above under Assumptions) rather than being blocked, since the handoff was
  explicit that "you decide the exact field names + the cross_view_covariance dict shape." Worth
  confirming the mapping holds when G3/G4 arrive, since a status column paired with the wrong
  value column would be silently wrong rather than loudly wrong.
- **Context rediscovered:** none beyond normal reading — the `power_drag_view.py` sentinel
  pattern and `weekend_state/layer1_physics.py` consumer-by-name behavior were both exactly
  where the Map Anchors said to look.
- **Instructions improvised around:** none — the gated-plan template's per-step
  precondition/postcondition/attest/advance loop mapped cleanly onto the handoff's 4 close
  criteria without needing any deviation.
- **What would have made this easier:** none — the handoff was unusually precise (down to
  naming the exact existing sentinel constants to pattern-match), which made the field-naming
  judgment calls fast and low-risk.

## Return status
complete
