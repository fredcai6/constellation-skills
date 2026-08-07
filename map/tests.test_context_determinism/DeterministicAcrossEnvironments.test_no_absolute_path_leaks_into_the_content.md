# tests.test_context_determinism:DeterministicAcrossEnvironments.test_no_absolute_path_leaks_into_the_content
method, tests/test_context_determinism.py:283, 8 lines

```python
def test_no_absolute_path_leaks_into_the_content(self)
```

HOLE: no docstring

calls internal: DeterministicAcrossEnvironments.assertNotIn x2, DeterministicAcrossEnvironments.subTest
calls stdlib: pathlib.Path
reads internal: DeterministicAcrossEnvironments.results
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
