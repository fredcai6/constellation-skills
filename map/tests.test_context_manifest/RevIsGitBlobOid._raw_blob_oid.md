# tests.test_context_manifest:RevIsGitBlobOid._raw_blob_oid
method, tests/test_context_manifest.py:122, 5 lines

```python
def _raw_blob_oid(self, data)
```

Git's blob OID of exactly these bytes, with no normalisation. The second

oracle: it lets the divergence test say *why* the two disagree, not merely
that they do.

calls stdlib: builtins.len, hashlib.sha1
reads stdlib: hashlib (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
