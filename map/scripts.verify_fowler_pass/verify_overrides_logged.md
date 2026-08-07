# scripts.verify_fowler_pass:verify_overrides_logged
function, scripts/verify_fowler_pass.py:135, 33 lines

```python
def verify_overrides_logged(record: dict) -> None
```

The bounded override rail: an `overridden` verdict (smell present but a

documented repo standard wins, so NOT flagged) needs a logged reason — the
standard that wins AND why. A `flagged` verdict needs a finding.

calls internal: _require x4, _nonempty x3
calls stdlib: builtins.isinstance x2, builtins.str
reads stdlib: builtins.dict x2
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
