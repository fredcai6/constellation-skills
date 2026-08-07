# tests.test_worktree_precondition_wiring:_run_coverage_script
function, tests/test_worktree_precondition_wiring.py:49, 6 lines

```python
def _run_coverage_script(root: Path) -> subprocess.CompletedProcess
```

HOLE: no docstring

calls stdlib: builtins.str x2, subprocess.run
reads internal: COVERAGE_SCRIPT
reads stdlib: subprocess (module), sys (module), sys.executable

referenced by: 2 sites, this module only
