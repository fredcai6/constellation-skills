# scripts.verify_agent_feedback:_staged_feedback_errors
function, scripts/verify_agent_feedback.py:141, 57 lines

```python
def _staged_feedback_errors(root: Path, work_id: str) -> list[str]
```

The fencing-aware positive check: a worktree-local staged trio + citation.

A delegated commander who is fenced off the main checkout's durable
`.agent-work/` may instead stage the trio under
`<root>/.agent-work/staged-feedback/<work_id>/`. Any missing member of the
trio (including the FENCE.md citation itself) is an error whose message
makes clear that learning cannot be silently dropped.

calls internal: _boilerplate_errors, _entry_block
calls stdlib: json.loads
reads stdlib: builtins.ValueError, builtins.list, builtins.str, json (module)
unresolved: 17 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
