# tests.test_gauge_writer:test_local_allowlist_admits_the_real_observed_id_shape
function, tests/test_gauge_writer.py:821, 6 lines

```python
def test_local_allowlist_admits_the_real_observed_id_shape(proj)
```

The guard must not be so tight it rejects the ids the harness actually

sends -- the probe captured `a8f0a946eaaa2fe6c`, `adb52b4ec6c7dbd40` and
the fixture's `af45cec63b2835a40`; `-` and `_` are admitted too.

reads internal: _PARENT_AGENT_ID, gw
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
