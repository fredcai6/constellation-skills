# tests.test_checklist_engine:SkipReasonAdvisoryTests._write_skip
method, tests/test_checklist_engine.py:3438, 5 lines

```python
def _write_skip(self, d, reason, observed_at, candidate_count=None)
```

HOLE: no docstring

calls stdlib: json.dumps, pathlib.Path
reads internal: E
reads stdlib: json (module)
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
