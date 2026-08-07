# scripts.verify_spec_confirmed:_confirmation_section
function, scripts/verify_spec_confirmed.py:46, 9 lines

```python
def _confirmation_section(text: str) -> str | None
```

Return the ``## Confirmation`` section body, or None if absent.

calls stdlib: builtins.len
reads internal: _ANY_H2_RE, _CONFIRMATION_HEADING_RE
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
