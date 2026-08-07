# tests.test_diagnose:seeded_touch
function, tests/test_diagnose.py:64, 4 lines

```python
def seeded_touch(x)
```

Execution drifted from the map: the map says pure, this mutates _STATE.

reads internal: _STATE
writes internal: _STATE[]
unresolved: 1 reads (non-name-expr)

referenced by: 1 sites, this module only
