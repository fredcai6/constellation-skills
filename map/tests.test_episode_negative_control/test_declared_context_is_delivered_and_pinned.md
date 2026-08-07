# tests.test_episode_negative_control:test_declared_context_is_delivered_and_pinned
function, tests/test_episode_negative_control.py:835, 25 lines

```python
def test_declared_context_is_delivered_and_pinned(control)
```

The delivered-context half of the manifest, EXERCISED and compared per row.

`context-manifest-ref` is a byte-pin over the manifest's own bytes, so it stays
correct however the rows inside come out — which is right, and is also why it can
never be the thing that tells you the rows are wrong. This is what covers the rows:
each declared entry must come back in declaration order, under the root token it was
declared with, carrying a `rev` equal to a blob OID this harness computed from the
file's own bytes.

calls internal: _git, compare_manifest_rows, expected_rows
calls stdlib: builtins.all, builtins.str, builtins.zip
reads internal: DECLARED_CONTEXT
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
