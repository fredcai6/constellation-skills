# scripts.hooks.gauge_writer_hook:_clear_uncalibrated_flag
function, scripts/hooks/gauge_writer_hook.py:439, 10 lines

```python
def _clear_uncalibrated_flag(gauge_path: Path) -> None
```

Drop a stale flag once the model resolves again -- otherwise adding the

missing row to MODEL_WINDOWS would fix the reading but leave the warning
nagging forever.

calls internal: _uncalibrated_path
reads stdlib: builtins.FileNotFoundError, builtins.OSError
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
