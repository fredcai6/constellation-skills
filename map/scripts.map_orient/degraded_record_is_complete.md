# scripts.map_orient:degraded_record_is_complete
function, scripts/map_orient.py:536, 13 lines

```python
def degraded_record_is_complete(receipt: dict) -> bool
```

PURE. A DEGRADED record discharges ONLY with all three declarations.

Falsification floor pins this `all` (tests/test_mutation_floor.py): under
`any`, a record carrying one field and omitting two would pass, which is
exactly the silent-degradation this module exists to refuse.

calls internal: escalation_declared, substitutes_declared, unmapped_declared
calls stdlib: builtins.all

referenced by: 6 sites, this module only
