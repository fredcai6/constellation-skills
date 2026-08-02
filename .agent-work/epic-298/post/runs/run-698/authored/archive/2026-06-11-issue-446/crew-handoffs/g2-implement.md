# Implementer Handoff

## Gate
g2 — Offline loaders + strawman candidate + runner

## Task
Add the IO + wiring layer to `src/preprocessing/trajectory_grading/`, on top of g1's pure core
(commit 579dbca). Four deliverables:

1. **Offline raw-stream loader** — load a session from the offline FastF1 cache and expose the
   RAW per-driver streams only. Use `fastf1.Cache.enable_cache('C:/Programs/f1Brainz/outputs/cache')`
   (absolute path — the cache is untracked, NOT in this worktree). Read `session.car_data[driver]`
   (Speed/RPM/.../SessionTime) and `session.pos_data[driver]` (X/Y/Z/Status/SessionTime) ONLY.
   NEVER call `session.get_telemetry()` or `lap.get_telemetry()` in the loader. The loader must
   not re-pull (offline cache only); if a session isn't cached, raise a clear error naming the
   session — do not fetch.

2. **DB truth loader** — load per-lap per-sector split DURATIONS (sector1/2/3_time, seconds) and
   lap_time from the season DB. Use the existing `DatabaseManager` from `src/data/database`.
   Season DBs are at absolute paths `C:/Programs/f1Brainz/data/f1_data_<year>.db` (untracked, not
   in the worktree) — instantiate `DatabaseManager(db_path=<absolute path>)`. Find the right
   `session_id` (the `sessions` table has year/round_num/gp_name/session_type; helper
   `get_lap_times(session_id=..., driver_id=...)` returns the sector columns). IMPORTANT: prefer a
   READ-ONLY access pattern — `DatabaseManager.__init__` ensures schema (a write). To stay truly
   read-only against the canonical DBs, either open the DB with a read-only sqlite connection
   (`file:...?mode=ro` URI) for the lap_times query, OR document explicitly why the
   DatabaseManager schema-ensure on an already-current DB is a safe no-op. Pick one and justify it
   in the result. Truth comes from the DB, never from fastf1.

3. **Strawman candidate** — the DELIBERATE strawman. This is the ONE place the merged product is
   allowed: wrap FastF1's merged `lap.get_telemetry()` (or `session.car_data`+`pos_data` merged via
   FastF1's own interpolation) as a candidate trajectory implementing g1's candidate contract.
   Derive `s(t)` (arc length from the merged X/Y position, cumulative) and a DELIBERATELY NAIVE
   covariance (e.g. a flat assumed position variance) — the point is that this covariance is NOT
   honest, so the harness should expose it. Add a clear module docstring stating this is the
   strawman / artifact-under-study and why `get_telemetry()` is used here and nowhere else.

4. **Runner** — given (year, gp, session_type, drivers, db_path, cache_path), build the strawman
   candidate, load DB truth, run all three g1 primitives, assemble the g1 JSON report, and write it
   to a caller-specified path. Return the report object too.

## Protected Intent
The harness reads RAW streams only; the merged product is confined to the strawman. Offline, no
re-pull, no DB writes to the canonical DBs. The runner must produce a schema-valid g1 report.

## Test Mode
Test-after allowed (this is IO/wiring). One integration test on a real cached session.

## Close Criteria
- Loader, truth loader, strawman, runner all exist in `src/preprocessing/trajectory_grading/`.
- `grep -rn get_telemetry src/preprocessing/trajectory_grading/` shows it ONLY inside the strawman
  module (and that module's docstring justifies it).
- Integration test `tests/integration/test_trajectory_grading_runner.py`: loads ONE small cached
  session offline (e.g. 2023 Belgium Qualifying — verified cached), runs the runner for a couple of
  drivers, asserts the report is schema-valid and that all three primitives produced output (the two
  gates have pass/fail verdicts; the diagnostic has fitted offsets). It need not assert the strawman
  PASSES — only that the harness runs end to end and emits a valid report.
- `py -m pytest tests/integration/test_trajectory_grading_runner.py -q` GREEN.
- `py -m src.utils.simplification_limits` passes on touched paths.
- Loading prints/logs "Using cached data" (offline) and performs no canonical-DB writes.

## Allowed Scope
`src/preprocessing/trajectory_grading/` (new loader/truth/strawman/runner modules),
`tests/integration/test_trajectory_grading_runner.py` (new).

## Specific Exclusions
- No re-pull / network fetch. No `get_telemetry()` outside the strawman.
- No touch to evo modules, `windowed_estimator.py`, `src/physics/`, or the g1 pure core's contract
  (consume it; don't change its signatures unless strictly required — if so, report why).
- No estimator/filter work.

## Constraints
- Raw streams only in the harness; merged `get_telemetry()` allowed ONLY inside the strawman.
- Offline cache only — `fastf1.Cache.enable_cache(<absolute cache path>)`; never re-pull.
- Sector/lap truth from the DB via `DatabaseManager`, read-only against canonical DBs.
- Physics region only: NO imports from `src/evo_predictor`, `src/latent_power`, `src/compound_prior`.
- Absolute paths into the main checkout for cache + DBs (they are untracked, not in this worktree).
- `py`, never `python`. Tests via `py -m pytest`. Set utf-8 in any captured subprocess env.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing.trajectory_grading` (loaders+runner+strawman);
  `struct:fastf1_api` (offline cache, raw car_data/pos_data); `struct:sqlite_db` (lap_times truth);
  `struct:data` (DatabaseManager read interface).
- **Capability:** trajectory grading — end-to-end wiring + strawman candidate.
- **Constraints/assumptions:** DB-only (Phase-0 narrowed cache exception, truth from DB);
  physics-region-isolation; pre-ruling 2 (raw streams only; strawman is the merged-product exception).
- **Decision anchors:** anchor-acquisition for the run — co-estimate from truth (g1 already does this).
- **Evidence expectations:** read-only/no-repull (offline load logs "Using cached data", no DB writes);
  harness runs end-to-end on a real cached session.

## Required Evidence
- `py -m pytest tests/integration/test_trajectory_grading_runner.py -q` output (green).
- `py -m src.utils.simplification_limits <touched paths>` output (pass).
- `grep -rn get_telemetry src/preprocessing/trajectory_grading/` output (confined to strawman).
- A note confirming the offline load logged "Using cached data" and the read-only DB approach used.

## Verification Commands
```bash
py -m pytest tests/integration/test_trajectory_grading_runner.py -q
py -m src.utils.simplification_limits src/preprocessing/trajectory_grading tests/integration/test_trajectory_grading_runner.py
```

## Suggested Model Tier
stronger — reason: FastF1 offline-cache mechanics, raw-vs-merged discipline, read-only DB pattern,
and arc-length derivation all have correctness traps.

## Authority
Loader/strawman/runner structure, arc-length derivation, and the naive-covariance form are yours to
decide within constraints. You may NOT: re-pull telemetry, use `get_telemetry()` outside the strawman,
write to canonical DBs, cross into data/evo regions for anything but the DatabaseManager read, or add
estimator logic. Surface anything needing those.

## Stop Conditions
Stop and return if: a chosen cached session turns out not to have usable raw car_data/pos_data (report
which sessions DO); scope must be exceeded; an exclusion must be touched; a decision outside authority
is needed.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/issue-446/crew-handoffs/g2-implement-RESULT.md`: completed
slice, files changed, test mode satisfied, evidence (paste green integration test + simplification
limits + the get_telemetry grep), the read-only-DB approach used and its justification, assumptions,
stop conditions hit, out-of-scope observations, workflow feedback.
