# tests.test_context_manifest:RevIsGitBlobOid.test_rev_crlf_twin_written_to_disk_matches_git_hash_object
method, tests/test_context_manifest.py:105, 16 lines

```python
def test_rev_crlf_twin_written_to_disk_matches_git_hash_object(self)
```

HOLE: no docstring

calls internal: RevIsGitBlobOid.assertEqual x3
calls stdlib: pathlib.Path x2, builtins.str, subprocess.run, tempfile.TemporaryDirectory
reads internal: cm x2, ROOT
reads stdlib: subprocess (module), tempfile (module)
unresolved: 7 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
