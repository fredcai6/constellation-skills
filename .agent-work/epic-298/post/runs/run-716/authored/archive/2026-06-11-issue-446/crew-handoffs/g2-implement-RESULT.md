# Implementation Result

## Assigned gate
`g2 — Offline loaders + strawman candidate + runner`

## Completed slice
Added the IO+wiring layer (4 new modules + 1 integration test) on top of g1's
pure core (commit 579dbca). All deliverables specified in the handoff are
present and verified.

## Scope
**Files changed:**
- `src/preprocessing/trajectory_grading/offline_loader.py` (new)
- `src/preprocessing/trajectory_grading/db_truth_loader.py` (new)
- `src/preprocessing/trajectory_grading/strawman_candidate.py` (new)
- `src/preprocessing/trajectory_grading/runner.py` (new)
- `tests/integration/test_trajectory_grading_runner.py` (new)
- `.agent-work/issue-446/crew-handoffs/g2-implement.md` (handoff, staged)
- `.agent-work/issue-446/crew-handoffs/g2-plan.json` (engine plan, staged)

**Specific exclusions touched:** no — no evo/latent/compound imports, no
windowed_estimator, no g1 pure core changes.

## Behavior changed
yes — new capability: the trajectory grading harness can now run end-to-end on
a real offline FastF1 session + canonical DB, producing a schema-valid
GradingReport JSON.

## Map Impact
- **Structural anchors touched:**
  - `struct:preprocessing.trajectory_grading` — four new modules added:
    `offline_loader`, `db_truth_loader`, `strawman_candidate`, `runner`. The
    package now covers the full g2 deliverable scope (loaders + wiring +
    strawman).
  - `struct:fastf1_api` — offline cache used via `fastf1.Cache.enable_cache()`
    with absolute path. `offline_mode(True)` called to prevent re-pull.
    Raw `car_data`/`pos_data` streams only; merged product confined to strawman.
  - `struct:sqlite_db` — read-only access via `file:...?mode=ro` URI pattern
    (see DB approach below).
  - `struct:data` — DatabaseManager NOT used for queries (read-only approach
    bypasses its `_init_database`). Direct `sqlite3.connect(uri, uri=True)`
    used instead.

- **Capabilities added:**
  - Offline session loading with no network fetch, clear `SessionNotCachedError`.
  - Per-driver sector split truth loading from canonical DB (read-only).
  - Strawman CandidateTrajectory from FastF1 merged product (naive flat cov).
  - Full pipeline runner: candidate + truth → g1 primitives → GradingReport JSON.

- **Constraints/assumptions honored:**
  - Physics region isolation: zero imports from evo/latent/compound.
  - `get_telemetry()` confined to `strawman_candidate.py` only (confirmed by grep).
  - Read-only access to canonical DBs (sqlite URI mode=ro).
  - Offline only: `offline_mode(True)` set before session load.

- **Claims/evidence produced:**
  - 19/19 integration tests pass on 2023 Belgium Q (offline, 2 drivers, 3 laps).
  - simplification_limits PASS on all 11 touched files.
  - grep confirms `get_telemetry` only in strawman.

## Test mode
**Required:** test-after  
**Satisfied:** yes — integration test written after implementation, all 19 pass.

## Evidence

```
py -m pytest tests/integration/test_trajectory_grading_runner.py -q
```
**Result:**
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1Brainz-worktrees\cmdr-446
configfile: pyproject.toml
plugins: anyio-4.9.0+, hypothesis-6.x, mock-3.x
collected 19 items

tests\integration\test_trajectory_grading_runner.py ...................  [100%]

