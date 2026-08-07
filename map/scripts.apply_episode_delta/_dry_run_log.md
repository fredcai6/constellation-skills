# scripts.apply_episode_delta:_dry_run_log
function, scripts/apply_episode_delta.py:1286, 20 lines

```python
def _dry_run_log(root: Path, delta: dict) -> list[str]
```

Validate and compute the write-plan, but never call commit().

Runs the same store pre-flight as apply_delta() so a dry run answers about the store
that is really there — but never creates the layout, because a dry run writes
nothing at all, including a directory.

calls internal: _Transaction, _Transaction.known_ids, _apply_amend_assertion, _apply_create, _apply_retire, validate_delta
reads stdlib: builtins.list, builtins.str
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
