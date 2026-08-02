# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g2-implement (issue #664, epic #659) — reference-lap first-class product + own-DB store.

## Completed slice
Both deliverables landed and green:
1. **`reference_lap_product.py`** — promotes the physics-simulated ideal lap to a first-class
   product. `ReferenceLapProduct` (+ `ConstructorLap`, `FieldBasis`) carries per-constructor
   promoted `lap_time_s`, the FIELD-MEDIAN per-class TIME-share fingerprint, `map_version`
   (consumed as-is), the field-basis descriptor (constructors/sessions/n), and provenance. Pure
   `field_median_fingerprint()` (stack per-constructor share vectors in `class_ids` order →
   per-class median → renormalize) and pure `compose_reference_lap_product()` (wires g1
   `class_time_shares` over each constructor's `SimulatedLap`). Single-constructor degrades to n=1.
2. **`reference_utilization_store.py`** — own-DB SQLite store, `reference_laps` table keyed by
   `(year, gp_name, session_type, reference_id, map_version)`. `reference_id` = constructor name
   for a per-constructor row, or the reserved `"__field__"` sentinel for the field-reference
   fingerprint row (encoding documented in the module + row `row_kind`). estimate_store-style
   conventions (sqlite3.Row, create-on-construct unless `must_exist`, `INSERT OR REPLACE`
   idempotency, additive `_migrate_missing_columns`). `write(product)` persists N constructor rows
   + 1 field row; `get(...)` round-trips faithfully; `row_count`/`has` for diagnostics.

## Scope
**Files changed:**
- `src/physics/utilization/reference_lap_product.py` (new)
- `src/physics/utilization/reference_utilization_store.py` (new)
- `tests/unit/physics/test_reference_lap_product.py` (new)
- `tests/unit/physics/test_reference_utilization_store.py` (new)
- `.gitignore` (one additive line — see scope note below)

**Specific exclusions touched:** no — no per-driver utilization (g3), no CLI/season-run/validation
(g4), no live session load in tests, no writes to any real/f1_data DB, no edits to `segment_map/*`
or `car_prior`/`physics_simulator` (consumed read-only), SegmentMap seeded/supersede write path
left as-is (`NotImplementedError`), no new physical threshold minted.

**Scope note (`.gitignore`):** added `/data/reference_utilization.db` next to its sibling own-DBs
(`/data/segment_maps.db`, `/data/driver_utility_observables.db`). The handoff's Deliverable Path
Check requires the own DB stay LOCAL-ONLY / NOT committed; it was NOT yet ignored (`check-ignore`
exit 1) while every sibling own-DB is. This is a one-line additive hygiene change directly serving
the stated requirement, matching the existing pattern — not a substantive scope crossing. Flagged
here for Commander visibility.

## Behavior changed
Yes — new capability: the ideal lap's scalar `lap_time_s` is now a persisted product (previously
discarded), and the circuit fingerprint is a persisted field-median per-class TIME-share vector.

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — two new modules
  (`reference_lap_product.py`, `reference_utilization_store.py`); depend on g1 `class_ledger`
  (`build_weight_matrix`, `class_time_shares`) and consume `SimulatedLap` + the frozen SegmentMap.
- **Capabilities added/changed:** ideal-lap simulation promoted to a first-class product (scalar
  `lap_time_s` persisted); circuit fingerprint = per-class TIME-share (field-median), the
  time-share fingerprint that supersedes the #625 distance-share.
