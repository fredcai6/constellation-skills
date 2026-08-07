# scripts.gauge_reader:skip_reason
function, scripts/gauge_reader.py:319, 35 lines

```python
def skip_reason(gauge_path: str | Path) -> dict | None
```

Why the writer hook wrote NO reading at this gauge path, if it knows --

mirrors `uncalibrated_model`'s fail-safe contract exactly: never raises,
any problem (absent file, corrupt JSON, missing/malformed fields) is None.

Returns `{"reason": str, "observed_at": datetime, "candidate_count": int}`
-- `candidate_count` only present when the source file carries it as a
valid non-bool int (it only applies to the ambiguous-binding reason).
`observed_at` is parsed the same way `_parse_fields` parses a gauge
record's own `observed_at`.

Deliberately NOT staleness-checked, same rationale as `raw_record`: this
answers "why is there no reading", which a caller displays with its own
raw age, never a pass/fail this function decides.

calls internal: _parse_observed_at
calls stdlib: builtins.isinstance x4, json.loads, pathlib.Path
reads internal: SKIP_FILENAME
reads stdlib: builtins.OSError, builtins.ValueError, builtins.bool, builtins.dict, builtins.int, builtins.str, json (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
