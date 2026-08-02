# P0 — Per-Session Physics Fit Store + Batch Runner — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist every single-quali-session physics fit (per-axis posteriors + covariances + identifiability flags + metadata) across the 2018–2025 seasons into a queryable store, and emit a first evidence report on which axes are single-session-identifiable — the substrate Epic 2 pooling reads.

**Architecture:** Four importable units. `fit_store.py` owns the on-disk schema (SQLite `data/physics_fits.db`, one row per year×gp×session×driver) and a `FitRecord` dataclass. `session_fit.py` lifts the validated smoother→adapter→estimator chain from `scripts/plot_capability_diagnostics.py::fit_session` into a reusable offline fit that returns a `FitRecord`. `fit_batch.py` orchestrates enumeration (calendar × seasons × sessions × drivers), resumable skip-existing, and per-session/per-driver error capture. `fit_evidence.py` aggregates the store into coverage/identifiability tables. Two thin `scripts/` CLIs wrap the batch and evidence modules.

**Tech Stack:** Python 3.14 (`py` launcher), FastF1 (offline cache only), SQLite (stdlib `sqlite3`), pandas, numpy, pytest.

## Global Constraints

- Python is invoked as `py`, never `python`. Tests run via `py -m pytest tests/...`.
- The batch reads telemetry from the **offline** FastF1 cache only (`outputs/cache`, 36 GB, 2015–2024+). Never fetch from network: enable `fastf1.Cache.offline_mode(True)`. A session missing from cache is a recorded skip, not a crash.
- The fit chain is **lifted verbatim** from the validated `scripts/plot_capability_diagnostics.py::fit_session` (the #488 production path), with two deltas: it operates on a **preloaded** session (load once, loop drivers) and loads `weather=True` so density is the real measured value (memory: use real per-session density, not fixed RHO=1.2).
- The store is **idempotent and resumable**: re-running skips rows already present unless `--force`. Primary key = `(year, gp_name, session_type, driver)`.
- Covariance matrices and apex observations are stored as **JSON text columns** (numpy arrays → nested lists). Every numeric column is nullable (a fit can fail or fall back on any axis).
- `MASS_KG = 808.0` is the documented drag mass (`CdA = 2 · MASS_KG · theta_D`); define it once where CdA is derived.
- Constructor key = the raw FastF1 `TeamName` (stable within a season; cross-season canonicalisation is P2's concern, not P0's).
- TDD: write the failing test first for every pure function; commit after each green task. Follow existing `src/physics` patterns (frozen dataclasses, typed signatures, module docstrings).

## File Structure

- `src/physics/fit_store.py` — `FitRecord` dataclass + `FitStore` (schema, `upsert`, `has_fit`, `load_fits`, `load_apex_weekend`). Pure; depends only on stdlib + numpy + pandas.
- `src/physics/session_fit.py` — `load_quali_session`, `fit_driver`, and the pure `record_from_params`. Lifts the diagnostics fit chain.
- `src/physics/fit_batch.py` — `run_batch` orchestration (enumeration, skip-existing, error capture, logging).
- `src/physics/fit_evidence.py` — `summarize_store`, `coverage_table`, `pooling_feasibility` aggregations.
- `scripts/build_physics_fit_store.py` — thin CLI over `run_batch`.
- `scripts/physics_fit_evidence.py` — thin CLI over the evidence aggregations (writes markdown).
- Tests: `tests/unit/physics/test_fit_store.py`, `test_session_fit.py`, `test_fit_batch.py`, `test_fit_evidence.py`.

---

### Task 1: Fit store (schema + FitRecord + read/write API)

**Files:**
- Create: `src/physics/fit_store.py`
- Test: `tests/unit/physics/test_fit_store.py`

**Interfaces:**
- Consumes: nothing from other tasks (stdlib `sqlite3`, `json`, `dataclasses`; `numpy`, `pandas`).
- Produces:
  - `FitRecord` — frozen dataclass with every persisted field (used by Tasks 2–4).
  - `FitStore(db_path: str)` with: `upsert(record: FitRecord) -> None`; `has_fit(year:int, gp_name:str, session_type:str, driver:str) -> bool`; `load_fits(year:int|None=None, session_type:str|None=None, status:str|None="ok") -> pandas.DataFrame`; `load_apex_weekend(year:int, gp_name:str, session_type:str) -> dict[str, list[dict]]` (constructor → concatenated apex-obs dicts, ok rows only).

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/test_fit_store.py
import numpy as np
import pytest

from src.physics.fit_store import FitRecord, FitStore


def _record(**over):
    base = dict(
        year=2023, gp_name="Great Britain", round_idx=10, session_type="Q",
        driver="VER", constructor="Red Bull Racing", fit_status="ok", error=None,
        best_lap_s=85.3, fit_air_density=1.18, n_flying_laps=4, n_samples_used=2200,
        theta_D=7.8e-4, theta_R=0.02, theta_D_open=6.7e-4, theta_D_source="throttle_joint_drs",
        fallback_longitudinal=False, fallback_reason_long=None, cda=1.26,
        A0=18.1, A2=5.5e-3, k_tire=0.0, g_track=1.0, ceiling=None, aero_identifiable=True,
        fallback_lateral=False, a_b=-45.0, b_b=-2e-3, a_t=12.0, b_t=4e-3,
        traction_source="measured", braking_source="measured", ceiling_trustworthy=False,
        n_apex=14, n_on_limit=12, p99_speed=92.0, speed_inflation=False, chi2=1.1, ell_used=3.2,
        lateral_covariance=[[1e-2, 0.0], [0.0, 1e-6]], braking_covariance=[[2.0, 0.0], [0.0, 1e-7]],
        traction_covariance=[[1.0, 0.0], [0.0, 1e-7]], fit_quality_metrics={"theta_D_source": "throttle_joint_drs"},
        apex_obs=[{"v_apex": 70.0, "radius_m": 120.0, "a_lat": 30.0, "on_limit": True}],
        engine_sha="abc1234", fitted_at="2026-06-17T00:00:00Z",
    )
    base.update(over)
    return FitRecord(**base)


def test_upsert_then_load_roundtrips_record(tmp_path):
    store = FitStore(str(tmp_path / "fits.db"))
    store.upsert(_record())
    df = store.load_fits(year=2023)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["driver"] == "VER"
    assert row["constructor"] == "Red Bull Racing"
    assert row["theta_D"] == pytest.approx(7.8e-4)
    assert row["fallback_lateral"] == False  # noqa: E712


def test_has_fit_and_idempotent_upsert(tmp_path):
    store = FitStore(str(tmp_path / "fits.db"))
    assert not store.has_fit(2023, "Great Britain", "Q", "VER")
    store.upsert(_record())
    assert store.has_fit(2023, "Great Britain", "Q", "VER")
    store.upsert(_record(best_lap_s=85.1))  # same PK -> replace, not duplicate
    df = store.load_fits(year=2023)
    assert len(df) == 1
    assert df.iloc[0]["best_lap_s"] == pytest.approx(85.1)


def test_covariance_json_roundtrips_to_nested_list(tmp_path):
    store = FitStore(str(tmp_path / "fits.db"))
    store.upsert(_record())
    df = store.load_fits(year=2023)
    cov = df.iloc[0]["braking_covariance"]
    assert np.array(cov).shape == (2, 2)


def test_load_fits_status_filter_excludes_errors(tmp_path):
    store = FitStore(str(tmp_path / "fits.db"))
    store.upsert(_record())
    store.upsert(_record(driver="PER", fit_status="error", error="boom", theta_D=None))
    assert len(store.load_fits(year=2023, status="ok")) == 1
    assert len(store.load_fits(year=2023, status=None)) == 2


def test_load_apex_weekend_groups_by_constructor(tmp_path):
    store = FitStore(str(tmp_path / "fits.db"))
    store.upsert(_record(driver="VER"))
    store.upsert(_record(driver="PER", apex_obs=[{"v_apex": 69.0, "radius_m": 121.0, "a_lat": 29.0, "on_limit": True}]))
    weekend = store.load_apex_weekend(2023, "Great Britain", "Q")
    assert set(weekend) == {"Red Bull Racing"}
    assert len(weekend["Red Bull Racing"]) == 2  # both drivers' apexes pooled
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_fit_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.fit_store'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/physics/fit_store.py
"""Per-session physics fit store (Epic 2 P0, #492).

One row per (year, gp_name, session_type, driver): the single-session
PhysicsParameterSet flattened to scalars + JSON covariances + identifiability
flags + weekend metadata. The substrate cross-session pooling reads.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import pandas as pd

# Columns serialized as JSON text (numpy arrays / dicts / lists).
_JSON_COLUMNS = (
    "lateral_covariance", "braking_covariance", "traction_covariance",
    "fit_quality_metrics", "apex_obs",
)


@dataclass(frozen=True)
class FitRecord:
    """One driver's single-session fit, flattened for storage."""

    year: int
    gp_name: str
    round_idx: Optional[int]
    session_type: str
    driver: str
    constructor: str
    fit_status: str            # "ok" | "error" | "no_laps"
    error: Optional[str]
    best_lap_s: Optional[float]
    fit_air_density: Optional[float]
    n_flying_laps: int
    n_samples_used: int
    # longitudinal
    theta_D: Optional[float]
    theta_R: Optional[float]
    theta_D_open: Optional[float]
    theta_D_source: Optional[str]
    fallback_longitudinal: bool
    fallback_reason_long: Optional[str]
    cda: Optional[float]
    # lateral
    A0: Optional[float]
    A2: Optional[float]
    k_tire: Optional[float]
    g_track: Optional[float]
    ceiling: Optional[float]
    aero_identifiable: Optional[bool]
    fallback_lateral: bool
    # braking / traction
    a_b: Optional[float]
    b_b: Optional[float]
    a_t: Optional[float]
    b_t: Optional[float]
    # envelope flags
    traction_source: Optional[str]
    braking_source: Optional[str]
    ceiling_trustworthy: Optional[bool]
    # apex
    n_apex: int
    n_on_limit: int
    # diagnostics
    p99_speed: Optional[float]
    speed_inflation: bool
    chi2: Optional[float]
    ell_used: Optional[float]
    # JSON blobs
    lateral_covariance: Optional[list]
    braking_covariance: Optional[list]
    traction_covariance: Optional[list]
    fit_quality_metrics: dict = field(default_factory=dict)
    apex_obs: list = field(default_factory=list)
    # bookkeeping
    engine_sha: Optional[str] = None
    fitted_at: Optional[str] = None


_PK = ("year", "gp_name", "session_type", "driver")


class FitStore:
    """SQLite-backed store of FitRecords (idempotent on the natural key)."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cols = [f.name for f in FitRecord.__dataclass_fields__.values()]
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_schema(self) -> None:
        cols_sql = ", ".join(f'"{c}"' for c in self._cols)
        with self._connect() as con:
            con.execute(
                f"CREATE TABLE IF NOT EXISTS session_fits ({cols_sql}, "
                f"PRIMARY KEY ({', '.join(_PK)}))"
            )

    def upsert(self, record: FitRecord) -> None:
        d = asdict(record)
        for c in _JSON_COLUMNS:
            d[c] = json.dumps(d[c]) if d[c] is not None else None
        placeholders = ", ".join("?" for _ in self._cols)
        cols_sql = ", ".join(f'"{c}"' for c in self._cols)
        with self._connect() as con:
            con.execute(
                f"INSERT OR REPLACE INTO session_fits ({cols_sql}) VALUES ({placeholders})",
                [d[c] for c in self._cols],
            )

    def has_fit(self, year: int, gp_name: str, session_type: str, driver: str) -> bool:
        with self._connect() as con:
            cur = con.execute(
                "SELECT 1 FROM session_fits WHERE year=? AND gp_name=? "
                "AND session_type=? AND driver=? LIMIT 1",
                (year, gp_name, session_type, driver),
            )
            return cur.fetchone() is not None

    def load_fits(
        self,
        year: Optional[int] = None,
        session_type: Optional[str] = None,
        status: Optional[str] = "ok",
    ) -> pd.DataFrame:
        clauses, params = [], []
        if year is not None:
            clauses.append("year=?"); params.append(year)
        if session_type is not None:
            clauses.append("session_type=?"); params.append(session_type)
        if status is not None:
            clauses.append("fit_status=?"); params.append(status)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._connect() as con:
            df = pd.read_sql_query(f"SELECT * FROM session_fits{where}", con, params=params)
        for c in _JSON_COLUMNS:
            if c in df.columns:
                df[c] = df[c].apply(lambda v: json.loads(v) if isinstance(v, str) else v)
        return df

    def load_apex_weekend(
        self, year: int, gp_name: str, session_type: str
    ) -> dict[str, list[dict]]:
        df = self.load_fits(year=year, session_type=session_type, status="ok")
        df = df[df["gp_name"] == gp_name]
        out: dict[str, list[dict]] = {}
        for _, row in df.iterrows():
            obs = row["apex_obs"] or []
            out.setdefault(row["constructor"], []).extend(obs)
        return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/unit/physics/test_fit_store.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/physics/fit_store.py tests/unit/physics/test_fit_store.py
git commit -m "feat(physics): per-session fit store schema + FitRecord (#492 P0)"
```

---

### Task 2: Session fit (offline chain → FitRecord)

**Files:**
- Create: `src/physics/session_fit.py`
- Test: `tests/unit/physics/test_session_fit.py`
- Reference (copy the chain from): `scripts/plot_capability_diagnostics.py:55-165`

**Interfaces:**
- Consumes: `FitRecord` from Task 1; the production engine (`ParameterEstimator`, `CapabilityEnvelope`, `extract_apex_observations`, the trajectory loaders/calibration/adapter).
- Produces:
  - `record_from_params(params, *, year, gp_name, round_idx, session_type, driver, constructor, rho, best_lap_s, n_flying_laps, apex_obs, env, diag) -> FitRecord` — **pure**, flattens a `PhysicsParameterSet` (+ envelope flags + apex obs + diagnostics) to a `FitRecord`. `env` is the `CapabilityEnvelope`; `diag` is a dict with `p99_speed`, `speed_inflation`, `chi2`, `ell_used`.
  - `load_quali_session(year:int, gp:str, session_type:str, cache:str, offline:bool=True) -> tuple[Any, float]` — returns `(fastf1_session, rho)` with `weather=True` and offline mode set; `rho` from measured pressure/temp/humidity, else `DEFAULT_RHO`.
  - `fit_driver(session, driver:str, *, year:int, gp_name:str, round_idx:int|None, session_type:str, constructor:str, rho:float, cfg=None) -> FitRecord` — runs the lifted chain for one driver on a preloaded session; returns `fit_status="no_laps"` when the driver has no valid flying lap, `"error"` on any exception (message captured), `"ok"` otherwise.

- [ ] **Step 1: Write the failing test (pure record conversion — no cache needed)**

```python
# tests/unit/physics/test_session_fit.py
import numpy as np
import pytest

from src.physics.physics_data_models import (
    PhysicsParameterSet, LongitudinalParameters, LateralParameters,
    BrakingParameters, TractionParameters,
)
from src.physics.session_fit import record_from_params


class _Env:  # stand-in for CapabilityEnvelope flags
    traction_source = "measured"
    braking_source = "population_ratio"
    ceiling_trustworthy = False


def _params():
    lon = LongitudinalParameters(
        theta_D=7.8e-4, theta_R=0.02, theta_D_std=1e-5, theta_R_std=1e-4,
        theta_P_times=np.array([0.0, 1.0]), theta_P_values=np.array([1.0, 1.0]),
        theta_D_open=6.7e-4,
    )
    lat = LateralParameters(A0=18.1, A2=5.5e-3, k_tire=0.0, g_track=1.0,
                            covariance=np.array([[1e-2, 0.0], [0.0, 1e-6]]),
                            ceiling=None, aero_identifiable=True)
    brk = BrakingParameters(a_b=-45.0, b_b=-2e-3, covariance=np.array([[2.0, 0.0], [0.0, 1e-7]]))
    trc = TractionParameters(a_t=12.0, b_t=4e-3, covariance=np.array([[1.0, 0.0], [0.0, 1e-7]]))
    return PhysicsParameterSet(
        driver_id="VER", session_id=0, longitudinal=lon, lateral=lat,
        n_samples_used=2200, fit_air_density=1.18,
        fit_quality_metrics={"fallback_longitudinal": False, "fallback_lateral": False,
                             "theta_D_source": "throttle_joint_drs"},
        braking=brk, traction=trc,
    )


def test_record_from_params_flattens_axes_and_covariances():
    apex = [{"v_apex": 70.0, "radius_m": 120.0, "a_lat": 30.0, "on_limit": True}]
    rec = record_from_params(
        _params(), year=2023, gp_name="Great Britain", round_idx=10, session_type="Q",
        driver="VER", constructor="Red Bull Racing", rho=1.18, best_lap_s=85.3,
        n_flying_laps=4, apex_obs=apex, env=_Env(),
        diag={"p99_speed": 92.0, "speed_inflation": False, "chi2": 1.1, "ell_used": 3.2},
    )
    assert rec.fit_status == "ok"
    assert rec.theta_D == pytest.approx(7.8e-4)
    assert rec.cda == pytest.approx(2.0 * 808.0 * 7.8e-4)
    assert rec.a_b == pytest.approx(-45.0)
    assert rec.a_t == pytest.approx(12.0)
    assert rec.braking_covariance == [[2.0, 0.0], [0.0, 1e-7]]
    assert rec.braking_source == "population_ratio"
    assert rec.fallback_lateral is False
    assert rec.n_on_limit == 1


def test_record_from_params_handles_missing_braking_and_traction():
    p = _params()
    p.braking = None
    p.traction = None
    rec = record_from_params(
        p, year=2023, gp_name="Spain", round_idx=8, session_type="Q",
        driver="VER", constructor="Red Bull Racing", rho=1.2, best_lap_s=78.0,
        n_flying_laps=3, apex_obs=[], env=_Env(),
        diag={"p99_speed": 90.0, "speed_inflation": False, "chi2": 1.0, "ell_used": 3.0},
    )
    assert rec.a_b is None and rec.b_b is None
    assert rec.a_t is None and rec.b_t is None
    assert rec.braking_covariance is None and rec.traction_covariance is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_session_fit.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.session_fit'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/physics/session_fit.py
"""Offline single-quali-session fit → FitRecord (Epic 2 P0, #492).

Lifts the validated smoother→adapter→estimator chain from
``scripts/plot_capability_diagnostics.py::fit_session`` (the #488 production
path) with two deltas: it operates on a PRELOADED session (load once, loop
drivers) and loads ``weather=True`` so air density is the real measured value.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

from src.physics.fit_store import FitRecord

logger = logging.getLogger(__name__)

MASS_KG = 808.0           # CdA = 2 * MASS_KG * theta_D
DEFAULT_RHO = 1.20        # fallback when session weather is unavailable
DEFAULT_CACHE = "outputs/cache"
_P99_SPEED_LIMIT = 110.0  # m/s; above this the smoothed speed channel is inflated
_FLY_FRACTION = 1.08      # pool laps within 8% of the driver's best


def _as_list(cov) -> Optional[list]:
    return None if cov is None else np.asarray(cov, dtype=float).tolist()


def record_from_params(
    params, *, year, gp_name, round_idx, session_type, driver, constructor,
    rho, best_lap_s, n_flying_laps, apex_obs, env, diag,
) -> FitRecord:
    """Flatten a PhysicsParameterSet (+ envelope flags + apex obs) to a FitRecord."""
    m = params.fit_quality_metrics
    lon, lat = params.longitudinal, params.lateral
    brk, trc = params.braking, params.traction
    theta_D = float(lon.theta_D)
    return FitRecord(
        year=year, gp_name=gp_name, round_idx=round_idx, session_type=session_type,
        driver=driver, constructor=constructor, fit_status="ok", error=None,
        best_lap_s=best_lap_s, fit_air_density=rho,
        n_flying_laps=n_flying_laps, n_samples_used=int(params.n_samples_used),
        theta_D=theta_D, theta_R=float(lon.theta_R),
        theta_D_open=(None if lon.theta_D_open is None else float(lon.theta_D_open)),
        theta_D_source=str(m.get("theta_D_source", "unknown")),
        fallback_longitudinal=bool(m.get("fallback_longitudinal", True)),
        fallback_reason_long=(None if m.get("fallback_reason_longitudinal") is None
                              else str(m.get("fallback_reason_longitudinal"))),
        cda=2.0 * MASS_KG * theta_D,
        A0=float(lat.A0), A2=float(lat.A2), k_tire=float(lat.k_tire), g_track=float(lat.g_track),
        ceiling=(None if lat.ceiling is None else float(lat.ceiling)),
        aero_identifiable=bool(lat.aero_identifiable),
        fallback_lateral=bool(m.get("fallback_lateral", True)),
        a_b=(None if brk is None else float(brk.a_b)),
        b_b=(None if brk is None else float(brk.b_b)),
        a_t=(None if trc is None else float(trc.a_t)),
        b_t=(None if trc is None else float(trc.b_t)),
        traction_source=getattr(env, "traction_source", None),
        braking_source=getattr(env, "braking_source", None),
        ceiling_trustworthy=getattr(env, "ceiling_trustworthy", None),
        n_apex=len(apex_obs), n_on_limit=sum(1 for o in apex_obs if o.get("on_limit")),
        p99_speed=diag.get("p99_speed"), speed_inflation=bool(diag.get("speed_inflation", False)),
        chi2=diag.get("chi2"), ell_used=diag.get("ell_used"),
        lateral_covariance=_as_list(lat.covariance),
        braking_covariance=(None if brk is None else _as_list(brk.covariance)),
        traction_covariance=(None if trc is None else _as_list(trc.covariance)),
        fit_quality_metrics={k: (str(v) if isinstance(v, str) else v) for k, v in m.items()},
        apex_obs=apex_obs,
    )


def load_quali_session(year, gp, session_type, cache=DEFAULT_CACHE, offline=True):
    """Load a FastF1 session from cache (offline) with weather; return (session, rho)."""
    import fastf1  # type: ignore[import-untyped]
    fastf1.Cache.enable_cache(cache)
    if offline:
        try:
            fastf1.Cache.offline_mode(True)  # type: ignore[attr-defined]
        except AttributeError:
            pass
    s = fastf1.get_session(year, gp, session_type)
    s.load(telemetry=True, laps=True, weather=True)
    rho = DEFAULT_RHO
    try:
        from src.utils.environment import moist_air_density_from_pressure
        wd = s.weather_data
        rho = moist_air_density_from_pressure(
            float(wd["Pressure"].median()) * 100.0,
            float(wd["AirTemp"].median()),
            float(wd["Humidity"].median()),
        )
    except Exception:
        logger.warning("weather density unavailable for %s %s %s; using DEFAULT_RHO",
                       year, gp, session_type)
    return s, float(rho)


def _build_control_df(session, drv_num, t0, t1, pad=2.0) -> pd.DataFrame:
    """control_df (throttle/brake/gear/drs) for one lap window. Lifted from diagnostics."""
    cd = pd.DataFrame(session.car_data[drv_num])
    t = cd["SessionTime"].dt.total_seconds().to_numpy()
    msk = (t >= t0 - pad) & (t <= t1 + pad)
    cd = cd[msk]
    if cd.empty:
        return pd.DataFrame()
    brake = cd["Brake"].astype(float).to_numpy()
    return pd.DataFrame({
        "session_time_ms": (t[msk] * 1000.0).astype(int),
        "throttle": cd["Throttle"].astype(float).to_numpy(),
        "brake": brake * 100.0 if brake.max() <= 1.0 else brake,
        "gear": cd["nGear"].astype(float).to_numpy() if "nGear" in cd.columns else 0.0,
        "drs": cd["DRS"].astype(float).to_numpy() if "DRS" in cd.columns else 0.0,
    })


def fit_driver(session, driver, *, year, gp_name, round_idx, session_type,
               constructor, rho, cfg=None) -> FitRecord:
    """Run the lifted production chain for one driver on a preloaded session."""
    from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span
    from src.preprocessing.trajectory.calibration import calibrate_session_hp, fit_lap
    from src.preprocessing.trajectory.physics_adapter import smoother_to_processed_telemetry
    from src.physics.parameter_estimator import ParameterEstimator
    from src.physics.physics_config import PhysicsEstimatorConfig
    from src.physics.regulation_era import RegulationEra
    from src.physics.capability_envelope import CapabilityEnvelope
    from src.physics.apex_extract import extract_apex_observations

    def _err(status, msg=None):
        return FitRecord(
            year=year, gp_name=gp_name, round_idx=round_idx, session_type=session_type,
            driver=driver, constructor=constructor, fit_status=status, error=msg,
            best_lap_s=None, fit_air_density=rho, n_flying_laps=0, n_samples_used=0,
            theta_D=None, theta_R=None, theta_D_open=None, theta_D_source=None,
            fallback_longitudinal=True, fallback_reason_long=None, cda=None,
            A0=None, A2=None, k_tire=None, g_track=None, ceiling=None,
            aero_identifiable=None, fallback_lateral=True,
            a_b=None, b_b=None, a_t=None, b_t=None,
            traction_source=None, braking_source=None, ceiling_trustworthy=None,
            n_apex=0, n_on_limit=0, p99_speed=None, speed_inflation=False,
            chi2=None, ell_used=None, lateral_covariance=None, braking_covariance=None,
            traction_covariance=None, fit_quality_metrics={}, apex_obs=[],
        )

    try:
        cfg = cfg or PhysicsEstimatorConfig.from_config()
        era = RegulationEra.for_season(year)
        num = driver_num(session, driver)
        pos_d, spd_d = driver_streams(session, num)
        valid = session.laps.pick_drivers(driver)
        valid = valid[valid["LapTime"].notna()]
        valid = valid[valid["LapTime"].dt.total_seconds() > 50]
        if valid.empty:
            return _err("no_laps")
        best_s = float(valid["LapTime"].dt.total_seconds().min())
        fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
        flying = valid[valid["LapTime"].dt.total_seconds() <= _FLY_FRACTION * best_s]

        st0, st1, _ = stint_span(session, driver, int(fast["Stint"]), pad=2.0)
        mp = (pos_d["t"] >= st0) & (pos_d["t"] <= st1)
        mc = (spd_d["t"] >= st0) & (spd_d["t"] <= st1)
        hp = calibrate_session_hp(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                                  spd_d["t"][mc], spd_d["V"][mc], order=4)

        span: dict[int, tuple] = {}
        proc, ctrl = [], []
        for _, lap in flying.iterrows():
            sn = int(lap["Stint"])
            if sn not in span:
                s0, s1, _ = stint_span(session, driver, sn, pad=2.0)
                span[sn] = (s0, s1)
            s0, s1 = span[sn]
            t0 = float(lap["LapStartTime"].total_seconds())
            t1 = float(lap["Time"].total_seconds())
            try:
                ss, info = fit_lap(pos_d, spd_d, t0, t1, hp, overhang=8.0, bounds=(s0, s1))
                dfp = smoother_to_processed_telemetry(ss, info["lap_t"], driver_id=driver,
                                                      lap_number=int(lap["LapNumber"]))
            except Exception as exc:  # one bad lap must not sink the driver
                logger.debug("skip lap %s: %s", int(lap["LapNumber"]), exc)
                continue
            cdf = _build_control_df(session, num, t0, t1)
            if dfp.empty or cdf.empty:
                continue
            proc.append(dfp)
            ctrl.append(cdf)

        if not proc:
            return _err("no_laps")
        processed = pd.concat(proc, ignore_index=True)
        control_df = pd.concat(ctrl, ignore_index=True)
        params = ParameterEstimator(cfg).estimate_parameters(
            processed, control_df=control_df, weather={"air_density": rho}, era=era,
        )
        env = CapabilityEnvelope.from_parameters(params, rho, cfg)
        fallback_lat = bool(params.fit_quality_metrics.get("fallback_lateral", True))
        apex = extract_apex_observations(
            processed, air_density=rho,
            lateral_envelope=params.lateral if not fallback_lat else None,
        )
        apex_dicts = [{"v_apex": float(o.v_apex), "radius_m": float(o.radius_m),
                       "a_lat": float(o.a_lat), "on_limit": bool(o.on_limit)} for o in apex]
        p99 = float(processed["speed_ms"].quantile(0.99))
        diag = {"p99_speed": p99, "speed_inflation": p99 > _P99_SPEED_LIMIT,
                "chi2": float(hp.get("chi2_pos", float("nan"))), "ell_used": float(hp["ell"])}
        return record_from_params(
            params, year=year, gp_name=gp_name, round_idx=round_idx, session_type=session_type,
            driver=driver, constructor=constructor, rho=rho, best_lap_s=best_s,
            n_flying_laps=len(proc), apex_obs=apex_dicts, env=env, diag=diag,
        )
    except Exception as exc:  # noqa: BLE001 — batch must never crash on one driver
        logger.warning("fit_driver failed %s %s %s: %s", year, gp_name, driver, exc)
        return _err("error", str(exc))
```

- [ ] **Step 4: Run the pure test to verify it passes**

Run: `py -m pytest tests/unit/physics/test_session_fit.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Add a cache-gated smoke test for the full chain**

```python
# append to tests/unit/physics/test_session_fit.py
import os
from pathlib import Path

CACHE = Path("outputs/cache")
pytestmark_cache = pytest.mark.skipif(
    not CACHE.exists() or os.environ.get("F1_RUN_CACHE_TESTS") != "1",
    reason="offline FastF1 cache smoke test (set F1_RUN_CACHE_TESTS=1 to run)",
)


@pytestmark_cache
def test_fit_driver_smoke_on_cached_session():
    from src.physics.session_fit import load_quali_session, fit_driver
    session, rho = load_quali_session(2023, "Great Britain", "Q")
    rec = fit_driver(session, "VER", year=2023, gp_name="Great Britain", round_idx=10,
                     session_type="Q", constructor="Red Bull Racing", rho=rho)
    assert rec.fit_status == "ok"
    assert rec.theta_D is not None and rec.theta_D > 0
    assert rec.n_apex > 0
```

- [ ] **Step 6: Run the smoke test (only if cache present)**

Run: `F1_RUN_CACHE_TESTS=1 py -m pytest tests/unit/physics/test_session_fit.py::test_fit_driver_smoke_on_cached_session -v`
Expected: PASS, or SKIP if the 2023 British GP Q is not cached. If it fails, report the error (do not paper over — it means the lifted chain diverged from the diagnostics source).

- [ ] **Step 7: Commit**

```bash
git add src/physics/session_fit.py tests/unit/physics/test_session_fit.py
git commit -m "feat(physics): offline single-session fit -> FitRecord (#492 P0)"
```

---

### Task 3: Batch runner (enumeration + resumability + error capture)

**Files:**
- Create: `src/physics/fit_batch.py`
- Create: `scripts/build_physics_fit_store.py`
- Test: `tests/unit/physics/test_fit_batch.py`

**Interfaces:**
- Consumes: `FitStore` (Task 1), `FitRecord` (Task 1), `load_quali_session` + `fit_driver` (Task 2), `get_calendar` (`src.utils.constants`).
- Produces:
  - `run_batch(store, *, seasons, sessions, cache, force=False, load_session_fn=load_quali_session, fit_driver_fn=fit_driver, calendar_fn=get_calendar, list_drivers_fn=_list_drivers, log=print) -> dict` — iterates `seasons × calendar(year) × sessions × drivers`; skips `(year, gp, session, driver)` already in the store unless `force`; on a session that fails to load, records nothing and continues; on a driver fit, always upserts the returned `FitRecord` (incl. `error`/`no_laps`). Returns counts `{"fitted":, "skipped":, "errors":, "sessions_missing":}`. The `*_fn` seams exist so the test injects fakes (no cache needed).
  - `_list_drivers(session) -> list[tuple[str, str]]` — `[(abbrev, constructor), ...]` from `session.drivers` via `session.get_driver(num)` (`Abbreviation`, `TeamName`).

- [ ] **Step 1: Write the failing test (injected fakes — no cache)**

```python
# tests/unit/physics/test_fit_batch.py
import pytest
from src.physics.fit_store import FitStore, FitRecord
from src.physics import fit_batch


def _ok_record(year, gp, ses, driver):
    return FitRecord(
        year=year, gp_name=gp, round_idx=1, session_type=ses, driver=driver,
        constructor="TeamX", fit_status="ok", error=None, best_lap_s=80.0,
        fit_air_density=1.2, n_flying_laps=3, n_samples_used=1000,
        theta_D=7e-4, theta_R=0.02, theta_D_open=None, theta_D_source="x",
        fallback_longitudinal=False, fallback_reason_long=None, cda=1.1,
        A0=18.0, A2=5e-3, k_tire=0.0, g_track=1.0, ceiling=None, aero_identifiable=True,
        fallback_lateral=False, a_b=-45.0, b_b=-2e-3, a_t=12.0, b_t=4e-3,
        traction_source="measured", braking_source="measured", ceiling_trustworthy=False,
        n_apex=10, n_on_limit=8, p99_speed=90.0, speed_inflation=False, chi2=1.0, ell_used=3.0,
        lateral_covariance=[[1e-2, 0], [0, 1e-6]], braking_covariance=None,
        traction_covariance=None, fit_quality_metrics={}, apex_obs=[],
    )


def _fakes():
    calls = {"fits": []}

    def calendar_fn(year):
        return ["Bahrain", "Spain"]

    def load_session_fn(year, gp, ses, cache, offline=True):
        if gp == "Spain":
            raise RuntimeError("not cached")  # session-missing path
        return (("SESSION", year, gp, ses), 1.2)

    def list_drivers_fn(session):
        return [("VER", "TeamX"), ("PER", "TeamX")]

    def fit_driver_fn(session, driver, *, year, gp_name, round_idx, session_type,
                      constructor, rho, cfg=None):
        calls["fits"].append((year, gp_name, driver))
        return _ok_record(year, gp_name, session_type, driver)

    return calls, calendar_fn, load_session_fn, list_drivers_fn, fit_driver_fn


def test_run_batch_fits_drivers_skips_missing_sessions(tmp_path):
    store = FitStore(str(tmp_path / "f.db"))
    calls, cal, load, lst, fit = _fakes()
    res = fit_batch.run_batch(
        store, seasons=[2023], sessions=["Q"], cache="x", force=False,
        load_session_fn=load, fit_driver_fn=fit, calendar_fn=cal,
        list_drivers_fn=lst, log=lambda *a, **k: None,
    )
    assert res["fitted"] == 2          # Bahrain VER, PER
    assert res["sessions_missing"] == 1  # Spain
    assert len(store.load_fits(year=2023)) == 2


def test_run_batch_is_resumable(tmp_path):
    store = FitStore(str(tmp_path / "f.db"))
    calls, cal, load, lst, fit = _fakes()
    fit_batch.run_batch(store, seasons=[2023], sessions=["Q"], cache="x",
                        load_session_fn=load, fit_driver_fn=fit, calendar_fn=cal,
                        list_drivers_fn=lst, log=lambda *a, **k: None)
    n_first = len(calls["fits"])
    res = fit_batch.run_batch(store, seasons=[2023], sessions=["Q"], cache="x",
                              load_session_fn=load, fit_driver_fn=fit, calendar_fn=cal,
                              list_drivers_fn=lst, log=lambda *a, **k: None)
    assert len(calls["fits"]) == n_first   # second run re-fit nothing
    assert res["skipped"] == 2


def test_run_batch_force_refits(tmp_path):
    store = FitStore(str(tmp_path / "f.db"))
    calls, cal, load, lst, fit = _fakes()
    fit_batch.run_batch(store, seasons=[2023], sessions=["Q"], cache="x",
                        load_session_fn=load, fit_driver_fn=fit, calendar_fn=cal,
                        list_drivers_fn=lst, log=lambda *a, **k: None)
    fit_batch.run_batch(store, seasons=[2023], sessions=["Q"], cache="x", force=True,
                        load_session_fn=load, fit_driver_fn=fit, calendar_fn=cal,
                        list_drivers_fn=lst, log=lambda *a, **k: None)
    assert len(calls["fits"]) == 4   # 2 + 2 (forced re-fit)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_fit_batch.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.fit_batch'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/physics/fit_batch.py
"""Batch driver for the per-session physics fit store (Epic 2 P0, #492).

Enumerates seasons × calendar × sessions × drivers, fits each driver offline,
and upserts the result. Idempotent (skip already-stored unless force) and
crash-tolerant (a missing session or a failing driver is recorded, never
fatal). The *_fn seams let tests inject fakes without the FastF1 cache.
"""
from __future__ import annotations

from typing import Any, Callable

from src.utils.constants import get_calendar
from src.physics.fit_store import FitStore
from src.physics.session_fit import load_quali_session, fit_driver


def _list_drivers(session) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for num in session.drivers:
        try:
            info = session.get_driver(num)
        except Exception:
            continue
        out.append((str(info.get("Abbreviation", num)), str(info.get("TeamName", "Unknown"))))
    return out


def run_batch(
    store: FitStore, *, seasons, sessions, cache, force: bool = False,
    load_session_fn: Callable = load_quali_session,
    fit_driver_fn: Callable = fit_driver,
    calendar_fn: Callable = get_calendar,
    list_drivers_fn: Callable = _list_drivers,
    log: Callable = print,
) -> dict:
    counts = {"fitted": 0, "skipped": 0, "errors": 0, "sessions_missing": 0}
    for year in seasons:
        try:
            rounds = calendar_fn(year)
        except KeyError:
            log(f"[skip] no calendar for {year}")
            continue
        for round_idx, gp in enumerate(rounds, start=1):
            for ses in sessions:
                try:
                    session, rho = load_session_fn(year, gp, ses, cache)
                except Exception as exc:  # session absent from cache, etc.
                    counts["sessions_missing"] += 1
                    log(f"[miss] {year} {gp} {ses}: {exc}")
                    continue
                for driver, constructor in list_drivers_fn(session):
                    if not force and store.has_fit(year, gp, ses, driver):
                        counts["skipped"] += 1
                        continue
                    rec = fit_driver_fn(
                        session, driver, year=year, gp_name=gp, round_idx=round_idx,
                        session_type=ses, constructor=constructor, rho=rho,
                    )
                    store.upsert(rec)
                    if rec.fit_status == "ok":
                        counts["fitted"] += 1
                    else:
                        counts["errors"] += 1
                    log(f"[{rec.fit_status}] {year} {gp} {ses} {driver}")
    return counts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/unit/physics/test_fit_batch.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Write the thin CLI**

```python
# scripts/build_physics_fit_store.py
"""Build the per-session physics fit store across seasons (Epic 2 P0, #492).

Offline only — reads the FastF1 cache, never the network. Resumable: re-run to
fill gaps; pass --force to re-fit. Example:

    py scripts/build_physics_fit_store.py --seasons 2022 2023 --sessions Q
    py scripts/build_physics_fit_store.py --seasons 2018 2019 2020 2021 2022 2023 2024 2025
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.physics.fit_store import FitStore
from src.physics.fit_batch import run_batch

DEFAULT_DB = str(REPO / "data" / "physics_fits.db")
DEFAULT_CACHE = str(REPO / "outputs" / "cache")


def _ts_log(msg: str) -> None:
    print(f"{dt.datetime.now():%H:%M:%S} {msg}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Build the per-session physics fit store (#492 P0)")
    p.add_argument("--seasons", type=int, nargs="+",
                   default=[2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
    p.add_argument("--sessions", nargs="+", default=["Q"])
    p.add_argument("--db", default=DEFAULT_DB)
    p.add_argument("--cache", default=DEFAULT_CACHE)
    p.add_argument("--force", action="store_true", help="re-fit rows already in the store")
    args = p.parse_args()

    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    store = FitStore(args.db)
    _ts_log(f"store={args.db} seasons={args.seasons} sessions={args.sessions} force={args.force}")
    counts = run_batch(store, seasons=args.seasons, sessions=args.sessions,
                       cache=args.cache, force=args.force, log=_ts_log)
    _ts_log(f"DONE {counts}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**

```bash
git add src/physics/fit_batch.py scripts/build_physics_fit_store.py tests/unit/physics/test_fit_batch.py
git commit -m "feat(physics): resumable offline batch runner for the fit store (#492 P0)"
```

---

### Task 4: Evidence report (coverage + identifiability)

**Files:**
- Create: `src/physics/fit_evidence.py`
- Create: `scripts/physics_fit_evidence.py`
- Test: `tests/unit/physics/test_fit_evidence.py`

**Interfaces:**
- Consumes: `FitStore.load_fits` (Task 1) → DataFrame.
- Produces:
  - `axis_identifiability(df) -> dict` — per-axis reliability: `fallback_lateral` rate, `fallback_longitudinal` rate, `braking_present` rate (`a_b` not null), `traction_present` rate, `aero_identifiable` rate, `ceiling_present` rate, `speed_inflation` rate. Each a fraction in [0, 1] over the `ok` rows.
  - `pooling_feasibility(df) -> pandas.DataFrame` — rows `(year, constructor, n_sessions)` sorted descending: how many quali fits each car-season has (the pool depth that P2 can borrow across).
  - `render_markdown(df) -> str` — a report stitching the two tables plus row counts.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/physics/test_fit_evidence.py
import pandas as pd
import pytest
from src.physics import fit_evidence


def _df():
    rows = [
        dict(year=2023, constructor="RBR", driver="VER", fit_status="ok",
             fallback_lateral=False, fallback_longitudinal=False, a_b=-45.0, a_t=12.0,
             aero_identifiable=True, ceiling=None, speed_inflation=False),
        dict(year=2023, constructor="RBR", driver="PER", fit_status="ok",
             fallback_lateral=True, fallback_longitudinal=False, a_b=None, a_t=12.0,
             aero_identifiable=False, ceiling=30.0, speed_inflation=True),
        dict(year=2023, constructor="FER", driver="LEC", fit_status="ok",
             fallback_lateral=False, fallback_longitudinal=True, a_b=-44.0, a_t=None,
             aero_identifiable=True, ceiling=None, speed_inflation=False),
    ]
    return pd.DataFrame(rows)


def test_axis_identifiability_rates():
    out = fit_evidence.axis_identifiability(_df())
    assert out["fallback_lateral"] == pytest.approx(1 / 3)
    assert out["braking_present"] == pytest.approx(2 / 3)
    assert out["traction_present"] == pytest.approx(2 / 3)
    assert out["aero_identifiable"] == pytest.approx(2 / 3)
    assert out["speed_inflation"] == pytest.approx(1 / 3)


def test_pooling_feasibility_counts_sessions_per_car_season():
    tbl = fit_evidence.pooling_feasibility(_df())
    rbr = tbl[(tbl["year"] == 2023) & (tbl["constructor"] == "RBR")].iloc[0]
    assert rbr["n_sessions"] == 2


def test_render_markdown_contains_sections():
    md = fit_evidence.render_markdown(_df())
    assert "Axis identifiability" in md
    assert "Pooling feasibility" in md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/unit/physics/test_fit_evidence.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.physics.fit_evidence'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/physics/fit_evidence.py
"""First evidence report over the per-session fit store (Epic 2 P0, #492).

Answers the question the P0 batch run exists to answer: which axes are
single-session-identifiable across the whole dataset (vs needing the pool),
and how much pool depth each car-season has.
"""
from __future__ import annotations

import pandas as pd


def axis_identifiability(df: pd.DataFrame) -> dict:
    ok = df[df["fit_status"] == "ok"]
    n = len(ok)
    if n == 0:
        return {}
    return {
        "fallback_lateral": float(ok["fallback_lateral"].mean()),
        "fallback_longitudinal": float(ok["fallback_longitudinal"].mean()),
        "braking_present": float(ok["a_b"].notna().mean()),
        "traction_present": float(ok["a_t"].notna().mean()),
        "aero_identifiable": float(ok["aero_identifiable"].fillna(False).mean()),
        "ceiling_present": float(ok["ceiling"].notna().mean()),
        "speed_inflation": float(ok["speed_inflation"].mean()),
    }


def pooling_feasibility(df: pd.DataFrame) -> pd.DataFrame:
    ok = df[df["fit_status"] == "ok"]
    tbl = (ok.groupby(["year", "constructor"]).size()
           .reset_index(name="n_sessions")
           .sort_values("n_sessions", ascending=False, ignore_index=True))
    return tbl


def render_markdown(df: pd.DataFrame) -> str:
    ok_n = int((df["fit_status"] == "ok").sum())
    lines = [
        "# Physics fit store — first evidence (#492 P0)", "",
        f"Rows: {len(df)} total, {ok_n} ok.", "",
        "## Axis identifiability (fraction of ok fits)", "",
    ]
    for k, v in axis_identifiability(df).items():
        lines.append(f"- {k}: {v:.1%}")
    lines += ["", "## Pooling feasibility (quali fits per car-season)", ""]
    lines.append(pooling_feasibility(df).to_markdown(index=False))
    return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/unit/physics/test_fit_evidence.py -v`
Expected: PASS (3 passed). If `to_markdown` raises about `tabulate`, install it (`py -m pip install tabulate`) or replace with a manual table; prefer the manual table to avoid a new dep.

- [ ] **Step 5: Write the thin CLI**

```python
# scripts/physics_fit_evidence.py
"""Emit the first-evidence report over the physics fit store (#492 P0)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.physics.fit_store import FitStore
from src.physics import fit_evidence

DEFAULT_DB = str(REPO / "data" / "physics_fits.db")


def main() -> None:
    p = argparse.ArgumentParser(description="Physics fit store evidence report (#492 P0)")
    p.add_argument("--db", default=DEFAULT_DB)
    p.add_argument("--out", default=str(REPO / "reports" / "physics" / "fit_store_evidence.md"))
    args = p.parse_args()
    df = FitStore(args.db).load_fits(status=None)
    md = fit_evidence.render_markdown(df)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"\n[wrote] {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**

```bash
git add src/physics/fit_evidence.py scripts/physics_fit_evidence.py tests/unit/physics/test_fit_evidence.py
git commit -m "feat(physics): first-evidence report over the fit store (#492 P0)"
```

---

### Task 5: First real batch run + evidence (verification, not unit-tested)

**Files:** none created — this runs the pipeline end-to-end on the real cache.

This is the payoff: the first cross-dataset evidence. It is a manual verification step (heavy, uses the 36 GB cache), not a pytest.

- [ ] **Step 1: Smoke one season to confirm the chain runs end-to-end**

Run: `py scripts/build_physics_fit_store.py --seasons 2023 --sessions Q`
Expected: timestamped `[ok]/[no_laps]/[error]/[miss]` lines; a final `DONE {...}` with `fitted` ≈ 18–22 × rounds. `data/physics_fits.db` exists.

- [ ] **Step 2: Generate the evidence report**

Run: `py scripts/physics_fit_evidence.py`
Expected: prints the report and writes `reports/physics/fit_store_evidence.md`. Read it: confirm `fallback_lateral`, `braking_present`, `aero_identifiable` rates are sane (these tell us which axes need the pool), and the pooling-feasibility table shows ~the right number of quali fits per car-season.

- [ ] **Step 3: Report findings to the controller**

Summarise the evidence numbers (do not commit `data/physics_fits.db` — it is a derived artifact; confirm it is gitignored, add it to `data/.gitignore` if not). Commit only `reports/physics/fit_store_evidence.md` if the controller wants the evidence tracked.

```bash
git add reports/physics/fit_store_evidence.md
git commit -m "docs(physics): first fit-store evidence (2023 Q) (#492 P0)"
```

---

## Self-Review

**Spec coverage** (against the P0 section of `2026-06-17-physics-cross-session-pooling-design.md`):
- "persist each car-session-driver's per-axis posteriors (value, covariance, identifiability/SNR flags, n_laps, fallback reason) keyed to weekend metadata" → Task 1 `FitRecord` + `FitStore`. ✓
- "Run the Epic-1 engine over every car-quali-session in the 2018–2025 DBs" → Task 2 (fit) + Task 3 (batch over `get_calendar` seasons). ✓ (telemetry source corrected: FastF1 offline cache, not the SQLite DBs — the DBs hold classifications, not telemetry.)
- "the first real evidence dump: fallback rates and σ distributions per axis" → Task 4 `axis_identifiability` + Task 5 run. (σ distributions: covariances are persisted per axis in Task 1; the report surfaces presence/fallback rates now and the σ histograms are a fast follow once the controller sees the coverage.)
- Resumable / offline / idempotent / per-driver error capture → Task 3. ✓
- apex observations persisted for later per-weekend `apex_pace` → Task 1 `apex_obs` column + `load_apex_weekend`. ✓

**Placeholder scan:** no TBD/TODO; every code step shows complete code; the lifted chain is reproduced in full in Task 2.

**Type consistency:** `FitRecord` field names are identical across Tasks 1–4; `run_batch`'s injected `*_fn` signatures match `load_quali_session`/`fit_driver`/`get_calendar`/`_list_drivers`; `record_from_params` is the single producer of `ok` records and matches `FitRecord` exactly.

**Known follow-ups (out of P0 scope, noted for the controller):** σ-distribution histograms in the evidence report; extending sessions beyond `Q` (FP/SQ) once P5 needs them; canonical cross-season constructor ids (P2). None block P0.
