# scripts.gauge_reader:read
function, scripts/gauge_reader.py:228, 39 lines

```python
def read(path: str | Path, *, now: datetime | None = None, max_age: timedelta = DEFAULT_MAX_AGE) -> Reading | None
```

Read the gauge file at `path` and return a fresh Reading, or None.

Collapses every failure to None and never raises: an absent file, corrupt
JSON, a malformed/missing-field record, a stale record (by `observed_at`),
clock-skew (observed_at in the future beyond tolerance), and a record for a
model with no entry in `_PROFILES` all return None. A Reading that reaches
the caller is therefore fresh, well-formed, AND calibrated -- so the
thresholds it is judged against are the real ones for its model.

`now` and `max_age` are injectable so callers -- and tests -- never touch
the real wall clock: `now` defaults to `datetime.now(timezone.utc)` when
omitted, and `max_age` defaults to DEFAULT_MAX_AGE but can be overridden
per call (e.g. by engine config).

calls internal: _parse_record
calls stdlib: builtins.isinstance, datetime.datetime.now, json.loads, pathlib.Path
reads stdlib: datetime.timezone x2, datetime.timezone.utc x2, builtins.OSError, builtins.ValueError, builtins.dict, datetime.datetime, json (module)
writes internal: read.now x2
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
