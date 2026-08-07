# tests.test_spine_rail:_derive
function, tests/test_spine_rail.py:180, 15 lines

```python
def _derive(payload, **overrides)
```

Derive an adversarial row by MUTATING a real captured payload.

This is not the forbidden hand-injection: these rows prove REJECTION, never
delivery. They are necessary because the real capture holds zero malformed
agent_ids and zero falsy session_ids, so the reject branch is unreachable
from unmutated capture alone.

calls stdlib: builtins.dict
reads internal: _ABSENT
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 13 sites, this module only
