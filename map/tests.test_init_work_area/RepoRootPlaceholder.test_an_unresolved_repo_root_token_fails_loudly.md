# tests.test_init_work_area:RepoRootPlaceholder.test_an_unresolved_repo_root_token_fails_loudly
method, tests/test_init_work_area.py:490, 6 lines

```python
def test_an_unresolved_repo_root_token_fails_loudly(self)
```

The guard owns the token, so a regressed resolver cannot ship it.

calls internal: RepoRootPlaceholder.assertIn, RepoRootPlaceholder.assertRaises, load
calls stdlib: builtins.str
reads stdlib: builtins.SystemExit
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
