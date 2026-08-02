# Implementer Handoff

## Gate
`g4` — Race stint store + tests + CI pyright clean

## Task

Implement `src/physics/layer2/race_stint_store.py`: SQLite-backed store for per-driver race stint estimates. Add tests:
- `tests/unit/physics/layer2/test_race_stint_store.py` — unit tests (no real DB)
- `tests/known_answer/test_ver_bahrain_stint.py` — known-answer stub (VER Bahrain 2023 R, asserts structural properties; does NOT require real DB or live fitting)

Also run `py scripts/pyright_baseline_diff.py` and FIX any new pyright errors in the new files. The CI gate requires `new=0`.

## Protected Intent

`session_estimates` table and `EstimateStore` are completely untouched. The new table is `race_stint_estimates` only. Schema is per-driver (not per-constructor like `session_estimates`). Session-agnostic: include `session_type` and `cumulative_track_laps` columns so FP/quali sessions can plug in later.

## Test Mode

TDD for store unit tests. Write unit tests first (fail), then implementation, then make pass. The known-answer test is a STUB that verifies structural properties only (no live data loading, no real fitting) — it must pass without the real `f1_data_2023.db` or `telemetry_store.db`.

## Close Criteria

- `from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord` imports cleanly
- `RaceStintStore(db_path).upsert(record)` stores a `RaceStintRecord` idempotently (INSERT OR REPLACE)
- `RaceStintStore(db_path).has(year, gp, driver, stint_num, compound)` works
- `RaceStintStore(db_path).load(year=...)` returns a DataFrame
- PK = (year, gp_name, driver, stint_num, compound) — per-driver, NOT per-constructor
- Schema includes: `session_type`, `cumulative_track_laps` columns for session-agnostic reuse
- Covariance blobs serialized as JSON (same as `EstimateStore._cov_list` pattern)
- `py -m pytest tests/unit/physics/layer2/test_race_stint_store.py -v` passes
- `py -m pytest tests/known_answer/test_ver_bahrain_stint.py -v` passes (structural stub, no real data)
- `py scripts/pyright_baseline_diff.py` shows `new=0` (check AFTER writing all new files)
- No existing file modified

## Allowed Scope

- `src/physics/layer2/race_stint_store.py` — NEW
- `tests/unit/physics/layer2/test_race_stint_store.py` — NEW
- `tests/known_answer/test_ver_bahrain_stint.py` — NEW (structural stub only)
- `src/physics/layer2/__init__.py` — only if `__all__` already exists

## Specific Exclusions

- `src/physics/layer2/estimate_store.py` — do NOT modify (use as reference pattern only)
- `session_estimates` table — do NOT modify
- Any existing source or test file — do NOT modify
- No new columns or changes to existing tables

## Constraints

- No imports from `src/evo_predictor/`, `src/latent_power/`, `src/compound_prior/`
- PK is per-driver: (year, gp_name, driver, stint_num, compound) — NOT (year, gp_name, session_type, constructor) like EstimateStore
- Reuse exactly the `_cov_list` blob encoding from EstimateStore: `np.asarray(cov, float).tolist()` → JSON string; `json.loads()` → list on read
- pyright baseline_diff must show `new=0`: run `py scripts/pyright_baseline_diff.py` BEFORE committing
- Python: `py`, not `python`; tests: `py -m pytest`

## Map Anchors

- **Structural:** `src/physics/layer2/race_stint_store.py` (NEW); `src/physics/layer2/estimate_store.py` (reference pattern, untouched)
- **Capability:** `StintEstimate` from `stint_estimator.py` is flattened into `RaceStintRecord`; `RaceStintData` provides `cumulative_track_laps`
- **Constraints:** PK per-driver; session-agnostic schema; blob encoding same as EstimateStore
- **Decision anchors:** per-driver (not per-constructor); `cumulative_track_laps` is W3's track-evolution axis — MUST be stored correctly

## Required Implementation

### `RaceStintRecord` dataclass

