# tests.test_episode_negative_control:_create_op
function, tests/test_episode_negative_control.py:1001, 26 lines

```python
def _create_op(run: str, role: str, step: str, artifact_refs: list[str]) -> dict
```

A create op. `id` is deliberately absent — the writer ASSIGNS it (EPISODE_STORE

section 2, zero agent effort) and `_validate_create` refuses a supplied one.

referenced by: 5 sites, this module only
