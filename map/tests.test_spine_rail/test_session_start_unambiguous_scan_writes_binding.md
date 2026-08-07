# tests.test_spine_rail:test_session_start_unambiguous_scan_writes_binding
function, tests/test_spine_rail.py:941, 27 lines

```python
def test_session_start_unambiguous_scan_writes_binding(proj)
```

Exactly ONE real, on-disk, active-leased spine and no prior binding

for the calling sid -- decide_session_start injects the advisory
context AND writes a real binding entry (g1's per-spine-path writer
shape) so a resumed/compacted session that never itself ran `claim`
still resolves through gauge_writer_hook for the rest of its life.

calls internal: make_spine, write_spine
calls stdlib: builtins.str x2
reads internal: sr x3
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