```python
@dataclass(frozen=True)
class RaceStintRecord:
    """One driver-stint's flattened physics estimate, ready for storage."""
    
    # Primary key fields
    year: int
    gp_name: str
    session_type: str             # 'R' for race; carried for session-agnostic reuse
    driver: str                   # driver code, e.g. 'VER'
    stint_num: int                # 1-based stint index
    compound: str                 # tyre compound
    
    # Metadata
    cumulative_track_laps: int    # W3's track-evolution axis
    tyre_life_start: int
    tyre_life_end: int
    n_clean_laps: int
    rho: Optional[float]
    
    # Fit provenance
    fit_status: str               # 'ok' | 'error'
    error: Optional[str]
    k_prior_mu: Optional[float]   # injected decay prior
    k_prior_sigma: Optional[float]
    
    # Lateral decay (PRIMARY — may be None)
    lateral_g0: Optional[float]
    lateral_g0_sigma: Optional[float]
    lateral_k: Optional[float]
    lateral_k_sigma: Optional[float]
    lateral_b_aero: Optional[float]
    lateral_b_aero_sigma: Optional[float]
    lateral_n_samples: Optional[int]
    lateral_covariance: Optional[list]    # 3x3 JSON blob, or None
    
    # Traction decay (SECONDARY — may be None)
    traction_a0: Optional[float]
    traction_a0_sigma: Optional[float]
    traction_k: Optional[float]
    traction_k_sigma: Optional[float]
    traction_b_aero: Optional[float]
    traction_b_aero_sigma: Optional[float]
    traction_n_samples: Optional[int]
    traction_covariance: Optional[list]   # 3x3 JSON blob, or None
    
    # Braking 2-param (honest-null — may be None)
    brake_decel_ms2: Optional[float]
    brake_decel_ms2_sigma: Optional[float]
    brake_aero_decel_per_m: Optional[float]
    brake_aero_decel_per_m_sigma: Optional[float]
    braking_covariance: Optional[list]    # 2x2 JSON blob
    
    # PowerDrag (honest-null — may be None)
    max_power_w: Optional[float]
    max_power_w_sigma: Optional[float]
    drag_area_m2: Optional[float]
    drag_area_m2_sigma: Optional[float]
    power_drag_covariance: Optional[list]  # 2x2 JSON blob
    
    # Coast (diagnostic — may be None)
    coast_rolling_decel_ms2: Optional[float]
    coast_rolling_decel_ms2_sigma: Optional[float]
    coast_drag_area_m2: Optional[float]
    coast_drag_area_m2_sigma: Optional[float]
    coast_covariance: Optional[list]       # 2x2 JSON blob
    
    # Bookkeeping
    fitted_at: Optional[str]
```

### `_PK` and `_JSON_COLUMNS`

```python
_PK = ("year", "gp_name", "session_type", "driver", "stint_num", "compound")
_JSON_COLUMNS = (
    "lateral_covariance", "traction_covariance",
    "braking_covariance", "power_drag_covariance", "coast_covariance",
)
```

### `_cov_list` helper (copy from estimate_store pattern)

```python
def _cov_list(cov):
    """2xN covariance → nested python list for JSON, or None."""
    if cov is None:
        return None
    return np.asarray(cov, dtype=float).tolist()

def _sigma(cov, i: int) -> Optional[float]:
    if cov is None:
        return None
    a = np.asarray(cov, dtype=float)
    if a.ndim != 2 or i >= a.shape[0]:
        return None
    return float(np.sqrt(max(a[i, i], 0.0)))
```

### `record_from_stint_estimate` function

