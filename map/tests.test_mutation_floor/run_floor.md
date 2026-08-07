# tests.test_mutation_floor:run_floor
function, tests/test_mutation_floor.py:241, 19 lines

```python
def run_floor(module_path: Path) -> subprocess.CompletedProcess
```

Run the whole floor with the module under test pointed at `module_path`.

calls stdlib: builtins.str x3, builtins.dict, subprocess.run
reads internal: FLOOR, ROOT
reads stdlib: os (module), os.environ, subprocess (module), sys (module), sys.executable
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
