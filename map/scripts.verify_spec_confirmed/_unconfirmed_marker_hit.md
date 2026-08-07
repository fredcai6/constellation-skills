# scripts.verify_spec_confirmed:_unconfirmed_marker_hit
function, scripts/verify_spec_confirmed.py:125, 13 lines

```python
def _unconfirmed_marker_hit(text: str) -> str | None
```

Return the offending line if the marker appears as a status/header

line (not merely mentioned in prose), else None.

calls stdlib: re.sub
reads internal: _UNCONFIRMED_MARKER_RE
reads stdlib: re (module)
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
