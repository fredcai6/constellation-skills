# tests.test_episode_store:SeamContainmentTests.test_retrieval_reaches_the_layout_only_through_the_seams
method, tests/test_episode_store.py:2690, 47 lines

```python
def test_retrieval_reaches_the_layout_only_through_the_seams(self)
```

The direct proof that the binding is contained: move the layout by replacing

the SEAMS ONLY — no source edit, no adapter switch — and retrieval follows it.

This is the successor to the pre-g4 test that flipped `_LAYOUT_ADAPTER` between
two candidate adapters. That switch is gone with the decision it existed for, but
the property it was proving is not: if any retrieval primitive had inlined the
real directory names, substituting the seams below would leave it reading the
wrong place and the assertions would fail.

calls internal: SeamContainmentTests.assertEqual x5, create_op
calls stdlib: builtins.str x4, pathlib.Path x3, builtins.sorted, json.dumps, shutil.move
reads internal: SeamContainmentTests.m x6, SeamContainmentTests.q x5, SeamContainmentTests.tmp x3
reads stdlib: json (module), shutil (module)
unresolved: 12 calls (dispatch-unknown-base), 2 calls (dynamic), 5 reads (dispatch-unknown-base), 3 reads (unbound-name), 3 writes (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
