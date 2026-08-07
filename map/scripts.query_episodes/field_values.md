# scripts.query_episodes:field_values
function, scripts/query_episodes.py:271, 10 lines

```python
def field_values(episode, field: str) -> list[str]
```

Every value an episode carries for `field`, as strings — one element for a

scalar, N for a repeated field like artifact-ref, zero if the episode carries none.

Counted fields are compared as strings (refusals "0", not 0) so one comparison rule
covers every field and a CLI --value never needs a per-field type. An unrecognized
field name RAISES: returning [] instead would make a typo indistinguishable from a
genuine no-match, which is the silent-omission failure mode wearing a different
hat.

calls internal: _selectable_field_reader

referenced by: 2 sites, this module only
