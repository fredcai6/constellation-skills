# tests.test_checklist_engine:_run_at
function, tests/test_checklist_engine.py:114, 11 lines

```python
def _run_at(path, argv)
```

Like `_run_main`, but against an EXISTING file path -- lets a sequence

of CLI calls share persisted state across steps, so a two-step recovery
(e.g. resume, THEN retry the original op) can be run end to end and the
retry's own success asserted, not just that the first step didn't raise.

calls stdlib: io.StringIO x2, builtins.str, contextlib.redirect_stderr, contextlib.redirect_stdout
reads internal: E
reads stdlib: contextlib (module) x2, io (module) x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 55 sites, this module only
