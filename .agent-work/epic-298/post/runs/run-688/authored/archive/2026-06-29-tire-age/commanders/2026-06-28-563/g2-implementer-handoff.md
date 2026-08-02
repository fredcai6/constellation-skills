# Implementer Handoff

## Gate
`g2` — Race session data loader

## Task

Implement `src/physics/layer2/session_race.py`: a **pure data-loader** for race stints. No view fitting, no decay model. Produces `RaceStintData` objects (one per qualifying stint) consumed by the g3 stint estimator.

Also write `tests/unit/physics/layer2/test_session_race.py` with unit tests that mock the telemetry/DB dependencies.

## Protected Intent

The quali fitting path (`session_estimates`, `EstimateStore`, `estimate_session`, `session_fit.py`) is **completely untouched**. The race data loader is a new module with no changes to existing modules.

`track_status` from `lap_times` must **always** reach `race_mass(...)`. Never pass `track_statuses=None` silently.

## Test Mode

TDD required for new functions. Write unit tests first, then the implementation. The DB and TelemetryStore are mocked via `unittest.mock.patch` — tests must not require the real `data/f1_data_2023.db` or `data/telemetry_store.db`.

## Close Criteria

- `from src.physics.layer2.session_race import load_race_stints, RaceStintData` imports cleanly
- `load_race_stints(year, gp, driver, *, db_path)` returns a list of `RaceStintData` objects (one per qualifying stint)
- `RaceStintData.mass_kg[i]` equals `race_mass(year, gp, lap_nums[i], n_race_laps, track_statuses=all_statuses_to_lap_i)` for each lap `i`
- `RaceStintData.cumulative_track_laps` is the count of all driver-laps in `lap_times` for that session where `lap_number < stint_first_clean_lap`
- `RaceStintData.tyre_life` is the ABSOLUTE `tyre_life` value from `lap_times` (NOT normalized); documented that VER Bahrain 2023 stint 1 starts at 4 (not 0)
- `py -m pytest tests/unit/physics/layer2/test_session_race.py -v` passes

## Allowed Scope

- `src/physics/layer2/session_race.py` — NEW file
- `src/physics/layer2/__init__.py` — add `session_race` to exports if the module uses `__all__`
- `tests/unit/physics/layer2/test_session_race.py` — NEW test file

## Specific Exclusions

- `src/physics/session_fit.py` — do NOT modify
- `src/physics/layer2/estimate_store.py` — do NOT modify
- `src/physics/layer2/session_estimator.py` — do NOT modify
- `src/physics/mass_model.py` — do NOT modify (import and use as-is)
- Any existing test file — do NOT modify

## Constraints

- `constraint:physics_region_no_evo_import` — no imports from `src/evo_predictor/`, `src/latent_power/`, `src/compound_prior/`
- `constraint:data_only` — no direct FastF1 calls; all data from SQLite (`lap_times`) + TelemetryStore (Parquet via `TelemetryStore.read_session`) + `build_db_session`
- TrackStatus hard gate: `race_mass(year, gp, lap_num, n_race_laps, track_statuses=ts)` must ALWAYS receive real `track_statuses` from `lap_times.track_status`; never pass `track_statuses=None`
- `tyre_life` = ABSOLUTE value from `lap_times.tyre_life`; do NOT subtract `min(tyre_life)` or normalize; document in code that VER Bahrain 2023 stint 1 starts at 4 (installation/warm-up lap included by FastF1)
- Python invocation: `py`, not `python`; run tests as `py -m pytest`

## Map Anchors (inbound)

