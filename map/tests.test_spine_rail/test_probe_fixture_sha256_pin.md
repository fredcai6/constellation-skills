# tests.test_spine_rail:test_probe_fixture_sha256_pin
function, tests/test_spine_rail.py:129, 12 lines

```python
def test_probe_fixture_sha256_pin()
```

Pin the fixture's content. If someone hand-edits the capture -- adding a

convenient agent_id, say -- this fails first and loudly, instead of every
downstream test quietly proving something about invented input.

calls stdlib: builtins.len x2, builtins.print, hashlib.sha256
reads internal: _PROBE_FIXTURE x3, _PROBE_FIXTURE_SHA256 x2, _PROBE_FIXTURE_NORMALIZED_BYTES
reads stdlib: hashlib (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
