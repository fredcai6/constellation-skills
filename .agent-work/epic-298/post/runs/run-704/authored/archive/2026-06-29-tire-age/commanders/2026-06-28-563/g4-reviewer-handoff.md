# Reviewer Handoff — Gate g4: Race stint store review

## Gate
`g4` — Race stint store + tests + CI pyright clean

## Survey State Location
Create your review survey at `C:/Programs/f1Brainz-563/.agent-work/563/g4-review/review.json`.

## What Was Implemented

Commit `d5b6297d` on branch `feat/563-race-fit-path`:
- `src/physics/layer2/race_stint_store.py` — NEW (237 lines): `RaceStintRecord`, `RaceStintStore`, `record_from_stint_estimate`, `error_record`
- `tests/unit/physics/layer2/test_race_stint_store.py` — NEW (52 TDD tests)
- `tests/known_answer/test_ver_bahrain_stint.py` — NEW (8 structural stub tests)
- `src/physics/layer2/stint_estimator.py` — TOUCHED (3-line `TYPE_CHECKING` fix for pyright; zero logic change)

## How to Inspect the Diff

```bash
cd C:/Programs/f1Brainz-563
git show d5b6297d --stat
git diff HEAD~1 HEAD -- src/physics/layer2/race_stint_store.py
git diff HEAD~1 HEAD -- src/physics/layer2/stint_estimator.py
```

## Task Statement

Implement `RaceStintStore(db_path)` with `race_stint_estimates` SQLite table (PK: year, gp_name, session_type, driver, stint_num, compound). Store `RaceStintRecord` objects that flatten a `StintEstimate` (all five views) plus `cumulative_track_laps` (W3 axis) and `session_type` (session-agnostic seam). Covariance blobs stored as JSON. Idempotent upsert. Load returns DataFrame.

## Close Criteria

1. `from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord` imports cleanly
2. `RaceStintStore(db_path).upsert(record)` is idempotent (INSERT OR REPLACE)
3. `RaceStintStore(db_path).has(year, gp_name, driver, stint_num, compound)` works
4. `RaceStintStore(db_path).load(year=...)` returns a DataFrame
5. PK = (year, gp_name, session_type, driver, stint_num, compound) — per-driver (NOT per-constructor)
6. Schema has `session_type` and `cumulative_track_laps` columns
7. Covariance blobs serialized as JSON (same pattern as `EstimateStore._cov_list`)
8. Table name is `race_stint_estimates`, NOT `session_estimates`
9. `py -m pytest tests/unit/physics/layer2/test_race_sint_store.py tests/known_answer/test_ver_bahrain_stint.py -v` → 60 passed
10. `py scripts/pyright_baseline_diff.py` → `new=0`

## Specific Exclusions (verify untouched)

Check with: `git diff HEAD~1 HEAD --name-only` — should show ONLY the 4 files listed above

Pre-branch files that MUST be untouched:
- `src/physics/layer2/estimate_store.py`
- `src/physics/layer2/session_estimator.py`
- `src/data/telemetry_store.py`
- Any existing test files

The `stint_estimator.py` touch is EXPECTED: a 3-line TYPE_CHECKING addition — verify it is ONLY:
```python
from typing import TYPE_CHECKING, Optional
# ...
if TYPE_CHECKING:
    import pandas as pd
    from src.physics.layer2.session_race import RaceStintData
```
No logic changes.

## Constraints to Verify

- PK is per-driver (not per-constructor) — `driver` in PK, `constructor` NOT in PK
- `session_type` column present (session-agnostic seam for W3)
- `cumulative_track_laps` column present (W3 track-evolution axis)
- Table = `race_stint_estimates` (not `session_estimates`)
- JSON blob encoding on 5 covariance columns
- `load()` defaults: check that `status=None` returns all rows (implementer notes the known-answer test stores an error record and expects it back)
- `error_record()` produces a valid record with all numeric fields = None, fit_status='error'
- pyright new=0 (already confirmed — verify the command output matches)

## Evidence Produced

- `py -m pytest tests/unit/physics/layer2/test_race_stint_store.py tests/known_answer/test_ver_bahrain_stint.py -v` → **60 passed in 0.36s**
- `py scripts/pyright_baseline_diff.py` → `base=2 head=2 new=0 fixed=0`
- `py -c "from src.physics.layer2.race_stint_store import RaceStintStore, RaceStintRecord; print('ok')"` → `ok`

## Suggested Model Tier

`sonnet` — bounded store pattern; verify schema, PK, JSON blobs, pyright clean

## Stop Conditions

Return BLOCK if:
- PK does NOT include `driver` (or does include `constructor`)
- `session_type` column absent
- `cumulative_track_laps` column absent
- Table named `session_estimates` (wrong)
- JSON covariance blobs not decoded on `load()`
- `stint_estimator.py` diff contains anything beyond the 3-line TYPE_CHECKING addition
- Pre-branch existing files modified

## Return Format

Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (if any), out-of-scope observations, workflow feedback.

Write to `C:/Programs/f1Brainz-563/.agent-work/563/g4-review-result.md`.

ENVIRONMENT: Python = `py`. Working dir = `C:/Programs/f1Brainz-563`.
