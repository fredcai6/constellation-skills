# tests.test_spine_rail:test_session_start_ambiguous_scan_injects_context_but_writes_no_binding
function, tests/test_spine_rail.py:917, 22 lines

```python
def test_session_start_ambiguous_scan_injects_context_but_writes_no_binding(proj)
```

Two real, on-disk, active-leased spines and NO prior binding for the

calling sid -- decide_session_start still injects the advisory context
(first match, same tone as before #261) but decision:no-bind-on-
ambiguous-scan means it must NOT write a binding: the scan is
ambiguous, so guessing which of the two spines this session actually
owns would be exactly the wrong-binding failure class the launch order
is protecting against.

calls internal: make_spine x2, write_spine x2
calls stdlib: builtins.str
reads internal: sr x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
