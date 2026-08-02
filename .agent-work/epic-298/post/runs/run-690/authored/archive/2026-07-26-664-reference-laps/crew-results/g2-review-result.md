# Review Result

## Assigned Gate
`g2-review` — issue #664 (epic #659, delegated): reference-lap first-class product + own-DB store.

## Result
`APPROVE`

## Handoff compliance
All close criteria met and independently reproduced.

1. **ReferenceLapProduct shape** — carries per-constructor `lap_time_s` (the promoted `SimulatedLap.lap_time_s` scalar, on `ConstructorLap`), the field-median per-class TIME-share `fingerprint` keyed by g1's `(2+k)` vocabulary, `map_version` (consumed as-is), a `FieldBasis` descriptor (constructors/sessions/n), and full weekend provenance. Confirmed by reading `reference_lap_product.py:118-152` + the compose test.
2. **Time-share, not distance-share, no re-implemented sim** — the fingerprint is built via g1 `class_ledger.class_time_shares` (which is `time_by_class_s / lap_time_s`, `class_ledger.py:234-235`). `compose_reference_lap_product` consumes pre-simulated `SimulatedLap`-like inputs and adds NO inline lap sim. Grep confirmed no `distance_share` and no `simulate` in the module body.
3. **Field-median aggregation** — per-class median across constructors, renormalized to sum 1. Reproduced independently: median of `(0.7,0.2,0.1)/(0.1,0.8,0.1)/(0.2,0.1,0.7)` → `(0.2,0.2,0.1)` → renorm `{a:0.4,b:0.4,c:0.2}`, sum 1.0. Single-constructor degrades to `n=1` (renorm-identity, field_basis records it) — not an error.
4. **strictly_pre seam** — the composer builds no ceiling; it consumes laps the caller produced via `build_car_ceiling(strictly_pre=True)`. It therefore cannot weaken anti-circularity; the docstring documents the caller's `strictly_pre` obligation. Correct for the g2 seam (live build is g4).
5. **Store mechanics** — `sqlite3.Row` factory, create-on-construct unless `must_exist` (raises `FileNotFoundError` before any connect), `INSERT OR REPLACE`, additive `_migrate_missing_columns`, PK `(year, gp_name, session_type, reference_id, map_version)`. Round-trip `get == product` reproduced True; 3× rerun → 2 rows (1 field + 1 constructor), no duplicate accumulation.

## Scope drift
In scope only: the 4 new files + 1 additive `.gitignore` line. Exclusions honored: no per-driver util/deficit/G/energy (g3); no CLI/season-run (g4 — composer is a pure core, live orchestration explicitly deferred); `segment_map/store.py` seeded/supersede write path UNCHANGED and still raises `NotImplementedError` (verified `store.py:154-163`); no new physical threshold literal — only `_POSITIVE_TOTAL_ATOL = 1e-12`, documented as `>0` float-hygiene, not a physical cut.

## Evidence verdict
Fully reproduced, not accepted on assertion:
- `pytest tests/unit/physics/test_reference_lap_product.py test_reference_utilization_store.py -q` → **15 passed in 0.42s** (matches claimed evidence).
- Field-median math, single-constructor degrade, store round-trip + idempotency all re-run in an independent script on a temp DB.
- `simplification_limits --paths <4 files>` → **PASS (4 files checked)** (project review-blocker check).
- Test double `_FakeLap` uses a `SimulatedLapLike` Protocol — synthetic; no live session load. Tests use `tmp_path` only.

## Code/doc quality
Minimal, cohesive, well-documented. Docstrings carry design rationale and decision-anchor references (`decision:field-reference-fingerprint`, `decision:c1_driver_utilization_design`), not deodorant. Validation messages name field/expectation (empty constructors, missing class id, degenerate all-zero field). Physics truth-anchoring present at the applicable level: field-median has an L1 analytic test; share-sum-1 is an L2 invariant; the underlying transit-time integral is g1's separately-tested core.

**Fowler pass** (12 baseline smells, `verify_fowler_pass.py` exit 0): 10 absent; **data-clumps OVERRIDDEN** — the weekend-key 4-tuple recurring across `has/get/row_count` is exactly the sibling stores' positional-key convention and mirrors the table PK 1:1; extracting a key object would break deliberate cross-store consistency (CREW_CONTEXT "match surrounding conventions"). **speculative-generality FLAGGED** — non-blocking observation below.

## Map impact verdict
- **Evidence supports claimed change:** Yes — reproduced tests back the promoted scalar + time-share fingerprint capability.
- **Constraints not violated:** own-db (#632), tests-clean-real-dbs (#656), anti-circularity, db-canonical, #662-map-as-is, time-share-not-distance-share — all honored.
- **Notes match the diff:** The inbound anchors (`struct:physics.utilization` two new modules; capability = ideal-lap scalar + time-share fingerprint; new `reference_laps` own-db table) match exactly what the diff touched.
- **Decision candidates surfaced:** `decision:field-reference-fingerprint` (guess-grade) was implemented as ruled, not revised — correct posture for a guess the reviewer does not own.
- **Durable context routed:** New own-db persistence surface is a planned Cartographer note already named in the anchors — no unrouted durable context.

## Reconciliation check
No divergence requiring Commander reconcile. No out-of-scope triage candidates surfaced.

## Blockers
- none — confirmed after full independent reproduction of all 8 close criteria; no stop-condition tripped (diff accessible, evidence reproducible, no real-DB write, time-share confirmed, no second sim, seeded path untouched, no new physical literal).

## Out-of-scope observations
- **(non-blocking) speculative-generality:** `FieldBasis.sessions` is a tuple that in g2 always holds one element `(session_type,)`, and the store records a `FORMAT_VERSION` "so a future schema evolution can branch on it". These are forward-compat hooks for capability not yet exercised. Accepted as reasonable: the field-basis descriptor is explicitly needed for the g4 drop-a-constructor jackknife (documented), the sessions-tuple is a cheap one-line hedge, and `FORMAT_VERSION` mirrors `estimate_store`'s own versioning convention. Raised for Commander awareness only.

## Workflow Feedback
- **Handoff gaps:** None material. The handoff was unusually complete — every close criterion mapped cleanly to a reproducible check, and the "reproduce yourself" side-effects were named with expected values (e.g. field-median `0.2/0.2/0.1 → 0.4/0.4/0.2`, "3 rows across 3 writes"). One tiny mismatch: the launch prompt's check #8 parenthetical `(/data/segment_maps.db)` reads as if that were the new line; the handoff body clarifies the new line is `/data/reference_utilization.db` and `segment_maps.db` is only the *sibling pattern* it should match — verified against the actual `git diff`, no issue.
- **Context rediscovered:** Had to confirm the SegmentMap seeded/supersede `NotImplementedError` lives in `segment_map/store.py` (not touched by g2's diff) rather than one of the 4 new files — the handoff named the constraint but not the file. Minor.
- **Instructions improvised around:** None. The engine, Fowler rail, and templates covered the run cleanly.
- **What would have made this easier:** Nothing concrete — this was a well-specified gate.

## Return status
`complete`
