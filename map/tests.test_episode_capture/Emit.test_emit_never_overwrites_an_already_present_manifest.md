# tests.test_episode_capture:Emit.test_emit_never_overwrites_an_already_present_manifest
method, tests/test_episode_capture.py:264, 17 lines

```python
def test_emit_never_overwrites_an_already_present_manifest(self)
```

A per-step *delivery snapshot*. If a later call rewrote it, the record

would silently become "whatever was available at the last call".

calls internal: Emit.assertEqual x3, norm x2, git_repo, work_area
calls stdlib: pathlib.Path x5, json.loads, tempfile.TemporaryDirectory
reads internal: ec x2
reads stdlib: json (module), tempfile (module)
unresolved: 7 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
