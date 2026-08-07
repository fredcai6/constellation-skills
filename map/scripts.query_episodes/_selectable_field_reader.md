# scripts.query_episodes:_selectable_field_reader
function, scripts/query_episodes.py:255, 14 lines

```python
def _selectable_field_reader(field: str)
```

The one place a field name is checked and the one place the refusal is worded.

Both `field_values()` (which reads a field off one episode) and `select_episodes()`
(which validates the caller's field before scanning anything) have to reject an
unknown name, and they used to carry the same sentence twice — two copies of a
contract that must not drift, since "your field name is wrong" has to read identically
whether the caller arrived through the CLI or through the API.

calls internal: QueryError
reads internal: SELECTABLE_FIELDS, _FIELD_READERS
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
