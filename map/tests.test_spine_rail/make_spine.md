# tests.test_spine_rail:make_spine
function, tests/test_spine_rail.py:32, 26 lines

```python
def make_spine(items_status, lease_status='active', session_id='eng-1', claimed_by='commander', imperatives=None)
```

Build a minimal spine dict.

items_status: list of (id, status) in item order.

writes internal: make_spine.imperatives
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 39 sites, this module only
