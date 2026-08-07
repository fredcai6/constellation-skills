# tests.test_diagnose:probe_disconnect
function, tests/test_diagnose.py:70, 10 lines

```python
def probe_disconnect() -> str
```

The oracle: probe the map's purity claim against actual behavior. Returns

the observed disagreement (empty string means map and execution agree).

calls internal: seeded_touch
reads internal: _STATE x2, MAP_CLAIM_PURE

referenced by: 1 sites, this module only
