# scripts.verify_agent_feedback:_boilerplate_errors
function, scripts/verify_agent_feedback.py:42, 28 lines

```python
def _boilerplate_errors(entry: str, work_id: str) -> list[str]
```

Reject content-free entries: every signal bullet is a bare 'none'.

calls stdlib: builtins.all
reads internal: _SIGNAL_SECTIONS x2, _BARE_NONE_RE
reads stdlib: builtins.list, builtins.str
unresolved: 12 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
