# tests.test_map_orient:degraded_receipt
function, tests/test_map_orient.py:324, 20 lines

```python
def degraded_receipt(root: Path, work_id: str, **overrides) -> Path
```

HOLE: no docstring

calls internal: write
calls stdlib: json.dumps
reads internal: COMPLETE_RECORD
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 16 sites, this module only