- **Structural:** `struct:physics.layer2 — src/physics/layer2/session_race.py (NEW file)`; `struct:data — src/data/telemetry_session.py (build_db_session) + src/data/telemetry_store.py (TelemetryStore)` — imported, not modified
- **Capability:** `TelemetryStore.read_session(year, gp_name, 'R')` returns dict with keys: `meta`, `drivers`, `laps` (lap_times DataFrame from tele_laps with `lap_start_time_s`, `lap_end_time_s`, `stint`, per driver_num), `car` (None for Parquet store — data is in Parquet), `pos` (None), `weather`; `build_db_session(payload) -> DBSession` creates FastF1-shim; `race_mass(season, circuit, lap_num, n_race_laps, *, track_statuses, team=None)` from `src/physics/mass_model.py`
- **Constraints/assumptions:** TrackStatus gate CLEARED — `lap_times.track_status` 100% populated in 2023; clean-lap filter: `valid_lap=1 AND pit_in_time IS NULL AND pit_out_time IS NULL AND track_status='1'`; stints where `n_clean_laps < 5` are included but marked `sparse=True`
- **Decision anchors:** ABSOLUTE tyre_life — do NOT normalize; tyre_life starts at 4 for VER Bahrain stint 1 — document in code but do NOT adjust
- **Evidence expectations:** `RaceStintData.mass_kg` cross-checked against `race_mass` per-lap in tests

## Required Implementations

### `RaceStintData` dataclass

```python
@dataclass(frozen=True)
class RaceStintData:
    year: int
    gp: str                     # circuit name (e.g. 'Bahrain')
    driver: str                 # driver code (e.g. 'VER')
    stint_num: int              # 1-based stint index for this driver in this race
    compound: str               # tyre compound: SOFT / MEDIUM / HARD
    lap_nums: np.ndarray        # race lap numbers, clean laps only (shape: [n_clean])
    tyre_life: np.ndarray       # ABSOLUTE tyre_life per clean lap (shape: [n_clean])
                                # WARNING: tyre_life starts at 4 for VER Bahrain 2023 R
                                # stint 1 — this is FastF1's installation-lap accounting;
                                # do NOT subtract the per-stint minimum
    processed_df: pd.DataFrame  # smoother output all clean laps concatenated;
                                # must include 'lap_number' column (int)
    mass_kg: np.ndarray         # per-lap race mass (kg), shape [n_clean]
                                # = race_mass(year, gp, lap_num, n_race_laps,
                                #             track_statuses=all_statuses_to_lap)
    cumulative_track_laps: int  # field-wide laps run on circuit BEFORE this stint's
                                # first clean lap; W3's track-evolution axis
    rho: float                  # session air density (kg/m^3)
    n_race_laps: int            # total race laps (from max(lap_number) in session)
    n_clean_laps: int           # count of clean laps in this stint
    tyre_life_start: int        # tyre_life at first clean lap
    tyre_life_end: int          # tyre_life at last clean lap
    sparse: bool = False        # True when n_clean_laps < 5
```

### `load_race_stints` function

```python
def load_race_stints(
    year: int,
    gp: str,
    driver: str,
    *,
    db_path: str,
    store_path: str | None = None,
    min_clean_laps: int = 1,
) -> list[RaceStintData]:
    """Load all qualifying stints for one driver in a race session.
    
    Loads lap-level data from SQLite, telemetry from TelemetryStore, fits each
    clean lap through the smoother chain, and computes per-lap mass with real
    track_statuses from lap_times.
    
    Parameters
    ----------
    year, gp, driver:
        Race identification.
    db_path:
        Path to the SQLite DB containing the `lap_times` and `sessions` tables.
    store_path:
        Override for TelemetryStore path (None = use DEFAULT_STORE_PATH).
    min_clean_laps:
        Stints with fewer than this many clean laps are excluded (default=1).
    """
```

### Implementation steps within `load_race_stints`

1. **Load session metadata from SQLite:**
   ```sql
   SELECT s.id, s.round_num
   FROM sessions s 
   WHERE s.year=? AND s.gp_name=? AND s.session_type='R'
   LIMIT 1
   ```
   
2. **Load ALL lap_times for this driver (all laps, clean and non-clean):**
   ```sql
   SELECT lap_number, compound, tyre_life, stint_id, track_status, valid_lap,
          pit_in_time, pit_out_time
   FROM lap_times
   WHERE session_id=? AND driver_id=?
   ORDER BY lap_number
   ```
   Keep this full set for track_statuses construction.

3. **Get n_race_laps** = `SELECT MAX(lap_number) FROM lap_times WHERE session_id=?`

4. **Identify clean laps per stint:** `valid_lap=1 AND pit_in_time IS NULL AND pit_out_time IS NULL AND track_status='1'`

