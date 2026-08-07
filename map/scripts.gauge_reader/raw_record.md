# scripts.gauge_reader:raw_record
function, scripts/gauge_reader.py:269, 34 lines

```python
def raw_record(gauge_path: str | Path) -> dict | None
```

The gauge file's own facts -- `fill_fraction`, `model`, `observed_at`

(a parsed, tz-aware datetime) -- with field-shape validation ONLY. NO
staleness check, NO clock-skew check, NO calibration-table check: this is
a raw report, not a judgment.

Exists for exactly one caller-facing purpose: when `read()` itself
rejects the file at this path (e.g. it is simply too old), this is the
one remaining honest thing to say about it -- the file's last recorded
numbers, displayed as-is, so a frozen `gauge.json` is never silently
mistaken for a fresh low reading. A caller must render these facts raw
(age included) and must not re-derive a soft/hard verdict from them --
that verdict is exactly what `read()` already declined to give.

Never raises: any problem -- absent file, corrupt JSON, missing/
malformed fields -- returns None, same fail-safe contract as `read()`.

calls internal: _parse_fields
calls stdlib: builtins.isinstance, json.loads, pathlib.Path
reads stdlib: builtins.OSError, builtins.ValueError, builtins.dict, json (module)
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