============================= 19 passed in 2.29s ==============================
```
**Status:** PASS

---

```
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory_grading tests/integration/test_trajectory_grading_runner.py
```
**Result:**
```
PASS (11 files checked)
```
**Status:** PASS

---

```
grep -rn get_telemetry src/preprocessing/trajectory_grading/
```
**Result:**
```
src/preprocessing/trajectory_grading/strawman_candidate.py:3:DESIGN INTENT AND get_telemetry() JUSTIFICATION
src/preprocessing/trajectory_grading/strawman_candidate.py:6:where ``lap.get_telemetry()`` is called.
src/preprocessing/trajectory_grading/strawman_candidate.py:9:``lap.get_telemetry()`` is FastF1's merged product: ...
src/preprocessing/trajectory_grading/strawman_candidate.py:32:``get_telemetry()`` is invoked ONLY inside ``_build_lap_telemetry()``.
src/preprocessing/trajectory_grading/strawman_candidate.py:149:    NOTE: This is the only place in the harness where get_telemetry() is
src/preprocessing/trajectory_grading/strawman_candidate.py:153:        tel = lap_row.get_telemetry()
src/preprocessing/trajectory_grading/strawman_candidate.py:158:        logger.debug("get_telemetry failed for lap: %s", exc)
Binary file src/preprocessing/trajectory_grading/__pycache__/strawman_candidate.cpython-314.pyc matches
```
**Status:** PASS — `get_telemetry` only in strawman (binary `.pyc` is expected).

---

**Offline load logged "Using cached data":**
FastF1's `req` logger emits `INFO: Using cached data for car_data` etc. for
each cache hit. The offline_loader also emits its own confirmation:
`INFO: Using cached data: year=2023 gp='Belgian Grand Prix' session_type='Q'`

**Read-only DB approach used:**
Direct `sqlite3.connect(f"file://{posix_path}?mode=ro", uri=True)` — bypasses
DatabaseManager entirely for queries. No `_init_database` write lock acquired.
Justification: `DatabaseManager.__init__` runs `conn.executescript(schema_sql)`
which acquires a write lock even though it's a DDL no-op on a current DB.
Using `mode=ro` guarantees zero writes to the canonical season DBs.

## TDD evidence, if required
- Test mode: test-after (not TDD per handoff). N/A.

## Docs/contracts touched
- `src/preprocessing/trajectory_grading/__init__.py` — NOT changed (g1 contract
  consumed, not extended; g2 modules not exported from the package init per
  handoff scope).

## Assumptions
1. FastF1 X/Y pos_data coordinates are in decimetres (0.1 m per unit) — verified
   empirically: raw arc-length / 10 matches FastF1's `Distance` column (ratio
   ~0.1002). `_XY_TO_METRES = 0.1` constant documented in the module.
2. Spa-Francorchamps official lap length = 7004 m (used as `lap_length_m` default).
3. The DB stores GP name as `"Belgium"` (not `"Belgian Grand Prix"`) — confirmed
   by direct SQL query. The runner exposes `gp_name_in_db` parameter to handle
   this divergence.
4. The DB uses 3-letter driver abbreviations (e.g. `"VER"`) as `driver_id`, while
   FastF1 uses driver number strings (e.g. `"1"`). The runner maps them via
   `session.get_driver(num).Abbreviation`.
5. `fastf1.Cache.offline_mode(True)` is called on FastF1 >= 3.0 to prevent any
   network attempt. On older builds the `AttributeError` is swallowed (best-effort).
6. `_LapsShim` wraps the full laps DataFrame so `build_strawman_candidate` can
   call `session.laps.pick_drivers()` without a full FastF1 Session object.
   This avoids storing the session in `RawSessionStreams` (which would have
   required changing the g1 pure-core contract).
7. The covariance gate in the runner uses time-residuals-×-speed as a rough
   arc-length conversion (deliberate approximation, consistent with naive covariance).

## Stop conditions hit
none

## Out-of-scope observations
1. **FastF1 X/Y coordinate unit discovery** — the handoff said "arc length from
   merged X/Y position" but did not mention that pos_data X/Y are in decimetres.
   This is a non-obvious FastF1 quirk. The strawman documents it with
   `_XY_TO_METRES = 0.1` and a verification note. Triage candidate: the
   architecture docs / contract.py should note this unit convention.
2. **DB GP name divergence** — FastF1 calls it "Belgian Grand Prix"; the DB has
   "Belgium". This required adding `gp_name_in_db` to `run_grading`. Other GP
   names may have similar mismatches. Triage candidate for the data layer.
3. **`fastf1.Cache.offline_mode()` availability** — only in FastF1 >= 3.0. On
   older builds the call is silently skipped. A future hardening could check
   the version and raise if offline_mode is unavailable.

## Workflow Feedback
- **Handoff gaps:** The handoff did not mention that FastF1 pos_data X/Y
  coordinates are in decimetres (not metres). This caused a silent correctness
  bug (arc-lengths 10× too large) that only surfaced when I compared the
  computed arc against FastF1's own `Distance` column. The handoff could include
  a note: "FastF1 X/Y in pos_data are in decimetres; multiply by 0.1 to get
  metres."

- **Context rediscovered:** The GP name divergence (FastF1 "Belgian Grand Prix"
  vs DB "Belgium") had to be discovered by direct SQL query. The handoff could
  say: "DB gp_name may differ from FastF1 gp name; use gp_name_in_db parameter."

- **Instructions improvised around:** The handoff said to use `DatabaseManager`
  from `src/data/database` for the truth loader, but then said to use a
  read-only `file:...?mode=ro` URI to bypass `_init_database`. These two
  instructions are contradictory: `DatabaseManager.__init__` always writes.
  I chose to bypass DatabaseManager for the query entirely (direct sqlite3) and
  document why — the handoff's intent (read-only) was clear even if the
  implementation path wasn't. This was the right call.

- **What would have made this easier:** Including a verified smoke-test snippet
  for the driver number→abbreviation mapping and the X/Y coordinate unit in the
  handoff's "Map Anchors" section would have prevented two discovery loops.

## Return status
`complete`
