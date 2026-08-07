# scripts.gauge_reader:_parse_record
function, scripts/gauge_reader.py:199, 27 lines

```python
def _parse_record(record: dict, now: datetime, max_age: timedelta) -> Reading | None
```

Validate an already-decoded record dict and convert it to a Reading.

Never raises: any problem -- missing field, wrong type, out-of-range
value, stale timestamp, clock-skew -- returns None.

calls internal: _parse_fields
reads internal: CLOCK_SKEW_TOLERANCE, _PROFILES
unresolved: 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
