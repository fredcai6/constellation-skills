# tests.test_episode_store:SeamContainmentTests.test_the_writer_names_the_directories_only_inside_the_seam_block
method, tests/test_episode_store.py:2738, 42 lines

```python
def test_the_writer_names_the_directories_only_inside_the_seam_block(self)
```

C2's other half. query_episodes.py may not name the directories at all; the

writer must — it is where the seams live — but only THERE. A path, glob, or move
that escaped into an op handler or the transaction would re-scatter the layout,
which is exactly what the seam table exists to prevent.

The record-grammar uses of the same two words are excluded by EXACT LINE, not by
a loosened pattern: `lifecycle-standing: active` and an episode's default `status`
are data that happen to share a vocabulary with the layout, and letting this check
drift into accepting them by shape would let a real inlined path through with
them.

calls internal: SeamContainmentTests.assertIn, SeamContainmentTests.assertNotIn
calls stdlib: builtins.any, re.sub
reads internal: WRITER_SCRIPT
reads stdlib: re (module)
unresolved: 8 calls (dispatch-unknown-base)

referenced by: none found
