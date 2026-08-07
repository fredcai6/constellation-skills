# scripts.run_crew:_print_drift_hint_if_any
function, scripts/run_crew.py:241, 9 lines

```python
def _print_drift_hint_if_any(stderr_path: Path) -> None
```

Best-effort drift sniff on a failed launch's captured stderr.

calls internal: cli_drift_hint
calls stdlib: builtins.print
reads stdlib: builtins.OSError, sys (module), sys.stderr
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
