# tests.test_install_constellation:_find_py_free_interpreter_dir
function, tests/test_install_constellation.py:951, 25 lines

```python
def _find_py_free_interpreter_dir(installer)
```

Find a real PATH entry that carries a genuine python3/python executable

but NOT a `py` launcher -- used to genuinely shadow PATH so the real probe
cannot resolve `py`, rather than asserting a hand-set fixture value (issue
#228's active lesson `verify-harness-field-and-drive-real-writer`). Returns
None if the current host has no such entry (test skips rather than fakes it).

calls stdlib: os.environ.get, pathlib.Path
reads stdlib: os (module) x2, builtins.OSError, os.environ, os.pathsep
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
