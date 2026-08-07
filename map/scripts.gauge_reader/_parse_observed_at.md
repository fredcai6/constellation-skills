# scripts.gauge_reader:_parse_observed_at
function, scripts/gauge_reader.py:137, 16 lines

```python
def _parse_observed_at(raw_value) -> datetime | None
```

Parse an `observed_at` value into a tz-aware datetime, or None if it

isn't a well-formed ISO-8601 string. A naive timestamp is assumed UTC --
the same convention `_parse_fields` and `_parse_record` have always used.
Shared by `_parse_fields` (the record's `observed_at` field) and
`skip_reason` (the sidecar's own `observed_at` field) so this parse-and-
assume-UTC logic lives in exactly one place.

calls stdlib: builtins.isinstance, datetime.datetime.fromisoformat
reads stdlib: builtins.ValueError, builtins.str, datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
