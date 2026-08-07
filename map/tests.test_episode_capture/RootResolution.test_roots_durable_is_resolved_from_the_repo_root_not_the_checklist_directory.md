# tests.test_episode_capture:RootResolution.test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory
method, tests/test_episode_capture.py:195, 19 lines

```python
def test_roots_durable_is_resolved_from_the_repo_root_not_the_checklist_directory(self)
```

`durable_root(start)` redirects to the main checkout ONLY for a linked

worktree with no active Admiral epic lease. On every other path — plain
checkout, active lease, no git — it returns `start` UNCHANGED. So handing it
the spine's own directory silently makes that directory the durable root, and
a `.agent-work/…`-relative durable declaration nests under it. This is the
argument, not the helper, and no assertion about which function was called
can see it.

calls internal: norm x4, RootResolution.assertEqual x2, git_repo
calls stdlib: pathlib.Path x2, tempfile.TemporaryDirectory
reads internal: cm, ec
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
