# tests.test_context_determinism:DeterministicAcrossEnvironments.test_content_is_byte_identical_excluding_exactly_the_run_subtree
method, tests/test_context_determinism.py:241, 18 lines

```python
def test_content_is_byte_identical_excluding_exactly_the_run_subtree(self)
```

HOLE: no docstring

calls internal: DeterministicAcrossEnvironments.assertEqual x2, DeterministicAcrossEnvironments.assertNotEqual, DeterministicAcrossEnvironments.assertNotIn, DeterministicAcrossEnvironments.subTest
calls stdlib: builtins.set x2
reads internal: DeterministicAcrossEnvironments.results x5, cm x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