5. **Compute `cumulative_track_laps` for each stint:** For stint with first clean lap at race lap `L`:
   ```sql
   SELECT COUNT(*) FROM lap_times WHERE session_id=? AND lap_number < ?
   ```
   (counts ALL driver-laps before lap L, across all drivers)

6. **Load TelemetryStore and build DBSession:**
   ```python
   from src.data.telemetry_store import TelemetryStore, DEFAULT_STORE_PATH
   from src.data.telemetry_session import build_db_session
   store = TelemetryStore(store_path or DEFAULT_STORE_PATH)
   payload = store.read_session(year, gp, 'R')
   session = build_db_session(payload)
   ```

7. **Calibrate smoother HP (once per driver-session):**
   ```python
   from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span
   from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
   from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
   
   num = driver_num(session, driver)
   pos_d, spd_d = driver_streams(session, num)
   # Use clean lap windows for HP calibration
   hp = calibrate_session_hp(
       pos_d["t"][...], pos_d["X"][...], pos_d["Y"][...],
       spd_d["t"][...], spd_d["V"][...],
       order=4, windows=clean_lap_windows
   )
   ```

8. **Fit each clean lap:**
   ```python
   for each clean lap in stint:
       t0 = lap.LapStartTime.total_seconds()
       t1 = lap.Time.total_seconds()
       s0, s1, _ = stint_span(session, driver, stint_num, pad=2.0)
       ss, info = fit_lap(pos_d, spd_d, t0, t1, hp, overhang=8.0, bounds=(s0, s1))
       dfp = smoother_to_processed_telemetry(ss, info["lap_t"], driver_id=driver,
                                             lap_number=int(lap_num))
   ```

9. **Compute per-lap mass** (MUST use real track_statuses):
   ```python
   from src.physics.mass_model import race_mass
   # Build track_statuses = [ts_lap1, ts_lap2, ..., ts_lap_num] from all_laps_df
   all_ts = all_laps_df.sort_values('lap_number')['track_status'].tolist()
   mass = race_mass(year, gp, lap_num, n_race_laps, track_statuses=all_ts)
   ```
   Note: `track_statuses[i]` is the status for lap `i+1` (0-indexed).

10. **Get rho from session weather** (if available) or fallback to 1.225.

### `compute_cumulative_track_laps` utility

```python
def compute_cumulative_track_laps(
    session_id: int,
    first_clean_lap_num: int,
    db_path: str,
) -> int:
    """Count total field laps completed before this stint's first clean lap.
    
    Returns COUNT of all (driver, lap_number) pairs in lap_times for the
    session where lap_number < first_clean_lap_num.
    """
```

## Required Evidence

- Test output: `py -m pytest tests/unit/physics/layer2/test_session_race.py -v` showing all tests pass
- The test for `mass_kg` correctness (verifies track_statuses are passed correctly)
- The test for `cumulative_track_laps` (verifies it increases for stints starting later in the race)
- Import smoke: `py -c "from src.physics.layer2.session_race import load_race_stints, RaceStintData; print('ok')"`

## Verification Commands

```bash
py -m pytest tests/unit/physics/layer2/test_session_race.py -v
py -c "from src.physics.layer2.session_race import load_race_stints, RaceStintData; print('ok')"
```

## Suggested Model Tier

`sonnet` — bounded scope, clear interfaces, pure data adapter with mocked tests

## Authority

- Interface design (`RaceStintData` fields, `load_race_stints` signature): FIXED as above; do NOT add or remove fields without floating a discovery
- Absolute tyre_life (no normalization): DECIDED by Admiral; do NOT normalize
- Minimum clean laps for sparse flag: 5 (mark `sparse=True`, still return)
- n_race_laps = max(lap_number) across all drivers: DECIDED; do NOT hardcode per-circuit values
- track_statuses MUST be real (never None): DECIDED by Admiral as TrackStatus hard gate

## Stop Conditions

Stop and return if:
- The DBSession from `build_db_session` does not expose the laps/pos/car structure expected by `driver_streams` for race sessions (surface the exact failure)
- `calibrate_session_hp` or `fit_lap` raises an unexpected exception on race-session data that can't be handled per-lap
- The `lap_times` table is missing the `stint_id`, `tyre_life`, or `track_status` columns

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
