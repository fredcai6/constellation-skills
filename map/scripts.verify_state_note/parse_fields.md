# scripts.verify_state_note:parse_fields
function, scripts/verify_state_note.py:39, 8 lines

```python
def parse_fields(text: str) -> dict[str, str]
```

Pull `- **key:** value` lines into a lowercased key -> value map.

reads internal: FIELD_RE
reads stdlib: builtins.str x2, builtins.dict
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
