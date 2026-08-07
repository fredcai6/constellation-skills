# tests.test_checklist_engine:_run_main
function, tests/test_checklist_engine.py:98, 14 lines

```python
def _run_main(cl, argv)
```

Run E.main() against `cl` (written to a tmp file) and capture

(exit_code, stdout, stderr) -- the real CLI boundary, not a direct verb
call, so this exercises dispatch()/main()'s COMPOSITION (rail position,
recovery text) rather than the pure verb functions alone.

calls stdlib: io.StringIO x2, builtins.str, contextlib.redirect_stderr, contextlib.redirect_stdout, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: contextlib (module) x2, io (module) x2, tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 26 sites, this module only
