# tests.test_episode_negative_control:blob_oid
function, tests/test_episode_negative_control.py:288, 8 lines

```python
def blob_oid(data: bytes) -> str
```

Git blob OID over `data`'s own bytes, computed here.

Deliberately NOT `context_manifest.rev()` — calling the producer's own identity
function to check the producer's own output compares the thing to itself.

calls stdlib: builtins.len, hashlib.sha1
reads stdlib: hashlib (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
