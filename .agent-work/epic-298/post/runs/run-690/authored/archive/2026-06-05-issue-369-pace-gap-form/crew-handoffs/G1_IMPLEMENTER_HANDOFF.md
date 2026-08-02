# Implementer Handoff

## Gate
g1 — pace-gap history provider (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## Task
Build the data layer for quali pace-gap history. Two pieces, plus tests:

**(a) DatabaseManager batch query** — new read method on the metadata mixin
(`src/data/database/_metadata.py`, next to `get_session_classifications_batch`
at line 429 and `get_practice_lap_times` at line 783, which are the patterns to
mirror):

```python
def get_quali_best_valid_laps_batch(
    self, year: int, round_nums: List[int]
) -> Dict[int, Dict[str, float]]:
    """{round_num: {driver_id: best_valid_lap_seconds}} for Q sessions."""
```

- Join `lap_times lt JOIN sessions s ON lt.session_id = s.id`,
  `s.year = ? AND s.round_num IN (...) AND s.session_type = 'Q'`.
- Lap validity filters (the frozen plan fixed these to mirror the practice
  convention — do not add or remove): `lt.valid_lap = 1`,
  `lt.pit_in_time IS NULL`, `lt.pit_out_time IS NULL`,
  `lt.lap_time IS NOT NULL`. No track_status filter (valid_lap already encodes
  deleted laps; this mirrors the practice-preprocessor convention).
- `MIN(lt.lap_time)` per (round_num, driver_id) — aggregate in SQL.
- Verify the `lap_time` unit from the schema/ingest code (expected: seconds as
  REAL) and note the verification in your result.
- Pattern conformance: empty `round_nums` → `{}` early return; requested rounds
  pre-seeded as empty dicts; `sqlite3.connect(self.db_path, timeout=DB_TIMEOUT)`;
  `except sqlite3.Error` → `logger.error` + raise `DatabaseError(..., operation="SELECT")`.

**(b) Evo-side provider** — new module `src/evo_predictor/quali_pace_gap_history.py`:

- Pure gap computation: for one event, given `{driver_id: best_lap_seconds}`,
  return `{driver_id: (t - field_median) / field_median}` where `field_median`
  is the median of best laps over drivers **with** a valid best lap that event.
  Empty input → `{}`. Single driver → gap `0.0`. Lower = better (faster lap →
  negative gap).
- `build_quali_pace_gap_history(db, year, round_num) -> Dict[str, List[float]]`:
  one batch call for rounds `1..round_num-1`; per driver a list aligned to
  those rounds **in order** — index `i` holds round `i+1`'s gap, `float('nan')`
  where the driver has no valid lap that round. Driver universe = union of
  drivers appearing in any prior round's best laps. A prior round with no Q
  laps at all contributes nan for every driver (it stays in the alignment —
  same contract as `quali_history_full` built at
  `src/evo_predictor/data_adapter/_assemble.py:138`).
- `round_num <= 1` → `{}` (no prior rounds). Never query the current round.

**(c) Unit tests** —
- `tests/unit/data/test_quali_best_laps_query.py`: build a fixture SQLite DB
  (tmp_path; minimal `sessions` + `lap_times` per `src/data/schema.sql`; look
  at existing `tests/unit/data/` fixtures for conventions). Cover: filter
  correctness (invalid lap excluded, pit-in/pit-out lap excluded, NULL
  lap_time excluded, non-Q session excluded, other year excluded), MIN per
  driver, batch shape over multiple rounds, requested-but-absent round → empty
  dict, empty round_nums → {}.
- `tests/unit/evo_predictor/test_quali_pace_gap_history.py`: gap math (median
  correctness, sign: slower → positive), single-driver event → 0.0, empty
  event, missing driver → nan at the right index, alignment/order over rounds
  1..n−1, round_num=1 → {}, all-missing round stays as a nan column. Use a
  stub/fake db object exposing the batch method (no real DB needed for the
  provider tests).

## Protected Intent
- DB is the only data source — no FastF1/Jolpica imports anywhere.
- Missingness explicit: nan, never imputed, never dropped from the alignment.
- As-of: prior rounds only (`1..round_num-1`); current round never touched.
- Pure addition: no existing method, model, or adapter changes; nothing else
  in the codebase changes behavior.

## Test Mode
TDD required — new logic on the promoted prediction path (project rule:
test-led; no implementation-only logic commits).

## Close Criteria
- `py -m pytest tests/unit/data/test_quali_best_laps_query.py tests/unit/evo_predictor/test_quali_pace_gap_history.py -q` green.
- `py -m pytest tests/unit/data -q` green (no regression in the data region).
- `py -m src.utils.simplification_limits --paths src/data/database/_metadata.py src/evo_predictor/quali_pace_gap_history.py tests/unit/data/test_quali_best_laps_query.py tests/unit/evo_predictor/test_quali_pace_gap_history.py` passes (strict).
- Gap formula, alignment contract, and filters exactly as specified above.

## Allowed Scope
- `src/data/database/_metadata.py` (add one method)
- `src/evo_predictor/quali_pace_gap_history.py` (new)
- `tests/unit/data/test_quali_best_laps_query.py` (new)
- `tests/unit/evo_predictor/test_quali_pace_gap_history.py` (new)

## Specific Exclusions
- `src/evo_predictor/models/` (DriverFeatures — G2's job)
- All adapters and `src/evo_predictor/data_adapter/` (G2/G3)
- `run.py`, gold config, `module_adapters/` (G3)
- `src/data/schema.sql` (read-only query; no schema change)
- `src/data/collector.py`, `load_fastf1.py`

## Constraints
- `py` not `python` on this machine.
- Gap formula is frozen: `(t − field_median) / field_median`; raw values, no
  clipping/winsorizing; lower = better.
- Mirror the existing mixin code style (docstring format, placeholders,
  DB_TIMEOUT, DatabaseError, logger usage).
- Type hints consistent with the file (the repo runs pyright in CI).

## Required Evidence
- pytest output for both new test files and `tests/unit/data`.
- simplification_limits output.
- One-line note confirming the lap_time unit verification.

## Verification Commands
```bash
py -m pytest tests/unit/data/test_quali_best_laps_query.py tests/unit/evo_predictor/test_quali_pace_gap_history.py -q
py -m pytest tests/unit/data -q
py -m src.utils.simplification_limits --paths src/data/database/_metadata.py src/evo_predictor/quali_pace_gap_history.py tests/unit/data/test_quali_best_laps_query.py tests/unit/evo_predictor/test_quali_pace_gap_history.py
```

## Suggested Model Tier
simple bounded — precedents given inline; low ambiguity.

## Authority
Human-confirmed problem statement at
`.agent-work/issue-369-pace-gap-form/PROBLEM_STATEMENT.md`; gate plan frozen.
You may choose internal helper structure and exact test-case naming. You must
NOT decide alone: changing the gap formula, alignment contract, validity
filters, method signature semantics, or touching any excluded file.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must
be touched, required evidence cannot be produced (e.g. schema lacks an assumed
column), or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit,
out-of-scope observations.
