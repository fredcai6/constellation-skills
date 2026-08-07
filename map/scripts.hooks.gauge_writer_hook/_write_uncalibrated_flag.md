# scripts.hooks.gauge_writer_hook:_write_uncalibrated_flag
function, scripts/hooks/gauge_writer_hook.py:428, 9 lines

```python
def _write_uncalibrated_flag(gauge_path: Path, uncalibrated: dict) -> None
```

Record that this model has no window, so no reading could be produced.

`observed_at` is the SAMPLED moment carried through from the transcript,
consistent with the gauge record -- not write time.

calls internal: _atomic_write_json, _uncalibrated_path
reads internal: SCHEMA_VERSION

referenced by: 1 sites, this module only
