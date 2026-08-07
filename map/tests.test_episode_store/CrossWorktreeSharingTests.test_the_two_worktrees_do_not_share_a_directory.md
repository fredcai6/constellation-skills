# tests.test_episode_store:CrossWorktreeSharingTests.test_the_two_worktrees_do_not_share_a_directory
method, tests/test_episode_store.py:1515, 16 lines

```python
def test_the_two_worktrees_do_not_share_a_directory(self)
```

Falsification guard for the exercise above. If the two worktrees were secretly

the same directory (or a symlink pair), the "retrievable from the second
worktree" result would be trivially true and would prove nothing about git. Write
an uncommitted file in one and confirm the other cannot see it: what crosses is
the COMMIT, not the filesystem.

calls internal: CrossWorktreeSharingTests.git x2, episode_path x2, CrossWorktreeSharingTests.assertEqual, CrossWorktreeSharingTests.assertFalse, CrossWorktreeSharingTests.assertTrue, CrossWorktreeSharingTests.query_in, SeparateProcessMixin.seed_in_separate_process, create_op
calls stdlib: builtins.str x2, json.loads
reads internal: CrossWorktreeSharingTests.origin x2, CrossWorktreeSharingTests.repo_dir x2
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
