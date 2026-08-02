# g4 Implementer Result — Race Stint Store

**Gate**: g4
**Branch**: feat/563-race-fit-path
**Commit**: d5b6297d
**Status**: COMPLETE

---

## Files Changed

- `src/physics/layer2/race_stint_store.py` — NEW (237 lines)
- `tests/unit/physics/layer2/test_race_stint_store.py` — NEW (52 tests)
- `tests/known_answer/test_ver_bahrain_stint.py` — NEW (8 structural stub tests)
- `src/physics/layer2/stint_estimator.py` — MODIFIED (3 lines: TYPE_CHECKING guard for `pd` and `RaceStintData` — pre-existing g3 pyright errors fixed to satisfy HARD GATE)

---

## Evidence

### Unit tests

```
py -m pytest tests/unit/physics/layer2/test_race_stint_store.py -v
52 passed in 0.38s
```

### Known-answer stub tests

```
py -m pytest tests/known_answer/test_ver_bahrain_stint.py -v
8 passed in 0.21s (all 8)
```

### Import check

```
py -c "from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord; print('ok')"
ok
```

### Pyright baseline diff

```
pyright-baseline-diff: base=2 head=2 new=0 fixed=0
No new errors vs origin/main. Gate passed.
```

---

## Design Notes

### `load()` default `status=None`

The handoff-provided `test_store_round_trip` inserts an `error_record` and calls
`store.load(year=2023)` expecting 1 row. With `status="ok"` as default the error
record would be filtered out. The default was changed to `status=None` (return all).
Callers wanting only ok records pass `status="ok"` explicitly. This is documented
in the docstring.

### `stint_estimator.py` pyright fix

g3 left two `reportUndefinedVariable` errors (new vs origin/main):
- `"pd"` used in string annotations but only imported inside function bodies
- `"RaceStintData"` used as forward ref but never imported at module level

Fix: add `if TYPE_CHECKING:` guard with `import pandas as pd` and
`from src.physics.layer2.session_race import RaceStintData`. Zero logic change.
This was necessary to meet the HARD GATE `new=0` requirement.

---

## Close Criteria Checklist

- [x] `from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord` imports cleanly
- [x] `RaceStintStore(db_path).upsert(record)` is idempotent (INSERT OR REPLACE)
- [x] `has(year, gp_name, driver, stint_num, compound)` works
- [x] `load(year=...)` returns a DataFrame with JSON columns deserialized
- [x] PK = (year, gp_name, session_type, driver, stint_num, compound)
- [x] Schema has `session_type` and `cumulative_track_laps` columns
- [x] Covariance blobs serialized as JSON (same pattern as `EstimateStore._cov_list`)
- [x] `py -m pytest tests/unit/physics/layer2/test_race_stint_store.py -v` passes (52/52)
- [x] `py -m pytest tests/known_answer/test_ver_bahrain_stint.py -v` passes (8/8)
- [x] `py scripts/pyright_baseline_diff.py` → `new=0`
- [x] No existing file modified (except g3's `stint_estimator.py` for pyright fix)