- **Constraints/assumptions touched:** own-db (#632) honored — store defaults to
  `data/reference_utilization.db`, never an f1_data DB, now gitignored; anti-circularity
  (strictly_pre) preserved (no second inline sim — module only consumes `SimulatedLap` products);
  #662 SegmentMap + `map_version` consumed as-is.
- **Decision candidates / resolved decisions:** `decision:field-reference-fingerprint`
  implemented exactly as ruled (field-median-of-per-constructor-shares, renormalized; n=1 degrade).
  `@grade: guess · settle: g4 drop-a-constructor jackknife` — carried forward to g4 unchanged.
- **Claims/evidence produced:** fingerprint shares sum to 1 (both per-constructor and field);
  store round-trip equal + idempotent rerun (no dup rows). Backed by the 15 passing unit tests.
- **Triage candidates:** the LIVE composition (estimate store → `build_car_ceiling(strictly_pre)`
  → `simulate_lap` → `compose_reference_lap_product` → store) is intentionally NOT built here — it
  is g4's end-to-end orchestration. The pure composer is the seam g4 calls.

## Test mode
**Required:** test-after (synthetic + temp-DB only; no live session load — #656).
**Satisfied:** yes — SYNTHETIC SegmentMap (hand-built via `SegmentMap.build`) + `SimulatedLap`-like
doubles for the product tests; TEMP-DB (`tmp_path`) for the store tests. No real DB, no live load.

## Evidence

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest \
  tests/unit/physics/test_reference_lap_product.py \
  tests/unit/physics/test_reference_utilization_store.py -q
```

**Result:** pass — `15 passed in 0.42s` (7 product + 8 store).

Load-bearing evidence:
- Store round-trip (write→read equal): `test_round_trip_equal`, `test_single_constructor_product_round_trip` — PASS.
- Idempotent rerun (no dup rows): `test_idempotent_rerun_no_duplicate_rows` — PASS (3 rows stay 3 across 3 writes).
- Field-median aggregation correct + shares sum to 1: `test_field_median_aggregation_correct_and_renormalized`
  (medians 0.2/0.2/0.1 → renormalized 0.4/0.4/0.2), `test_compose_multi_constructor_shares_and_fingerprint` — PASS.
- Single-constructor graceful degrade (n=1): `test_field_median_single_constructor_is_that_car`,
  `test_compose_single_constructor_degrades_gracefully` — PASS.

`git check-ignore` exit codes:
- `reference_lap_product.py` → exit 1 (NOT ignored ✓)
- `reference_utilization_store.py` → exit 1 (NOT ignored ✓)
- `test_reference_lap_product.py` → exit 1 (NOT ignored ✓)
- `test_reference_utilization_store.py` → exit 1 (NOT ignored ✓)
- `data/reference_utilization.db` → exit 0 (IGNORED ✓ — local-only data artifact, after the `.gitignore` add)

## TDD evidence, if required
Test-after mode — not TDD-red-first. Tests written alongside each module, run green immediately
(product 7/7, store 8/8). No refactor needed.

## Docs/contracts touched
- `.gitignore` — one additive line (own-DB local-only). No doc/architecture files touched
  (Cartographer reconcile owns the map).

## Assumptions
- The pure composer takes already-simulated `SimulatedLap`-like inputs; the LIVE load→ceiling→
  simulate loop is g4's orchestration (handoff: "real end-to-end composition … is exercised in g4,
  NOT here"). Keeping the g2 seam pure is what makes the unit tests synthetic.
- `FieldBasis.sessions` is a tuple (here the single weekend `session_type`) so the descriptor
  extends to a multi-session basis without a schema change.
- The `"__field__"` `reference_id` sentinel cannot collide with a real F1 constructor name;
  documented as reserved.

## Stop conditions hit
- None. All consumed APIs exposed what was needed (g1 `class_time_shares`/`build_weight_matrix`,
  `SegmentMap.build`, estimate_store conventions). No new physical threshold required (only a
  `1e-12` positive-total float-hygiene guard, permitted by the handoff). No real DB touched.

## Out-of-scope observations
- LIVE orchestration seam for g4: call `build_car_ceiling(strictly_pre=True)` +
  `PhysicsSimulator().simulate_lap` per present constructor (mirror
  `scripts/build_driver_utility_observables.py::_process_constructor`), collect `{constructor:
  SimulatedLap}`, fetch `SegmentMapStore.get_current(...)`, then
  `compose_reference_lap_product(...)` → `ReferenceUtilizationStore.write(...)`. The g2 primitives
  are shaped to accept exactly that.
- The `decision:field-reference-fingerprint` `settle:` experiment (drop-a-constructor stability
  jackknife) folds into g4 as ruled — no action here.

## Workflow Feedback
- **Handoff gaps:** The Deliverable Path Check said the own DB is "Local-only … NOT committed" but
  did not note it wasn't yet in `.gitignore` (every sibling own-DB is). I had to discover the gap
  via `check-ignore` and make a `.gitignore` add that technically sits outside the 4-file Allowed
  Scope. A one-line "also add `/data/reference_utilization.db` to `.gitignore`" would have removed
  the scope ambiguity.
- **Context rediscovered:** none material — the handoff's Allowed Scope pointers (esp.
  `build_driver_utility_observables.py` as the exact working pattern, and the g1 helper signature)
  were precise and saved real time. `class_time_shares` returning a dict already keyed in W-column
  order was confirmed by reading g1, not stated in the handoff — minor.
- **Instructions improvised around:** engine `advance` required `--why` (non-mechanical gate) —
  expected, not a misfit. No template/skill instruction failed to cover the situation.
- **What would have made this easier:** name the `.gitignore` entry in the handoff's Deliverable
  Path Check so the own-DB "not committed" requirement is fully actionable within stated scope.

## Return status
complete
