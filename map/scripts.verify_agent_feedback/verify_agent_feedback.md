# scripts.verify_agent_feedback:verify_agent_feedback
function, scripts/verify_agent_feedback.py:200, 23 lines

```python
def verify_agent_feedback(root: Path, work_id: str, phase: str, durable: Path | None = None) -> None
```

HOLE: no docstring

calls internal: FeedbackVerificationError, _durable_feedback_errors, _negative_errors, _staged_feedback_errors
writes internal: verify_agent_feedback.durable
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
