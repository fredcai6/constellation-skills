# scripts.verify_spec_confirmed:parse_confirmation
function, scripts/verify_spec_confirmed.py:57, 18 lines

```python
def parse_confirmation(text: str) -> dict[str, str | None]
```

Pull Status / Confirmed-by / Date out of the Confirmation section.

Any field not found is None (missing, not merely blank).

- [_find](parse_confirmation._find.md) method: HOLE: no docstring

calls internal: _confirmation_section
reads internal: _CONFIRMED_BY_RE, _DATE_RE, _STATUS_RE
reads stdlib: builtins.str, re (module), re.Pattern

referenced by: 1 sites, this module only
