# scripts.map_orient:exit_code_for
function, scripts/map_orient.py:849, 11 lines

```python
def exit_code_for(mode: str, discharged: bool) -> int
```

PURE. The frozen exit code for a verdict.

Falsification floor pins the UNRESOLVABLE-ROOT arm and the undischarged
arm (tests/test_mutation_floor.py).

reads internal: EXIT_OK x2, EXIT_DEGRADED_UNDISCHARGED, EXIT_UNRESOLVABLE_ROOT, MODE_RESOLVED, MODE_UNRESOLVABLE_ROOT

referenced by: 7 sites, this module only
