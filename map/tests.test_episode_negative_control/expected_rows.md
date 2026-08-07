# tests.test_episode_negative_control:expected_rows
function, tests/test_episode_negative_control.py:319, 17 lines

```python
def expected_rows(repo: Path) -> list[dict]
```

What the delivered-context rows MUST say, computed HERE from the files' bytes.

`blob_oid`, never `context_manifest.rev()` and never the manifest itself — the same
independence rule the field expectations follow. `rev: null` is the correct reading
for a declared file that is not there, and it is produced here the same way, so the
absent case is expected rather than special-cased.

calls internal: blob_oid
reads internal: DECLARED_CONTEXT
reads stdlib: builtins.dict, builtins.list
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
