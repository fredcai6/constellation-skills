# tests.test_context_manifest:AdversarialDeclarations.test_untracked_vs_absent_does_not_change_the_content_shape
method, tests/test_context_manifest.py:699, 17 lines

```python
def test_untracked_vs_absent_does_not_change_the_content_shape(self)
```

HOLE: no docstring

calls internal: AdversarialDeclarations.assertEqual x2, AdversarialDeclarations.build x2, AdversarialDeclarations.assertIsNone, AdversarialDeclarations.assertIsNotNone
calls stdlib: pathlib.Path
reads internal: AdversarialDeclarations.tmp, FIXTURES
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
