# tests.test_episode_capture:Emit.test_emit_without_a_checklist_directory_writes_nothing_at_all
method, tests/test_episode_capture.py:299, 6 lines

```python
def test_emit_without_a_checklist_directory_writes_nothing_at_all(self)
```

No spine location means no work area; inventing one would write the record

outside the run it belongs to. Absence here is the correct answer, and it is
what keeps in-process engine calls from scattering manifests.

calls internal: Emit.assertIsNone, checklist
reads internal: ec
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
