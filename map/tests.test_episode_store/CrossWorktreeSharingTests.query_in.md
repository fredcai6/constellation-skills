# tests.test_episode_store:CrossWorktreeSharingTests.query_in
method, tests/test_episode_store.py:1367, 10 lines

```python
def query_in(self, worktree, *args, expect_rc=0)
```

Run retrieval in a freshly booted interpreter whose CWD is that worktree,

against that worktree's OWN episodes/ directory.

calls internal: CrossWorktreeSharingTests.assertEqual, SeparateProcessMixin.run_in_separate_process
calls stdlib: builtins.str, pathlib.Path
reads internal: QUERY_SCRIPT

referenced by: 5 sites, this module only
