# tests.test_episode_store:RelocatedSilentOmissionTests.test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames
method, tests/test_episode_store.py:2349, 31 lines

```python
def test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames(self)
```

The mechanism behind trap 4, asserted directly.

"Is this file an episode?" is DERIVABLE from the id grammar the store already
enforces at create time, so it is derived. A hand-maintained enumeration would
have to be edited whenever anyone adds a file and is silent in one direction (a
real stray accepted) and store-bricking in the other.

calls internal: RelocatedSilentOmissionTests.assertEqual, RelocatedSilentOmissionTests.assertIn, RelocatedSilentOmissionTests.assertIsNone, RelocatedSilentOmissionTests.assertRaises
calls stdlib: pathlib.Path x2, builtins.frozenset, builtins.len, builtins.str
reads internal: RelocatedSilentOmissionTests.root x3, RelocatedSilentOmissionTests.m, RelocatedSilentOmissionTests.q
unresolved: 5 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 2 writes (dispatch-unknown-base)

referenced by: none found
