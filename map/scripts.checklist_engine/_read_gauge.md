# scripts.checklist_engine:_read_gauge
function, scripts/checklist_engine.py:1201, 12 lines

```python
def _read_gauge(base_dir: Path | None)
```

Read a fresh `Reading` for this checklist, or None. Fail-safe: an absent

reader binding or unresolvable path collapses to None, and the reader itself
never raises (every failure mode — absent/corrupt/malformed/stale/clock-skew —
is already collapsed to None inside `read()`). A None reading must produce
neither a SOFT question nor a HARD refusal.

calls internal: _gauge_path
reads internal: _gauge_reader x2
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
