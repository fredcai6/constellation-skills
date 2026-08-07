# scripts.verify_state_note:validate
function, scripts/verify_state_note.py:57, 10 lines

```python
def validate(text: str) -> list[str]
```

Return a list of problems; empty means the note is well-formed.

calls internal: _is_placeholder, parse_fields
reads internal: REQUIRED_FIELDS
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
