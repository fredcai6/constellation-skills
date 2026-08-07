# tests.test_context_determinism:DeterministicAcrossEnvironments.setUpClass
class method, tests/test_context_determinism.py:148, 23 lines

```python
def setUpClass(cls)
```

HOLE: no docstring

calls internal: DeterministicAcrossEnvironments._cleanup
calls stdlib: shutil.copyfile x2, unittest.SkipTest x2, builtins.len, builtins.range, builtins.str, pathlib.Path, shutil.which, subprocess.run, tempfile.mkdtemp
reads internal: ROOT x3, DeterministicAcrossEnvironments.ENVIRONMENTS, DeterministicAcrossEnvironments._tmp, DeterministicAcrossEnvironments._worktrees, INSTALL_SHIM, OVERLAY
reads stdlib: shutil (module) x3, unittest (module) x2, builtins.Exception, subprocess (module), tempfile (module)
writes internal: DeterministicAcrossEnvironments._tmp, DeterministicAcrossEnvironments._worktrees
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
