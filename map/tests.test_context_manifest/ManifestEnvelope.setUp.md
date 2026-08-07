# tests.test_context_manifest:ManifestEnvelope.setUp
method, tests/test_context_manifest.py:247, 10 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: ManifestEnvelope.addCleanup
calls stdlib: pathlib.Path x2, tempfile.TemporaryDirectory
reads internal: ManifestEnvelope.repo x4, ManifestEnvelope.skill x3, ManifestEnvelope.tmp x3
reads stdlib: tempfile (module)
writes internal: ManifestEnvelope.repo, ManifestEnvelope.roots, ManifestEnvelope.skill, ManifestEnvelope.tmp
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
