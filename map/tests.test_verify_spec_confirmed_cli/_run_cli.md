# tests.test_verify_spec_confirmed_cli:_run_cli
function, tests/test_verify_spec_confirmed_cli.py:69, 8 lines

```python
def _run_cli(tmp_path: Path, text: str) -> subprocess.CompletedProcess
```

HOLE: no docstring

calls stdlib: builtins.str x2, subprocess.run
reads internal: SCRIPT
reads stdlib: subprocess (module), sys (module), sys.executable
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