```python
def record_from_stint_estimate(
    est: "StintEstimate",
    *,
    session_type: str = "R",
    fitted_at: Optional[str] = None,
) -> RaceStintRecord:
    """Flatten a StintEstimate into a RaceStintRecord for storage."""
    lat = est.lateral_decay
    trac = est.traction_decay
    brk = est.braking
    pd_ = est.power_drag
    co = est.coast
    return RaceStintRecord(
        year=est.year, gp_name=est.gp, session_type=session_type,
        driver=est.driver, stint_num=est.stint_num, compound=est.compound,
        cumulative_track_laps=est.cumulative_track_laps,
        tyre_life_start=est.tyre_life_start, tyre_life_end=est.tyre_life_end,
        n_clean_laps=est.n_clean_laps, rho=est.rho,
        fit_status="ok", error=None,
        k_prior_mu=est.k_prior_mu, k_prior_sigma=est.k_prior_sigma,
        # Lateral
        lateral_g0=(float(lat.g0) if lat else None),
        lateral_g0_sigma=(_sigma(lat.covariance, 0) if lat else None),
        lateral_k=(float(lat.k) if lat else None),
        lateral_k_sigma=(_sigma(lat.covariance, 1) if lat else None),
        lateral_b_aero=(float(lat.b_aero) if lat else None),
        lateral_b_aero_sigma=(_sigma(lat.covariance, 2) if lat else None),
        lateral_n_samples=(lat.n_samples if lat else None),
        lateral_covariance=(_cov_list(lat.covariance) if lat else None),
        # Traction
        traction_a0=(float(trac.a0) if trac else None),
        traction_a0_sigma=(_sigma(trac.covariance, 0) if trac else None),
        traction_k=(float(trac.k) if trac else None),
        traction_k_sigma=(_sigma(trac.covariance, 1) if trac else None),
        traction_b_aero=(float(trac.b_aero) if trac else None),
        traction_b_aero_sigma=(_sigma(trac.covariance, 2) if trac else None),
        traction_n_samples=(trac.n_samples if trac else None),
        traction_covariance=(_cov_list(trac.covariance) if trac else None),
        # Braking
        brake_decel_ms2=(float(brk.brake_decel_ms2) if brk else None),
        brake_decel_ms2_sigma=(_sigma(getattr(brk, 'covariance', None), 0) if brk else None),
        brake_aero_decel_per_m=(float(brk.brake_aero_decel_per_m) if brk else None),
        brake_aero_decel_per_m_sigma=(_sigma(getattr(brk, 'covariance', None), 1) if brk else None),
        braking_covariance=(_cov_list(getattr(brk, 'covariance', None)) if brk else None),
        # PowerDrag
        max_power_w=(float(pd_.max_power_w) if pd_ else None),
        max_power_w_sigma=(_sigma(getattr(pd_, 'covariance', None), 0) if pd_ else None),
        drag_area_m2=(float(pd_.drag_area_closed_m2) if pd_ else None),
        drag_area_m2_sigma=(_sigma(getattr(pd_, 'covariance', None), 1) if pd_ else None),
        power_drag_covariance=(_cov_list(getattr(pd_, 'covariance', None)) if pd_ else None),
        # Coast
        coast_rolling_decel_ms2=(float(co.coast_rolling_decel_ms2) if co else None),
        coast_rolling_decel_ms2_sigma=(_sigma(getattr(co, 'covariance', None), 0) if co else None),
        coast_drag_area_m2=(float(co.coast_drag_area_m2) if co else None),
        coast_drag_area_m2_sigma=(_sigma(getattr(co, 'covariance', None), 1) if co else None),
        coast_covariance=(_cov_list(getattr(co, 'covariance', None)) if co else None),
        fitted_at=fitted_at,
    )
```

### `error_record` function

```python
def error_record(
    year: int, gp_name: str, driver: str, stint_num: int, compound: str, *,
    error: str, session_type: str = "R", fitted_at: Optional[str] = None,
) -> RaceStintRecord:
    """A fit_status='error' row so a failing stint is recorded, never lost."""
```
Return a RaceStintRecord with all numeric fields = None, fit_status='error', error=str(error)[:500].

### `RaceStintStore` class

```python
class RaceStintStore:
    """SQLite-backed store of RaceStintRecords (idempotent on PK)."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cols = [f.name for f in RaceStintRecord.__dataclass_fields__.values()]
        self._init_schema()
    
    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con
    
    def _init_schema(self) -> None:
        # CREATE TABLE IF NOT EXISTS race_stint_estimates (all columns, PRIMARY KEY (_PK))
        ...
    
    def upsert(self, record: RaceStintRecord) -> None:
        # Serialize JSON columns, INSERT OR REPLACE INTO race_stint_estimates
        ...
    
    def has(self, year: int, gp_name: str, driver: str, stint_num: int,
            compound: str, session_type: str = "R") -> bool:
        ...
    
    def load(
        self,
        year: Optional[int] = None,
        session_type: Optional[str] = "R",
        status: Optional[str] = "ok",
    ) -> pd.DataFrame:
        # SELECT with optional filters; deserialize JSON columns on read
        ...
```

