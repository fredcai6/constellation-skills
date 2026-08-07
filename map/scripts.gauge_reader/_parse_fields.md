# scripts.gauge_reader:_parse_fields
function, scripts/gauge_reader.py:155, 42 lines

```python
def _parse_fields(record: dict) -> Reading | None
```

Validate an already-decoded record dict's required fields, types, and

range, and convert it to a Reading -- WITH NO staleness, clock-skew, or
calibration-table gate. Never raises: any problem -- missing field, wrong
type, out-of-range value -- returns None.

This is the field-shape half of what `_parse_record` used to do inline.
It is shared by `_parse_record` (which layers staleness/skew/calibration
on top of the Reading this returns) and `raw_record` (which reports the
Reading's fields as-is, with nothing layered on top) -- one place for the
required-fields/types/range checks, so the two callers cannot drift.

calls internal: Reading, _parse_observed_at
calls stdlib: builtins.isinstance x5, builtins.float x2
reads internal: REQUIRED_FIELDS
reads stdlib: builtins.bool x2, builtins.int x2, builtins.float, builtins.str

referenced by: 2 sites, this module only
