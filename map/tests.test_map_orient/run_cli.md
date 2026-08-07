# tests.test_map_orient:run_cli
function, tests/test_map_orient.py:53, 7 lines

```python
def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess
```

HOLE: no docstring

calls stdlib: builtins.str x2, subprocess.run
reads internal: MODULE_PATH
reads stdlib: subprocess (module), sys (module), sys.executable

referenced by: 7 sites, this module only