## Known-Answer Test Structure

The known-answer test `tests/known_answer/test_ver_bahrain_stint.py` must be a STRUCTURAL STUB only — no real data required. Example:

```python
"""Known-answer structural contract for VER Bahrain 2023 R stint 1.

This test verifies the STRUCTURE of RaceStintRecord (not the values — actual
fitting requires the real DB and telemetry store). Run integration tests for
value verification.
"""
import pytest
from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord, error_record

def test_race_stint_record_importable():
    assert RaceStintRecord is not None

def test_pk_fields():
    """PK is per-driver, not per-constructor."""
    fields = set(RaceStintRecord.__dataclass_fields__)
    assert 'driver' in fields
    assert 'stint_num' in fields
    assert 'compound' in fields
    assert 'constructor' not in fields   # should NOT have constructor

def test_session_type_field():
    """session_type column enables session-agnostic reuse."""
    fields = set(RaceStintRecord.__dataclass_fields__)
    assert 'session_type' in fields

def test_cumulative_track_laps_field():
    """cumulative_track_laps is W3's track-evolution axis."""
    fields = set(RaceStintRecord.__dataclass_fields__)
    assert 'cumulative_track_laps' in fields

def test_all_five_views_present():
    """All five views have at least one field in the record."""
    fields = set(RaceStintRecord.__dataclass_fields__)
    assert any('lateral' in f for f in fields)
    assert any('traction' in f for f in fields)
    assert any('brake' in f for f in fields)
    assert any('power_drag' in f or 'max_power' in f for f in fields)
    assert any('coast' in f for f in fields)

def test_error_record_construction():
    """error_record produces a valid RaceStintRecord with fit_status='error'."""
    r = error_record(2023, 'Bahrain', 'VER', 1, 'SOFT', error='test error')
    assert r.fit_status == 'error'
    assert r.lateral_g0 is None
    assert r.lateral_k is None

def test_store_round_trip(tmp_path):
    """RaceStintStore round-trips a record idempotently."""
    db = str(tmp_path / 'test.db')
    store = RaceStintStore(db)
    r = error_record(2023, 'Bahrain', 'VER', 1, 'SOFT', error='test')
    store.upsert(r)
    store.upsert(r)   # idempotent
    assert store.has(2023, 'Bahrain', 'VER', 1, 'SOFT')
    df = store.load(year=2023)
    assert len(df) == 1
```

## Pyright Requirement

After writing all files, run:
```bash
py scripts/pyright_baseline_diff.py
```

If output shows `new > 0`, FIX the type errors in the new files BEFORE committing. Common issues:
- Missing `Optional` wrapper on nullable fields
- `None` vs `Optional[float]` mismatches  
- Missing return type annotations on class methods
- `sqlite3.Connection` type annotation

The CI gate requires `new=0`. Do not commit until pyright is clean.

## Required Evidence

- `py -m pytest tests/unit/physics/layer2/test_race_stint_store.py -v` → all pass
- `py -m pytest tests/known_answer/test_ver_bahrain_stint.py -v` → all pass
- `py scripts/pyright_baseline_diff.py` output showing `new=0`
- Import smoke: `py -c "from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord; print('ok')"`

## Verification Commands

```bash
py -m pytest tests/unit/physics/layer2/test_race_stint_store.py -v
py -m pytest tests/known_answer/test_ver_bahrain_stint.py -v
py scripts/pyright_baseline_diff.py
py -c "from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord; print('ok')"
```

## Suggested Model Tier

`sonnet` — well-specified store pattern (reuses EstimateStore), pyright clean is the main risk

## Authority

- PK = per-driver: DECIDED
- session_type column: DECIDED
- cumulative_track_laps: DECIDED (W3 axis)
- Blob encoding (same as EstimateStore._cov_list): DECIDED
- known-answer test is structural only (no live data): DECIDED
- pyright new=0: HARD GATE

## Stop Conditions

Stop and return if:
- `py scripts/pyright_baseline_diff.py` produces `new > 0` that cannot be fixed in new files (i.e. requires modifying an existing file's type annotations)
- The `StintEstimate` dataclass fields from `stint_estimator.py` don't match what this flattener expects

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (including pyright output), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
