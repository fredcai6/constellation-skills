# tests.test_context_manifest:AdversarialDeclarations.setUp
method, tests/test_context_manifest.py:637, 13 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: AdversarialDeclarations.addCleanup
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: AdversarialDeclarations.tmp x2, FIXTURES
reads stdlib: tempfile (module)
writes internal: AdversarialDeclarations.roots, AdversarialDeclarations.tmp
unresolved: 5 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
