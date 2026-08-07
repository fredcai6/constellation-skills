# tests.test_episode_fields:ProjectFieldTests.test_non_repository_refuses_rather_than_guessing
method, tests/test_episode_fields.py:142, 7 lines

```python
def test_non_repository_refuses_rather_than_guessing(self)
```

Refuse, never fabricate. A worktree-derived (or cwd-derived) fallback would

silently poison the one join meant to survive worktree deletion, and a wrong
mechanical fact is worse than an absent one.

calls internal: ProjectFieldTests.assertIsNone
calls stdlib: pathlib.Path
reads internal: ProjectFieldTests.tmp, ec
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
