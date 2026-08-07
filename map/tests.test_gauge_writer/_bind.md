# tests.test_gauge_writer:_bind
function, tests/test_gauge_writer.py:53, 15 lines

```python
def _bind(proj, session_id, spine_path)
```

Write a NEW-shape (#202 nested) binding entry for `session_id`, keyed

by `spine_path` -- merges onto any existing entries for this session_id
rather than clobbering them, so two calls under the same session_id bind
two distinct spines (needed for the fan-out tests below).

calls stdlib: builtins.str x3, builtins.dict
reads internal: sr x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 35 sites, this module only
