# Implementer Handoff — g2 (reference-lap first-class product + own-DB store)

## Gate
g2-implement (issue #664, epic #659, delegated). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
Two deliverables:
1. `src/physics/utilization/reference_lap_product.py` — promote the physics-simulated ideal
   lap to a first-class product. A `ReferenceLapProduct` dataclass + a composer that, for a
   `(year, gp_name, session_type)` weekend, produces:
   - per-constructor scalar **`lap_time_s`** (the promoted, previously-discarded
     `SimulatedLap.lap_time_s` from the canonical
     `build_car_ceiling(strictly_pre=True) → PhysicsSimulator.simulate_lap` path);
   - the **circuit fingerprint** = per-class TIME-shares (via g1 `class_ledger`), computed
     as the FIELD-REFERENCE aggregate (RULING below);
   - `map_version` (from the consumed SegmentMap) + provenance + a **FIELD-BASIS descriptor**
     (which constructors/sessions defined the field reference — the fingerprint is
     field-CONDITIONED, not a pure-circuit invariant).
2. `src/physics/utilization/reference_utilization_store.py` — an OWN-db SQLite store with a
   `reference_laps` table.

## RULING (commander decision, my latitude — record, do not re-open)
**decision:field-reference-fingerprint** — the circuit fingerprint = the FIELD-MEDIAN,
across the constructors present in the weekend's ok-status estimate store, of each
constructor's simulated-lap per-class TIME-shares (stack the per-constructor share vectors,
take the per-class median, renormalize to sum 1). Each constructor's OWN scalar `lap_time_s`
is stored as its own product row. The FIELD-BASIS descriptor records the constructor/session
set the median was taken over. Rationale: a circuit fingerprint should be robust to which
single car defines it; a field-median of per-constructor shares is a robust, low-dimensionality
field aggregate that needs no cross-constructor param pooling. `@grade: guess · leans
g2-implement,g4-implement · settle: on the g4 bounded slice, confirm the field-median
fingerprint is stable when one constructor is dropped (folds into the g4 jackknife).`
If the real data makes this awkward (e.g. a weekend with one constructor), degrade gracefully
(single-constructor fingerprint = that car's shares, field-basis records n=1) and note it —
do NOT invent a new threshold.

## Protected Intent
- Anti-circularity: the ceiling is `strictly_pre=True` (target round excluded); single
  canonical ideal-lap path (`decision:c1_driver_utilization_design`) — do NOT add a second
  inline sim.
- Own-db (#632): the reference-lap store writes to its OWN db, NEVER the f1_data DBs.
- Consume the #662 SegmentMap + `map_version` AS-IS.
- Fingerprint is a TIME-share (via g1), NOT the #625 distance-share.

## Test Mode
Test-after allowed; unit tests on SYNTHETIC data + a temp DB only (never a real DB — #656).
The real end-to-end composition over live sessions is exercised in g4, NOT here — so unit-test
the fingerprint AGGREGATION (field-median-of-shares) and the store round-trip against
synthetic `SimulatedLap`-like inputs / a small synthetic SegmentMap, not a live session load.

## Close Criteria
- `ReferenceLapProduct` carries: per-constructor `lap_time_s`, the field-reference per-class
  TIME-share fingerprint (keys = g1's `(2+k)` vocabulary), `map_version`, field-basis
  descriptor (constructor/session set + n), provenance (year, gp_name, session_type).
- The fingerprint is computed via g1 `class_ledger.class_time_shares(segment_map,
  distance_profile, speed_profile)` on each constructor's simulated lap, then field-median +
  renormalize. Shares sum to 1.
- `reference_utilization_store.py`: a `SegmentMapStore`/`estimate_store`-style SQLite store
  (sqlite3.Row factory; create-on-construct unless `must_exist`; `INSERT OR REPLACE`
  idempotency; additive `_migrate_missing_columns`) with a `reference_laps` table keyed by
  `(year, gp_name, session_type, reference_id, map_version)` where `reference_id` distinguishes
  a per-constructor row from the field-reference fingerprint row (your schema choice —
  document it). Round-trips faithfully; a plain rerun never accumulates duplicate rows.
- Tests: round-trip (write→read equal), idempotent rerun (no dup rows), fingerprint shares
  sum to 1, field-median aggregation correct on a synthetic multi-constructor fixture,
  temp-DB-only.

## Allowed Scope
- CREATE `src/physics/utilization/reference_lap_product.py`,
  `src/physics/utilization/reference_utilization_store.py`,
  `tests/unit/physics/test_reference_lap_product.py`,
  `tests/unit/physics/test_reference_utilization_store.py`.
- READ-ONLY reference: `src/physics/utilization/car_prior.py`
  (`build_car_ceiling(*, store_df, year, constructor, target_round, strictly_pre, config) ->
  CarCeilingResult(params, envelope, air_density, n_sessions, as_of_means)`),
  `src/physics/physics_simulator.py`
  (`PhysicsSimulator().simulate_lap(track_profile, params, sample=False) ->
  SimulatedLap(lap_time_s, max_speed_ms, distance_profile, speed_profile)`),
  `src/physics/utilization/class_ledger.py` (g1 — the fingerprint helper),
  `src/physics/segment_map/store.py` (`SegmentMapStore.get_current(gp_name, year, weekend)`
  / `get_by_version`), `src/physics/segment_map/derivation/derive.py`
  (`derive_segment_map(...)`), `src/physics/segment_map/derivation/reference_lap.py`
  (`reference_lap_from_store(year, gp_name, session_type) -> ReferenceLap` with
  `distance_m`/`curvature` — the track profile for `simulate_lap`),
  `src/physics/layer2/estimate_store.py` (`EstimateStore(path, must_exist=True).load(year=,
  session_type=, status="ok")`), and `scripts/build_driver_utility_observables.py` (the #628
  build script — the EXACT working pattern for load_store_df → build_car_ceiling →
  simulate_lap; mirror it).

## Specific Exclusions
- NO per-driver utilization / deficits / G / energy here (that is g3).
- NO CLI / season-run / validation here (that is g4).
- NO writing to any f1_data DB or any real DB in tests.
- Do NOT touch `segment_map/*` or `car_prior`/`physics_simulator` — consume them.
- Do NOT implement the SegmentMap seeded/supersede write path — OUT of scope (it stays
  NotImplementedError).
- Mint NO new literal threshold (a float-equality tolerance like `1e-9` is fine; a physical
  threshold is a STOP-and-return float).

## Constraints
- `PhysicsParameterSet` is the `ceiling.params` passed to `simulate_lap`. `simulate_lap`'s
  `track_profile` needs columns `distance_m` + `curvature` (a DataFrame or dict) — source
  them from the `ReferenceLap` (`distance_m`, `curvature`) which is the SAME geometry the
  SegmentMap was derived from.
- The SegmentMap's `segment_of` operates on the same `distance_m` grid — pass
  `SimulatedLap.distance_profile` (== the input distances) to `class_time_shares`.
- Own-db: default the store path to an OWN db (e.g. `data/reference_utilization.db`) — NOT
  `f1_data*.db`. Tests pass an explicit temp path.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new `reference_lap_product.py` +
  `reference_utilization_store.py`; depends on `car_prior`, `physics_simulator`, g1
  `class_ledger`, `segment_map`.
- **Capability:** ideal-lap simulation (scalar `lap_time_s` promoted); circuit fingerprint
  (per-class TIME-share, retires #625 distance-share).
- **Constraints:** own-db (#632); anti-circularity (strictly_pre); db-canonical; consume
  #662 map as-is.
- **Decision anchors:**
  - `decision:c1_driver_utilization_design` — single canonical ideal-lap path.
    `@grade: settled/human`
  - `decision:field-reference-fingerprint` — field-median-of-per-constructor-shares.
    `@grade: guess · leans g2-implement,g4-implement · settle: g4 drop-a-constructor stability`
- **Evidence expectations:** fingerprint shares sum to 1; store round-trip + idempotency.

## Deliverable Path Check
- **Committed** — all four files (`reference_lap_product.py`,
  `reference_utilization_store.py`, and the two test files); confirm `git check-ignore`
  exits 1 for each before you finish. All are NEW → appear in `git status` (untracked).
- **Local-only** — the OWN db file itself (`data/reference_utilization.db`) is a data
  artifact, NOT committed; tests use a temp path.

## Required Evidence
- LOAD-BEARING: (1) store round-trip test (write→read equal); (2) idempotent-rerun test (no
  duplicate rows); (3) field-median fingerprint aggregation correct + shares sum to 1 on a
  synthetic multi-constructor fixture.
- CONFIRMATORY: single-constructor graceful degrade (n=1 field-basis); `git check-ignore`
  exit codes.
- Run: `pytest tests/unit/physics/test_reference_lap_product.py
  tests/unit/physics/test_reference_utilization_store.py -q` — paste the tail.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/test_reference_lap_product.py tests/unit/physics/test_reference_utilization_store.py -q
git check-ignore src/physics/utilization/reference_lap_product.py src/physics/utilization/reference_utilization_store.py; echo "exit $? (expect 1 = not ignored)"
```

## Suggested Model Tier
Stronger — real cross-module composition (estimate store → car_prior → simulate_lap → g1
fingerprint) + a new persistence store; several APIs to wire correctly.

## Authority
DECIDED (do not re-open): field-median-of-shares fingerprint (RULING above); own-db;
strictly_pre; single canonical sim path; fingerprint = time-share. You DECIDE: exact
dataclass/store schema, `reference_id` encoding, function names. You must NOT decide alone:
any new physical threshold (STOP + return — a float); any change to a consumed module.

## Stop Conditions
Stop and return IMPLEMENTER_RESULT if: a consumed API does not expose what this needs (report
the exact gap); you would need a new physical threshold; you cannot build the store/fingerprint
without touching a real DB in tests; or an allowed-scope boundary must be crossed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
(pytest tail + check-ignore), assumptions, stop conditions hit, out-of-scope observations,
Workflow Feedback. WRITE it to
`.agent-work/664-reference-laps/crew-results/g2-implement-result.md` AND return a tight
pointer summary as your final message.
