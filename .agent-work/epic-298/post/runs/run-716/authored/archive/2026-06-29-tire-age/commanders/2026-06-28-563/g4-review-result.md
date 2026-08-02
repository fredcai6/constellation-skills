# Gate g4 Review Result

**REVIEW_RESULT: APPROVE**

Reviewed by: constellation-reviewer  
Commit: `d5b6297d`  
Branch: `feat/563-race-fit-path`  
Date: 2026-06-28

---

## Per-Check Findings (10 items)

1. **Import works** — PASS. `from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord` succeeds (confirmed by test collection and TestImport class, 2 tests passed).

2. **`upsert(record)` uses INSERT OR REPLACE** — PASS. Line 309: `"INSERT OR REPLACE INTO race_stint_estimates ({cols_sql}) VALUES ({placeholders})"`. Idempotency confirmed by `test_upsert_idempotent` and `test_upsert_replaces_on_pk_conflict`.

3. **`has(year, gp_name, driver, stint_num, compound)` works** — PASS. Signature at line 314–331 matches spec. Session_type defaults to `"R"`. Tests confirm: present→True, absent→False, session_type distinguishes rows.

4. **`load(year=...)` returns a DataFrame** — PASS. Uses `pd.read_sql_query`. Tests confirm empty DataFrame on no rows, filtered by year, session_type, and status. JSON columns deserialized after load.

5. **PK includes `driver`, `stint_num`, `compound`; does NOT include `constructor`** — PASS. `_PK` tuple at line 40: `("year", "gp_name", "session_type", "driver", "stint_num", "compound")`. `constructor` is absent from the dataclass fields. Two dedicated tests confirm this.

6. **`session_type` and `cumulative_track_laps` columns in schema** — PASS. Both are declared as dataclass fields (lines 95, 100) and appear in the schema via `_cols`. Schema test at line 289–302 confirms column presence via PRAGMA table_info.

7. **JSON blob encoding on covariance columns (5 of them)** — PASS. `_JSON_COLUMNS` at line 42–48 enumerates all five: `lateral_covariance`, `traction_covariance`, `braking_covariance`, `power_drag_covariance`, `coast_covariance`. `upsert` serialises with `json.dumps`; `load` deserialises with `json.loads`. Round-trip tests pass including 3x3 and 2x2 matrices and None.

8. **Table named `race_stint_estimates`** — PASS. Hardcoded at line 296: `"CREATE TABLE IF NOT EXISTS race_stint_estimates ..."` and at line 309 in INSERT. Two tests confirm the table name and that `session_estimates` is absent.

9. **60 tests pass** — PASS. `py -m pytest tests/unit/physics/layer2/test_race_stint_store.py tests/known_answer/test_ver_bahrain_stint.py -v` → 60 passed in 0.37s. 52 unit tests + 8 known-answer structural stubs.

10. **`py scripts/pyright_baseline_diff.py` → `new=0`** — PASS. Output: `base=2 head=2 new=0 fixed=0. No new errors vs origin/main. Gate passed.`

---

## Scope Check

`git diff HEAD~1 HEAD --name-only` shows exactly 4 files:
- `src/physics/layer2/race_stint_store.py` — new file
- `tests/unit/physics/layer2/test_race_stint_store.py` — new file
- `tests/known_answer/test_ver_bahrain_stint.py` — new file
- `src/physics/layer2/stint_estimator.py` — TYPE_CHECKING fix only

The `stint_estimator.py` diff is exactly the 3-line TYPE_CHECKING addition specified in the handoff:
```python
-from typing import Optional
+from typing import TYPE_CHECKING, Optional
+
+if TYPE_CHECKING:
+    import pandas as pd
+    from src.physics.layer2.session_race import RaceStintData
```
No logic changes. No pre-branch files (`estimate_store.py`, `session_estimator.py`, etc.) were touched.

---

## Blockers

None. All stop conditions checked — none triggered.

---

## Out-of-Scope Observations

- `load()` defaults `session_type="R"` but `status=None` (all statuses). This deviates from EstimateStore's default-to-ok pattern intentionally — the docstring explains the rationale. No issue.
- `record_from_stint_estimate()` factory uses `getattr(brk, "covariance", None)` defensively for views that may not have a `covariance` attribute. This is a reasonable guard for the braking/power_drag/coast views, which were described in the handoff as having optional covariance. No concern.
- `_sigma()` clamps negative diagonal values to 0 (line 69: `max(a[i, i], 0.0)`). Good defensive practice for numerical noise.

---

## Workflow Feedback

Clean gate. Scope discipline is excellent — exactly 4 files, no drift. Test coverage is thorough (helpers, schema, upsert/has, load filters, JSON round-trip, persistence). Known-answer file is correctly structured as a stub (structural, not value-based) with a clear comment that value verification requires the real DB. Pyright is green. No issues to flag.
