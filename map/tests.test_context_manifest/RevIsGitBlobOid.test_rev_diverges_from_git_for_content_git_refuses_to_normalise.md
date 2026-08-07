# tests.test_context_manifest:RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise
method, tests/test_context_manifest.py:128, 47 lines

```python
def test_rev_diverges_from_git_for_content_git_refuses_to_normalise(self)
```

HOLE: no docstring

calls internal: RevIsGitBlobOid.assertEqual x5, RevIsGitBlobOid._raw_blob_oid x3, RevIsGitBlobOid._git x2, RevIsGitBlobOid.assertNotEqual x2, RevIsGitBlobOid.subTest
calls stdlib: builtins.str x2, pathlib.Path x2, tempfile.TemporaryDirectory
reads internal: cm x3
reads stdlib: tempfile (module)
unresolved: 10 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: none found
