# tests.test_fowler_pass:_with
function, tests/test_fowler_pass.py:69, 3 lines

```python
def _with(name: str, **overrides) -> list
```

The full baseline with one smell's entry overridden by `overrides`.

calls internal: _smell x2
reads internal: REQUIRED_SMELLS

referenced by: 9 sites, this module only
