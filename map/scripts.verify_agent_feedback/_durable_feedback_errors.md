# scripts.verify_agent_feedback:_durable_feedback_errors
function, scripts/verify_agent_feedback.py:83, 22 lines

```python
def _durable_feedback_errors(durable: Path, work_id: str) -> list[str]
```

The durable-log positive check: the shared main-checkout AGENT_FEEDBACK.md.

calls internal: _boilerplate_errors, _entry_block
reads stdlib: builtins.list, builtins.str
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
