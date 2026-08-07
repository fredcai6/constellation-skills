# tests.test_context_determinism:DeterministicAcrossEnvironments.setUp
method, tests/test_context_determinism.py:188, 29 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: DeterministicAcrossEnvironments.assertEqual
calls stdlib: builtins.str x5, json.loads x2, builtins.dict, builtins.zip, pathlib.Path, subprocess.run
reads internal: CHILD, DeterministicAcrossEnvironments.ENVIRONMENTS, DeterministicAcrossEnvironments._tmp, DeterministicAcrossEnvironments._worktrees, DeterministicAcrossEnvironments.results
reads stdlib: json (module) x2, os (module), os.environ, subprocess (module), sys (module), sys.executable
writes internal: DeterministicAcrossEnvironments.results
unresolved: 7 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
