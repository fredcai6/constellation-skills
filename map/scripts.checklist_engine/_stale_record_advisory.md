# scripts.checklist_engine:_stale_record_advisory
function, scripts/checklist_engine.py:1310, 21 lines

```python
def _stale_record_advisory(gauge_path: Path | None) -> str
```

When `read()` itself rejected the gauge file at this path (e.g. it is

simply too old, or clock-skewed, or names an uncalibrated model), report
the file's OWN raw facts — fill, model, age — with explicitly NO threshold
judgment: this is not a fresh SOFT/HARD verdict, just the last recorded
number, so a caller never mistakes a frozen reading for a live low one.
Fail-safe like every other gauge-adjacent advisory.

calls internal: _format_age
calls stdlib: datetime.datetime.now
reads internal: _gauge_reader x2
reads stdlib: builtins.Exception, datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
