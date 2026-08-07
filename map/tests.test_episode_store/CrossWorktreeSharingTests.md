# tests.test_episode_store:CrossWorktreeSharingTests
class, tests/test_episode_store.py:1316, 215 lines

```python
@unittest.skipIf(shutil.which('git') is None, 'git is required for the cross-worktree exercise')
class CrossWorktreeSharingTests(QueryTestCase, SeparateProcessMixin)
```

C3 — cross-worktree sharing, exercised THROUGH GIT (EPISODE_STORE.md section 9).

This is the mechanism that actually provides cross-worktree durability now that the
store is a tracked path, so it is exercised the way it really works: a real
`git worktree add` against a real repository, a real commit in one worktree, the
ordinary merge path, and retrieval from a SECOND worktree. A test that simulated a
worktree with a directory name would pass while proving nothing — a store that
silos per worktree passes a same-directory test too, and that is exactly the
silently-wrong-but-green shape this exercise guards against.

The reader worktree is created BEFORE the episode exists and queried BEFORE the
merge, so the "absent, then present" transition is observed rather than assumed.

- [setUp](CrossWorktreeSharingTests.setUp.md) method: HOLE: no docstring
- [cleanup_repo](CrossWorktreeSharingTests.cleanup_repo.md) method: HOLE: no docstring
- [git](CrossWorktreeSharingTests.git.md) method: HOLE: no docstring
- [query_in](CrossWorktreeSharingTests.query_in.md) method: Run retrieval in a freshly booted interpreter whose CWD is that worktree,
- [test_episode_committed_in_one_worktree_is_retrievable_from_another](CrossWorktreeSharingTests.test_episode_committed_in_one_worktree_is_retrievable_from_another.md) method: HOLE: no docstring
- [test_working_tree_bytes_are_not_the_cross_worktree_identity](CrossWorktreeSharingTests.test_working_tree_bytes_are_not_the_cross_worktree_identity.md) method: A finding, pinned as a test rather than left as prose.
- [test_the_two_worktrees_do_not_share_a_directory](CrossWorktreeSharingTests.test_the_two_worktrees_do_not_share_a_directory.md) method: Falsification guard for the exercise above. If the two worktrees were secretly

referenced by: none found
