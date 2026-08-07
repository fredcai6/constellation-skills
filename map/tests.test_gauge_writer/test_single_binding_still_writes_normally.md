# tests.test_gauge_writer:test_single_binding_still_writes_normally
function, tests/test_gauge_writer.py:341, 14 lines

```python
def test_single_binding_still_writes_normally(proj)
```

No-regression check: exactly ONE bound spine must still write the real

record -- skip-on-multiple must not become skip-on-any.

calls internal: _bind, _hook_data
calls stdlib: json.loads
calls third-party: pytest.approx
reads internal: EXPECTED_FILL, EXPECTED_MODEL, _FIXTURE, gw
reads stdlib: json (module)
reads third-party: pytest (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
