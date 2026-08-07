# tests.test_episode_store:CrossWorktreeSharingTests.test_working_tree_bytes_are_not_the_cross_worktree_identity
method, tests/test_episode_store.py:1459, 55 lines

```python
def test_working_tree_bytes_are_not_the_cross_worktree_identity(self)
```

A finding, pinned as a test rather than left as prose.

On a machine with core.autocrlf=true (the Git-for-Windows default, and the
setting on this one), git converts line endings on CHECKOUT. The writer emits
LF-only bytes; a second worktree that materializes the same commit gets CRLF.
So the episode's raw working-tree bytes are NOT stable across worktrees, even
though the episode is.

This does not weaken C3 — retrieval crosses the boundary intact either way,
because the record, not the byte string, is what the store promises. It does
mean anything downstream that wants a stable content address for an episode
must use git's blob hash (computed on the normalized index content) and not a
hash of the file it finds in its own worktree. That is exactly what
EPISODE_STORE.md section 8's `<ref>@<revision>` pinning already prescribes, so
the contract is intact — but a future consolidation/dedup pass (#308) that
compares episodes by reading and hashing working-tree bytes would be silently
wrong on Windows, which is why this is asserted here rather than assumed.

calls internal: CrossWorktreeSharingTests.git x7, CrossWorktreeSharingTests.assertEqual x2, episode_path x2, CrossWorktreeSharingTests.assertIn, CrossWorktreeSharingTests.assertNotEqual, CrossWorktreeSharingTests.assertNotIn, SeparateProcessMixin.seed_in_separate_process, create_op
calls stdlib: builtins.str x2
reads internal: CrossWorktreeSharingTests.q x4, CrossWorktreeSharingTests.origin x3, CrossWorktreeSharingTests.repo_dir x2
unresolved: 8 calls (dispatch-unknown-base)

referenced by: none found
