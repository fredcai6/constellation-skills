# Implementer Handoff — G3 (cumulative_track_laps unlock)

## Gate
`g3` (execute.json)

## Task
Land the per-car `cumulative_track_laps` unlock into `session_estimates` — the bridge #626's
within-session evolution latent is blocked on. THREE parts:
1. Add `cumulative_track_laps: Optional[int] = None` to `EstimateRecord` (`estimate_store.py`, place
   next to `mass_kg_assumed`). It auto-migrates via the existing `_migrate_missing_columns` self-heal.
2. Add a session-level compute helper `session_cumulative_track_laps(...)` reusing
   `session_race.compute_cumulative_track_laps`.
3. Populate the column via `record_from_estimate` (optional param) and a DEMO-SCOPED populate path.

## Protected Intent
Unblock #626 without a whole-store backfill. The column must self-heal on legacy stores (NULL for
existing rows) and never corrupt/rewrite existing data. Do NOT trigger a full re-pop (that is #646).

## Test Mode
TDD required (schema migration + count logic are deterministic).

## Close Criteria
- `EstimateRecord` gains `cumulative_track_laps: Optional[int] = None`; a fresh `EstimateStore` on a
  legacy store DB (one WITHOUT the column) self-heals via `_migrate_missing_columns` (add a test that
  opens a store copy lacking the column and confirms the ALTER runs + reads back NULL).
- `session_cumulative_track_laps(year, gp, session_type, constructor, db_path, *, session_id=None) ->
  Optional[int]`: finds the constructor's REPRESENTATIVE lap (its fastest clean `valid_lap=1` lap in
  that session), takes its `lap_number`, and returns `compute_cumulative_track_laps(session_id,
  that_lap_number, db_path)` — total FIELD laps (all cars) before that lap. Returns None if the
  constructor has no clean lap / session missing. DEFINITION CONFIRMED by ShipE-626 (owner of merged
  #626): rubber-at-representative-lap per constructor, FIELD laps (not the car's own laps — that is
  tyre_life, controlled separately), matching compute_cumulative_track_laps' "lap_number < anchor"
  convention so it stays on one scale with the race-side grip_bin_obs. NOTE (honest approximation): the
  estimator pools observations across MANY laps at varying track states, so a single scalar per
  (session, constructor) is anchored at the constructor's fastest clean lap as its pace anchor — document
  this approximation in the docstring.
- `record_from_estimate` accepts an optional `cumulative_track_laps: Optional[int] = None` and stores it
  (default None = byte-identical to today).
- A demo-scoped populate helper `populate_cumulative_track_laps_for_demo(store_path, db_path, weekends)`
  (or equivalent) that sets the column ONLY for the named demo weekends' rows; NULL elsewhere untouched.
- Tests green; existing estimate_store tests still pass (no behavior change for default-arg callers).

## Allowed Scope
- `src/physics/layer2/estimate_store.py` (add field + optional record param + demo populate helper).
- `src/physics/layer2/session_race.py` (add `session_cumulative_track_laps` helper; reuse
  `compute_cumulative_track_laps` — do not change it).
- Tests `tests/unit/physics/test_estimate_store.py` (extend), and a session_race test if needed.

## Specific Exclusions
- Do NOT run any real backfill / re-pop / estimate_batch over real data (#646 is separate).
- Do NOT read/modify/commit any `data/*.db` (#632) — tests use tmp/in-memory sqlite store copies.
- Do NOT touch `session_estimator.py` (G5) or the views.

## Constraints
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- The self-heal must be ADDITIVE (ALTER ADD COLUMN), mirroring `mass_kg_assumed`'s precedent exactly.
- Read-only DB access for the count (reuse `_ro_uri` pattern).

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — `estimate_store.py::EstimateRecord`,
  `session_race.py::compute_cumulative_track_laps`.
- Capability: unblocks #626 within-session evolution.
- Constraints: DB hygiene #632; demo-scoped populate not whole-store backfill.
- Decision: cumulative_track_laps definition (coordinated with ShipE-626).

## Deliverable Path Check
- Committed — `src/physics/layer2/estimate_store.py`, `src/physics/layer2/session_race.py`,
  `tests/unit/physics/test_estimate_store.py`. Tracked (src/tests). Not gitignored.

## Required Evidence
- `py -m pytest tests/unit/physics/test_estimate_store.py -q` green (paste summary).
- The self-heal-on-legacy-store test output.
- `git status --short data/` clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/test_estimate_store.py -q && git status --short data/
```

## Suggested Model Tier
`simple bounded` — schema + count, seams cited.

## Authority
The unlock design (additive column, session-representative-lap count definition, demo-scoped populate)
is DECIDED (Ship I, coordinated with ShipE-626). You choose implementation details but do not run a real
backfill or change `compute_cumulative_track_laps`.

## Stop Conditions
Stop and return if scope must be exceeded, a real backfill would be required, or the self-heal cannot be
additive.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence, assumptions, stop
conditions, out-of-scope observations, workflow feedback.
