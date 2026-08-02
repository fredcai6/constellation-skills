# Reviewer Handoff — g2 (reference-lap first-class product + own-DB store)

## Gate
g2-review (issue #664, epic #659, delegated). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Survey State Location
`.agent-work/664-reference-laps/g2-review/review.json`.

## What Was Implemented
Four new files + one additive `.gitignore` line:
- `src/physics/utilization/reference_lap_product.py` — `ReferenceLapProduct` / `ConstructorLap`
  / `FieldBasis`; `field_median_fingerprint()` (per-constructor share vectors → per-class
  median → renormalize) + `compose_reference_lap_product()` (wires g1 `class_time_shares` over
  each constructor's `SimulatedLap`; consumes SegmentMap `map_version` as-is; single-constructor
  degrades to n=1).
- `src/physics/utilization/reference_utilization_store.py` — own-DB `reference_laps` store,
  PK `(year, gp_name, session_type, reference_id, map_version)`, `reference_id="__field__"`
  sentinel for the field-reference fingerprint row vs per-constructor rows; estimate_store
  conventions.
- `tests/unit/physics/test_reference_lap_product.py` (7) + `test_reference_utilization_store.py`
  (8) — synthetic + temp-DB only.
- `.gitignore` — one additive line `/data/reference_utilization.db` (keeps the own-DB local).

## How to Inspect the Diff
UNCOMMITTED working tree in a linked worktree. `git status --porcelain` then open the new
files; `git diff .gitignore` for the one-line change. `git diff --name-only` hides untracked
files — do not rely on it.

## Task Statement
Promote `SimulatedLap.lap_time_s` to a first-class stored product + a per-class TIME-share
circuit fingerprint from a FIELD-REFERENCE car's simulated lap, in an OWN db. See the
implementer handoff at `.agent-work/664-reference-laps/crew-handoffs/g2-implement-handoff.md`
(carries the field-median RULING).

## Close Criteria (each becomes a review check)
- `ReferenceLapProduct` carries per-constructor `lap_time_s` (the promoted scalar),
  the field-reference per-class TIME-share fingerprint (keys = g1's `(2+k)` vocabulary),
  `map_version`, a FIELD-BASIS descriptor (constructor/session set + n), and provenance.
- The fingerprint is a TIME-share via g1 `class_ledger.class_time_shares` — NOT the #625
  distance-share, and NOT a second inline sim. Confirm no re-implemented lap sim.
- Field-reference aggregation = field-MEDIAN across present constructors of per-constructor
  shares, renormalized to sum 1 (per the RULING). Confirm the aggregation math + shares-sum-1.
  Single-constructor degrades to n=1 (field-basis records it) — not an error.
- The ceiling path is `strictly_pre=True` (anti-circularity) — confirm the composer does not
  weaken it (note: the LIVE build is g4; here confirm the composer's SEAM expects strictly_pre
  ceilings and does not itself relax it).
- Store: `sqlite3.Row`, create-on-construct unless `must_exist`, `INSERT OR REPLACE`
  idempotency, additive migrate; PK `(year, gp_name, session_type, reference_id, map_version)`.
  Round-trips faithfully; a plain rerun does NOT accumulate duplicate rows (reproduce the
  idempotency test).
- **Own-db discipline (#632):** the store defaults to its OWN db and NEVER writes an f1_data
  DB; tests use a TEMP db only (#656). Confirm no real-DB write anywhere in the module or
  tests.
- The `.gitignore` addition is additive and matches the sibling own-db pattern
  (`/data/segment_maps.db`) — confirm it is a single benign line, not a broad ignore.
- Re-run `pytest tests/unit/physics/test_reference_lap_product.py
  tests/unit/physics/test_reference_utilization_store.py -q` yourself → confirm 15 green.

## Allowed Scope
The four new files + the one `.gitignore` line. Read-only consumption of `car_prior`,
`physics_simulator`, `class_ledger`, `segment_map/*`, `estimate_store`.

## Specific Exclusions (flag if touched)
- NO per-driver utilization / deficit / G / energy (that is g3).
- NO CLI / season-run (g4).
- The SegmentMap seeded/supersede write path must remain `NotImplementedError` — confirm it
  was NOT implemented.
- No new PHYSICAL threshold literal (a `1e-12`/`1e-9` float-hygiene tolerance is fine).

## Constraints the Implementation Must Respect
own-db (#632); tests-clean-real-dbs (#656); anti-circularity (strictly_pre, single canonical
sim); consume #662 map as-is; time-share not distance-share.

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new `reference_lap_product.py` +
  `reference_utilization_store.py`.
- **Capability:** ideal-lap simulation (scalar promoted); circuit fingerprint (time-share).
- **Constraints:** own-db; anti-circularity; db-canonical.
- **Decision anchors:** `decision:c1_driver_utilization_design` (single canonical sim path,
  `@grade: settled/human`); `decision:field-reference-fingerprint` (field-median-of-shares,
  `@grade: guess` — a contradiction is a float-back candidate, not yours to revise).
- **Evidence expectations:** fingerprint shares sum to 1; store round-trip + idempotency.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/664-reference-laps/crew-results/g2-implement-result.md`:
`15 passed in 0.42s`; field-median correctness (0.2/0.2/0.1 → 0.4/0.4/0.2); round-trip equal;
idempotent (3 rows across 3 writes); check-ignore: 4 deliverables exit 1, own-db exit 0. The
APPROVE `review-result` you return is matched at `g2-integrate.c2`.

## Suggested Model Tier
Stronger — cross-module composition + a new persistence store; the own-db + strictly_pre +
time-share invariants are load-bearing.

## Stop Conditions
BLOCK if: the diff is inaccessible; any evidence is unverifiable; a real DB is written; a
distance-share (not time-share) fingerprint; a second inline lap sim; the seeded/supersede
path was implemented; or a new physical threshold literal was minted.

## Return Format
Return REVIEW_RESULT (verdict APPROVE/BLOCK + per-check findings + blockers + workflow
feedback). WRITE it to `.agent-work/664-reference-laps/crew-results/g2-review-result.md` AND
return a tight verdict summary as your final message.
