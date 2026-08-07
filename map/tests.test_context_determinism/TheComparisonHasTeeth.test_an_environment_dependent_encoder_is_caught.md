# tests.test_context_determinism:TheComparisonHasTeeth.test_an_environment_dependent_encoder_is_caught
method, tests/test_context_determinism.py:374, 8 lines

```python
def test_an_environment_dependent_encoder_is_caught(self)
```

HOLE: no docstring

calls internal: TheComparisonHasTeeth.assertEqual, TheComparisonHasTeeth.assertNotEqual, TheComparisonHasTeeth.content_bytes_from_two_environments
calls stdlib: json.loads x2
reads stdlib: json (module) x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
