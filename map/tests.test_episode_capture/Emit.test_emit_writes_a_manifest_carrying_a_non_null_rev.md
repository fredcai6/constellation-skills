# tests.test_episode_capture:Emit.test_emit_writes_a_manifest_carrying_a_non_null_rev
method, tests/test_episode_capture.py:230, 23 lines

```python
def test_emit_writes_a_manifest_carrying_a_non_null_rev(self)
```

Guards against the all-null manifest: a wrong root produces a structurally

valid file whose every `rev` is null, so the shape alone proves nothing.

calls internal: Emit.assertEqual x2, Emit.assertIsNone, Emit.assertIsNotNone, git_repo, work_area
calls stdlib: pathlib.Path x2, builtins.open, json.loads, tempfile.TemporaryDirectory
reads internal: cm, ec
reads stdlib: json (module), tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
