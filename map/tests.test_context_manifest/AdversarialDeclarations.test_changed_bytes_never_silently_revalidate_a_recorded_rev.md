# tests.test_context_manifest:AdversarialDeclarations.test_changed_bytes_never_silently_revalidate_a_recorded_rev
method, tests/test_context_manifest.py:692, 6 lines

```python
def test_changed_bytes_never_silently_revalidate_a_recorded_rev(self)
```

HOLE: no docstring

calls internal: AdversarialDeclarations.build x2, AdversarialDeclarations.assertNotEqual
calls stdlib: pathlib.Path
reads internal: cm x2, AdversarialDeclarations.tmp, FIXTURES
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
