# tests.test_agent_work_root:_write_lease
function, tests/test_agent_work_root.py:55, 17 lines

```python
def _write_lease(main: Path, epic: str, *, status: str, claimed_by: str) -> Path
```

Simulate an epic lease: `<main>/.agent-work/<epic>/spine.json` carrying an

`engine_session` dict with the given status/claimed_by.

calls stdlib: json.dumps
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
