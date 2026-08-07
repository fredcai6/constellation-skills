# tests.test_gauge_writer:test_atomic_write_uses_tmp_then_replace
function, tests/test_gauge_writer.py:1326, 8 lines

```python
def test_atomic_write_uses_tmp_then_replace(proj)
```

Direct check of the write primitive: the target is only ever touched

by os.replace from a distinct tmp file, never opened for direct writing.

calls stdlib: json.loads
reads internal: gw
reads stdlib: json (module)
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
