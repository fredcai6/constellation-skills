# tests.test_gauge_writer:test_no_default_window_constant_remains
function, tests/test_gauge_writer.py:1253, 4 lines

```python
def test_no_default_window_constant_remains(proj)
```

The 200k default IS the bug — guard against a well-meaning reintroduction

of a fallback on the reading path.

calls stdlib: builtins.hasattr
reads internal: gw

referenced by: none found
