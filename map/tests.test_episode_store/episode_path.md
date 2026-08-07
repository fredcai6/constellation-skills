# tests.test_episode_store:episode_path
function, tests/test_episode_store.py:48, 9 lines

```python
def episode_path(root, episode_id, retired=False)
```

The on-disk path of an episode under the layout ratified at g4: `active/` for the

ordinary-search set, `retired/` for the archive.

Tests name the directories literally on purpose — the shipped primitives may not
(close criterion C2 forbids any literal `active/`/`retired/` outside the seam block),
so a test that also went through the seam would be asserting the implementation
against itself. Here the literal IS the assertion.

calls stdlib: pathlib.Path

referenced by: 40 sites, this module only
