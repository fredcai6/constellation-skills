# scripts.verify_agent_feedback:_negative_errors
function, scripts/verify_agent_feedback.py:107, 32 lines

```python
def _negative_errors(root: Path, work_id: str, phase: str) -> list[str]
```

The mode-independent negative checks: nothing durable leaked into the work

area or the archive package, plus the archive-phase structural checks.

calls internal: _current_run_archive_dirs
reads stdlib: builtins.list, builtins.str
unresolved: 11 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
