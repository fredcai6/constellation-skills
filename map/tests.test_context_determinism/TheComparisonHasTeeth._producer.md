# tests.test_context_determinism:TheComparisonHasTeeth._producer
method, tests/test_context_determinism.py:332, 10 lines

```python
def _producer(self, tmp, poison)
```

A copy of the real producer under `tmp`, optionally poisoned.

calls stdlib: builtins.open, pathlib.Path, shutil.copyfile
reads internal: ROOT x2, POISONS
reads stdlib: shutil (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
