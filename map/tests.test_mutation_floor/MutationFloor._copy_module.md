# tests.test_mutation_floor:MutationFloor._copy_module
method, tests/test_mutation_floor.py:274, 9 lines

```python
def _copy_module(self, source: str) -> Path
```

HOLE: no docstring

calls internal: MutationFloor.addCleanup
calls stdlib: builtins.open, pathlib.Path, tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
