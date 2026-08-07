# tests.test_context_determinism:TheComparisonHasTeeth.content_bytes_from_two_environments
method, tests/test_context_determinism.py:343, 25 lines

```python
def content_bytes_from_two_environments(self, poison=None)
```

HOLE: no docstring

calls internal: TheComparisonHasTeeth._producer, TheComparisonHasTeeth.assertEqual
calls stdlib: builtins.str x6, pathlib.Path x2, builtins.dict, builtins.enumerate, shutil.rmtree, subprocess.run, tempfile.mkdtemp
reads internal: CHILD, DeterministicAcrossEnvironments, DeterministicAcrossEnvironments.ENVIRONMENTS, ROOT
reads stdlib: os (module), os.environ, shutil (module), subprocess (module), sys (module), sys.executable, tempfile (module)
unresolved: 6 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
